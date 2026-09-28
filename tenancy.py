"""Multi-tenancy: isolation + per-tenant budgets with action states.

Each tenant owns an isolated namespace (keys prefixed, stores
partitioned) plus a budget {monthly_cap, state}. Spend moves the
state machine: ok -> warning (80%) -> degraded (100%: cheaper model,
expensive paths off) -> critical (escalate to human) -> exceeded
(block new spend). State transitions append to a per-tenant ledger
for audit. No cross-tenant reads: every accessor requires tenant_id.

Only stdlib is used. Persistence is a caller-chosen JSON file.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

STATES = ("ok", "warning", "degraded", "critical", "exceeded")
WARN_AT, DEGRADE_AT, CRIT_AT = 0.8, 1.0, 1.2


class Tenancy:
    """Tenant registry with isolated keys + budget state machine."""

    def __init__(self, path: str = "tenancy.json"):
        self._path = Path(path)
        self._tenants: dict[str, dict] = {}
        self._load()

    def _load(self) -> None:
        if not self._path.is_file():
            return
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return
        if isinstance(data, dict):
            self._tenants = {str(k): v for k, v in data.items()
                             if isinstance(v, dict)}

    def save(self) -> None:
        """Persist tenants + ledgers."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(self._tenants, sort_keys=True,
                                         indent=1, default=str),
                              encoding="utf-8")

    def add_tenant(self, tenant_id: str, monthly_cap: float) -> dict:
        """Register a tenant with a monthly AI budget cap."""
        tid = str(tenant_id)
        if tid in self._tenants:
            raise ValueError(f"tenant exists: {tid}")
        rec = {"cap": float(monthly_cap), "spent": 0.0, "state": "ok",
               "ledger": []}
        self._tenants[tid] = rec
        return {"tenant": tid, "state": "ok"}

    def namespaced(self, tenant_id: str, key: str) -> str:
        """Isolation primitive: prefix every foreign key with tenant."""
        tid = str(tenant_id)
        if tid not in self._tenants:
            raise KeyError(f"unknown tenant: {tid}")
        return f"t:{tid}:{key}"

    def record_spend(self, tenant_id: str, amount: float,
                     note: str = "") -> dict:
        """Add spend; advance the state machine; return state + actions."""
        rec = self._tenants.get(str(tenant_id))
        if rec is None:
            raise KeyError(f"unknown tenant: {tenant_id}")
        if amount < 0:
            raise ValueError("spend cannot be negative")
        rec["spent"] = round(rec["spent"] + float(amount), 6)
        ratio = rec["spent"] / rec["cap"] if rec["cap"] > 0 else 0.0
        if ratio >= CRIT_AT:
            state, actions = "exceeded", ["block_new_spend",
                                          "escalate_human"]
        elif ratio >= 1.1:
            state, actions = "critical", ["escalate_human",
                                          "degrade_model"]
        elif ratio >= DEGRADE_AT:
            state, actions = "degraded", ["degrade_model",
                                          "disable_expensive_paths"]
        elif ratio >= WARN_AT:
            state, actions = "warning", ["notify_owner"]
        else:
            state, actions = "ok", []
        rec["state"] = state
        rec["ledger"].append({"ts": time.time(), "amount": float(amount),
                              "note": str(note), "state": state})
        return {"tenant": str(tenant_id), "state": state,
                "spent": rec["spent"], "actions": actions}

    def status(self, tenant_id: str) -> dict:
        """Current budget posture for one tenant."""
        rec = self._tenants.get(str(tenant_id))
        if rec is None:
            raise KeyError(f"unknown tenant: {tenant_id}")
        return {"tenant": str(tenant_id), "cap": rec["cap"],
                "spent": rec["spent"], "state": rec["state"],
                "events": len(rec["ledger"])}
