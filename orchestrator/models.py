"""Model Router: Scheduler -> Router -> Worker. Per-task model decisions.

- Catalog DISCOVERED live from `opencode models --verbose` (never hardcoded).
- Quotas/limits USER-CONFIGURED in models.json (no quota API exists).
- Limit-hits RUNTIME-DETECTED from worker stderr patterns -> cooldown.
- Unknown models are fail-closed: never selected unless explicitly listed.
"""
from __future__ import annotations
import json
import re
import subprocess
import threading
import time

LIMIT_PATTERNS = [r"429", r"rate.?limit", r"\bquota\b", r"limit.?exceed",
                  r"payment", r"billing", r"model.?not.?found",
                  r"\bunavailable\b"]
_LIMIT_RE = re.compile("|".join(f"(?:{p})" for p in LIMIT_PATTERNS),
                       re.IGNORECASE)

DEFAULT_COOLDOWN_S = 900
DEFAULT_MAX_LIMITED_PARALLEL = 1


def parse_models_verbose(raw: str) -> list[dict]:
    """Parse `opencode models --verbose` (name line + JSON block each)."""
    out = []
    for chunk in raw.split("opencode/")[1:]:
        nl = chunk.find("\n")
        if nl < 0:
            continue
        name = "opencode/" + chunk[:nl].strip()
        brace = chunk.find("{", nl)
        if brace < 0:
            continue
        try:
            doc = json.loads(chunk[brace:])
        except ValueError:
            continue
        out.append({"id": name, "status": doc.get("status"),
                    "cost": doc.get("cost") or {},
                    "context": (doc.get("limit") or {}).get("context"),
                    "capabilities": list((doc.get("capabilities") or {}).keys())})
    return out


def load_live_catalog(timeout_s: int = 60) -> list[dict]:
    from .opencode_worker import OPENCODE_BIN
    proc = subprocess.run([OPENCODE_BIN, "models", "--verbose"],
                          capture_output=True, text=True, timeout=timeout_s)
    return parse_models_verbose(proc.stdout or "")


def is_zero_cost(entry: dict) -> bool:
    cost = entry.get("cost") or {}
    try:
        return float(cost.get("input", 1)) == 0 and float(cost.get("output", 1)) == 0
    except (TypeError, ValueError):
        return False


def resolve_primary(catalog: list[dict], override: str | None = None) -> str | None:
    if override:
        for e in catalog:
            if e["id"] == override and e.get("status") == "active":
                return override
        return None
    cands = [e for e in catalog
             if e.get("status") == "active" and is_zero_cost(e)
             and "toolcall" in (e.get("capabilities") or [])]
    cands.sort(key=lambda e: e.get("context") or 0, reverse=True)
    return cands[0]["id"] if cands else None


class ModelRouter:
    """Quota-aware per-task model selection with semaphores + cooldowns."""

    def __init__(self, registry: dict | None = None,
                 catalog: list[dict] | None = None,
                 store=None):
        reg = registry or {}
        self.models_cfg = reg.get("models", {})
        self.primary_override = reg.get("primary_override")
        self.cooldown_s = int(reg.get("cooldown_s", DEFAULT_COOLDOWN_S))
        self.max_limited_parallel = int(reg.get(
            "max_limited_parallel", DEFAULT_MAX_LIMITED_PARALLEL))
        self.catalog = catalog if catalog is not None else []
        self.by_id = {e["id"]: e for e in self.catalog}
        self.primary = resolve_primary(self.catalog, self.primary_override)
        self.store = store
        self._lock = threading.RLock()
        self._inflight: dict[str, int] = {}
        self._limited_inflight = 0
        self._forced_primary: set[str] = set()

    # -- config ------------------------------------------------------
    def model_type(self, model_id: str) -> str:
        cfg = self.models_cfg.get(model_id)
        if cfg:
            return cfg.get("type", "limited")
        if model_id == self.primary:
            return "unlimited"
        return "limited"

    def max_parallel(self, model_id: str) -> int:
        cfg = self.models_cfg.get(model_id, {})
        return int(cfg.get("max_parallel", 1))

    def is_known(self, model_id: str) -> bool:
        return model_id in self.models_cfg or model_id == self.primary

    def cooldown_active(self, model_id: str, now: float | None = None) -> bool:
        if self.store is None:
            return False
        return self.store.model_cooldown_active(
            model_id, now if now is not None else time.time())

    # -- selection ---------------------------------------------------
    def select(self, contract: dict, task_id: str) -> dict:
        """Return {model, model_type, reason, quota_status, fallback_used,
        deferred}."""
        policy = contract.get("model_policy", "primary-only")
        if task_id in self._forced_primary:
            return self._pick(self.primary, "forced-primary-after-limit-hit",
                              fallback_used=True)
        if policy in ("primary-only", "auto"):
            return self._pick(self.primary, "default-primary")
        if policy.startswith("capability:"):
            need = policy.split(":", 1)[1]
            return self._select_capability(contract, task_id, need)
        return self._pick(self.primary, f"unknown-policy-fallback:{policy}",
                          fallback_used=True)

    def _pick(self, model: str | None, reason: str,
              fallback_used: bool = False) -> dict:
        if not model:
            return {"model": None, "model_type": "unknown",
                    "reason": "no-primary-resolved", "quota_status": "deferred",
                    "fallback_used": fallback_used, "deferred": True}
        mtype = self.model_type(model)
        if self.cooldown_active(model):
            if model != self.primary and self.primary:
                return self._pick(self.primary, "limited-cooldown-fallback",
                                  fallback_used=True)
            return {"model": model, "model_type": mtype,
                    "reason": "primary-in-cooldown", "quota_status": "deferred",
                    "fallback_used": fallback_used, "deferred": True}
        return {"model": model, "model_type": mtype, "reason": reason,
                "quota_status": "ok", "fallback_used": fallback_used,
                "deferred": False}

    def _select_capability(self, contract: dict, task_id: str,
                           need: str) -> dict:
        cands = []
        for e in self.catalog:
            mid = e["id"]
            if e.get("status") != "active":
                continue
            if need not in (e.get("capabilities") or []):
                continue
            if not self.is_known(mid):
                continue  # fail-closed: unlisted models never selected
            cands.append(mid)
        cands.sort(key=lambda m: (0 if m == self.primary else 1, m))
        if not cands:
            return {"model": None, "model_type": "unknown",
                    "reason": f"no-model-has-capability:{need}",
                    "quota_status": "deferred", "fallback_used": False,
                    "deferred": True}
        for mid in cands:
            if mid == self.primary:
                return self._pick(mid, f"capability-need:{need}-via-primary")
            if contract.get("allow_limited"):
                if self.cooldown_active(mid):
                    continue
                return self._pick(mid, f"capability-need:{need}",
                                  fallback_used=False)
        # limited-only candidates but no allowance -> defer (never burn silently)
        prim = self.by_id.get(self.primary or "")
        if prim and need in (prim.get("capabilities") or []):
            return self._pick(self.primary, f"capability-need:{need}-via-primary")
        return {"model": None, "model_type": "unknown",
                "reason": f"capability-need:{need}-limited-only-no-allowance",
                "quota_status": "deferred", "fallback_used": False,
                "deferred": True}

    # -- quota guards --------------------------------------------------
    def headroom(self, model: str) -> int:
        with self._lock:
            if model is None or self.cooldown_active(model):
                return 0
            return max(0, self.max_parallel(model) - self._inflight.get(model, 0))

    def try_acquire(self, model: str) -> bool:
        """Non-blocking acquire respecting per-model + limited-global caps."""
        with self._lock:
            if model is None:
                return False
            if self.cooldown_active(model):
                return False
            if self._inflight.get(model, 0) >= self.max_parallel(model):
                return False
            if self.model_type(model) == "limited":
                if self._limited_inflight >= self.max_limited_parallel:
                    return False
                self._limited_inflight += 1
            self._inflight[model] = self._inflight.get(model, 0) + 1
            return True

    def release(self, model: str) -> None:
        with self._lock:
            if model is None:
                return
            self._inflight[model] = max(0, self._inflight.get(model, 0) - 1)
            if self.model_type(model) == "limited":
                self._limited_inflight = max(0, self._limited_inflight - 1)

    @staticmethod
    def is_limit_hit(stderr_detail: str) -> bool:
        return bool(_LIMIT_RE.search(stderr_detail or ""))

    def report_limit_hit(self, model: str, project_id: str | None = None,
                         task_id: str | None = None) -> None:
        with self._lock:
            until = time.time() + self.cooldown_s
            if self.store is not None:
                self.store.set_model_cooldown(model, until)
                self.store.bump_model_usage(model, "limit_hits")
            if project_id and self.store is not None:
                self.store.record_event(project_id, "model_limit_hit",
                                        {"model": model, "task_id": task_id,
                                         "cooldown_until": until})

    def force_primary(self, task_id: str) -> None:
        with self._lock:
            self._forced_primary.add(task_id)
