"""Cost governor: budget states that ACT (degrade, disable, escalate).

Dashboards watch; this module decides. A spend ledger (caller-fed
{model, tokens, cost, expensive_path}) rolls into windowed totals;
threshold crossings emit actions: warn owner, switch default model to
the cheap tier, disable flagged expensive paths, require human
approval for further spend, or block. Actions apply in severity order
and every transition journals with its trigger values.

Only stdlib is used. Read-only toward cost_ledger.py by design (it
consumes numbers; it never rewrites platform books).
"""

from __future__ import annotations

import time

LEVELS = ("normal", "watch", "tight", "critical", "frozen")


class CostGovernor:
    """Threshold-driven spend actions over a caller-fed ledger."""

    def __init__(self, *, warn_at: float, tight_at: float,
                 critical_at: float, freeze_at: float,
                 cheap_model: str = "local"):
        bounds = sorted([warn_at, tight_at, critical_at, freeze_at])
        if list(bounds) != [warn_at, tight_at, critical_at, freeze_at]:
            raise ValueError("thresholds must ascend")
        if not cheap_model:
            raise ValueError("cheap_model name required")
        self._bounds = {"warn": float(warn_at), "tight": float(tight_at),
                        "critical": float(critical_at),
                        "freeze": float(freeze_at)}
        self._cheap = str(cheap_model)
        self._spent = 0.0
        self._log: list[dict] = []

    def record(self, *, cost: float, model: str = "",
               expensive_path: bool = False) -> dict:
        """Add spend; return the resulting level + actions taken."""
        if cost < 0:
            raise ValueError("cost cannot be negative")
        self._spent = round(self._spent + float(cost), 6)
        return self._act(model=model, expensive_path=expensive_path)

    def _act(self, *, model: str, expensive_path: bool) -> dict:
        b, s = self._bounds, self._spent
        actions: list[str] = []
        if s >= b["freeze"]:
            level, actions = "frozen", ["block_spend", "escalate_human"]
        elif s >= b["critical"]:
            level, actions = "critical", ["require_approval",
                                          "disable_expensive_paths",
                                          "escalate_human"]
        elif s >= b["tight"]:
            level = "tight"
            actions = ["use_cheap_model:" + self._cheap]
            if expensive_path or model != self._cheap:
                actions.append("reroute_to_cheap")
        elif s >= b["warn"]:
            level, actions = "watch", ["notify_owner"]
        else:
            level = "normal"
        entry = {"ts": time.time(), "spent": s, "level": level,
                 "actions": actions}
        self._log.append(entry)
        return {"level": level, "spent": s, "actions": actions}

    def status(self) -> dict:
        """Current posture without recording spend."""
        return self._act(model=self._cheap, expensive_path=False)

    def history(self) -> list[dict]:
        """Transitions in order (read-only copy)."""
        return list(self._log)
