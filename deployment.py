"""Deployment controller: staged rollout with automatic rollback.

Replaces overwrite-deploys: a candidate advances 1% -> 10% -> 50% ->
100% behind feature flags; each stage runs health probes (error
rate, latency, tool failures, cost) over a sample window; any probe
breach halts and rolls back to the pinned previous version. Flags are
plain named booleans with percentage buckets evaluated off a stable
identity hash (same identity always sees the same bucket).

Only stdlib is used. Probes and promoters are caller callables.
"""

from __future__ import annotations

import hashlib
import time

STAGES = (1, 10, 50, 100)


class FeatureFlags:
    """Percentage-bucketed flags over stable identity hashes."""

    def __init__(self):
        self._flags: dict[str, int] = {}

    def set(self, name: str, percent: int) -> None:
        """Set rollout percent 0..100 for a flag."""
        if not 0 <= int(percent) <= 100:
            raise ValueError("percent must be 0..100")
        self._flags[str(name)] = int(percent)

    def enabled(self, name: str, identity: str = "") -> bool:
        """Deterministic bucket: sha of flag+identity mod 100 < percent."""
        pct = self._flags.get(str(name), 0)
        if pct <= 0:
            return False
        if pct >= 100:
            return True
        h = hashlib.sha256(f"{name}|{identity}".encode()).hexdigest()
        return (int(h, 16) % 100) < pct


class DeploymentController:
    """Canary stages + probe gates + automatic rollback."""

    def __init__(self, flags: FeatureFlags | None = None):
        self.flags = flags or FeatureFlags()
        self.history: list[dict] = []

    def rollout(self, release: str, previous: str, probes: dict,
                promote_fn=None) -> dict:
        """Advance stages while probes pass; rollback on first breach.

        probes: {stage_percent: fn() -> (ok, metrics-dict)}.
        promote_fn(stage) applies traffic shift (optional in dry runs).
        """
        flag = f"release:{release}"
        trail = []
        for stage in STAGES:
            fn = probes.get(stage)
            if fn is None:
                trail.append({"stage": stage, "ok": False,
                              "note": "no probe: halt"})
                return self._finish(release, previous, trail,
                                    rolled_back=True,
                                    reason=f"missing probe at {stage}%")
            try:
                ok, metrics = fn()
            except Exception as exc:  # noqa: BLE001 - breach, roll back
                ok, metrics = False, {"error": str(exc)}
            self.flags.set(flag, stage if ok else 0)
            if promote_fn is not None and ok:
                try:
                    promote_fn(stage)
                except Exception as exc:  # noqa: BLE001 - breach
                    ok, metrics = False, {"promote_error": str(exc)}
            trail.append({"stage": stage, "ok": bool(ok),
                          "metrics": dict(metrics or {})})
            if not ok:
                return self._finish(
                    release, previous, trail, rolled_back=True,
                    reason=f"probe breach at {stage}%")
        return self._finish(release, previous, trail, rolled_back=False,
                            reason="")

    def _finish(self, release, previous, trail, rolled_back, reason):
        if rolled_back:
            self.flags.set(f"release:{release}", 0)
        out = {"release": release, "previous": previous,
               "rolled_back": rolled_back, "reason": reason,
               "trail": trail, "ts": time.time(),
               "live": previous if rolled_back else release}
        self.history.append(out)
        return out
