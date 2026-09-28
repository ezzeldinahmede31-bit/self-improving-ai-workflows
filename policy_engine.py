"""Deterministic Policy-as-Code engine.

Independent allow/deny/approve decisions evaluated BEFORE any execution.
A prompt, a model output, or a caller preference can never override a
deny — the verdict is pure function of (policy, request, spend state).

Policy schema (plain dict/JSON, no YAML dependency):
    {
      "default": "deny",            # fallback when no rule matches
      "rules": [
        {"id": "r1", "effect": "allow" | "deny" | "approve",
         "agent": "*",              # exact name or "*" wildcard
         "action": "calendar.read", # fnmatch glob, e.g. "calendar.*"
         "resource": "*",           # fnmatch glob over resource string
         "reason": "human text"}
      ],
      "budget": {"max_tokens": 500000, "max_cost": 10.0,
                 "max_runtime_s": 1800},
    }

Rule order: first matching DENY wins outright; otherwise first matching
APPROVE routes to human review; otherwise first matching ALLOW permits;
no match falls back to "default". Budget exhaustion denies everything
with an explicit reason (spend tracked via record_use / reset).
"""

from __future__ import annotations

import fnmatch
import time
from dataclasses import dataclass, field


@dataclass
class PolicyDecision:
    allowed: bool
    needs_approval: bool = False
    reason: str = ""
    rule_id: str = ""


@dataclass
class SpendState:
    tokens_used: int = 0
    cost_used: float = 0.0
    started_at: float = field(default_factory=time.time)


class PolicyEngine:
    """Stateless policy text + mutable spend ledger (per engine instance)."""

    def __init__(self, policy: dict):
        if not isinstance(policy, dict):
            raise TypeError("policy must be a dict")
        self._default = str(policy.get("default", "deny")).lower()
        if self._default not in ("allow", "deny", "approve"):
            raise ValueError("policy.default must be allow|deny|approve")
        self._rules = list(policy.get("rules", []) or [])
        for rule in self._rules:
            self._check_rule(rule)
        self._budget = dict(policy.get("budget", {}) or {})
        self.spend = SpendState()

    @staticmethod
    def _check_rule(rule: dict) -> None:
        for key in ("id", "effect", "agent", "action", "resource"):
            if key not in rule:
                raise ValueError(f"rule missing required key: {key}")
        if rule["effect"] not in ("allow", "deny", "approve"):
            raise ValueError(f"rule {rule.get('id')}: bad effect")

    def _budget_verdict(self) -> PolicyDecision | None:
        b = self._budget
        if not b:
            return None
        spent_s = time.time() - self.spend.started_at
        if "max_tokens" in b and self.spend.tokens_used > int(b["max_tokens"]):
            return PolicyDecision(False, False, "budget: token ceiling reached", "budget")
        if "max_cost" in b and self.spend.cost_used > float(b["max_cost"]):
            return PolicyDecision(False, False, "budget: cost ceiling reached", "budget")
        if "max_runtime_s" in b and spent_s > float(b["max_runtime_s"]):
            return PolicyDecision(False, False, "budget: runtime ceiling reached", "budget")
        return None

    def evaluate(self, *, agent: str, action: str, resource: str = "") -> PolicyDecision:
        """Return the verdict for one proposed operation."""
        over = self._budget_verdict()
        if over is not None:
            return over
        hit_approve: PolicyDecision | None = None
        for rule in self._rules:
            if not fnmatch.fnmatchcase(str(agent), str(rule["agent"])):
                continue
            if not fnmatch.fnmatchcase(str(action), str(rule["action"])):
                continue
            if not fnmatch.fnmatchcase(str(resource), str(rule["resource"])):
                continue
            effect = rule["effect"]
            reason = str(rule.get("reason", rule["id"]))
            if effect == "deny":
                return PolicyDecision(False, False, reason, str(rule["id"]))
            if effect == "approve" and hit_approve is None:
                hit_approve = PolicyDecision(False, True, reason, str(rule["id"]))
            if effect == "allow" and hit_approve is None:
                return PolicyDecision(True, False, reason, str(rule["id"]))
        if hit_approve is not None:
            return hit_approve
        if self._default == "allow":
            return PolicyDecision(True, False, "policy default allow", "default")
        if self._default == "approve":
            return PolicyDecision(False, True, "policy default approve", "default")
        return PolicyDecision(False, False, "policy default deny", "default")

    def record_use(self, *, tokens: int = 0, cost: float = 0.0) -> None:
        """Add observed spend (call AFTER the metered operation)."""
        if tokens < 0 or cost < 0:
            raise ValueError("spend cannot be negative")
        self.spend.tokens_used += int(tokens)
        self.spend.cost_used += float(cost)

    def reset_spend(self) -> None:
        """Start a fresh spend window (new billing interval)."""
        self.spend = SpendState()

    def remaining(self) -> dict:
        """Remaining budget headroom (None where uncapped)."""
        b = self._budget
        out: dict = {}
        out["tokens"] = (int(b["max_tokens"]) - self.spend.tokens_used
                         if "max_tokens" in b else None)
        out["cost"] = (float(b["max_cost"]) - self.spend.cost_used
                       if "max_cost" in b else None)
        return out
