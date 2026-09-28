"""Central enforcement: No Gate -> No Execution.

Every sensitive production action (tool/HTTP/filesystem/MCP/browser/n8n/
database/deployment/memory-write/external-service) MUST pass through
`EnforcedExecutor.execute`. The executor runs the mandatory chain:

    Policy -> Capability -> Skill Trust -> Sandbox tier -> Egress ->
    Execution -> Tool Result Verification -> Business Invariants ->
    Audit/Provenance -> Commit

Fail-closed semantics:
  - `strict=True` (production default): any missing gate configuration or
    any gate denial raises `EnforcementError` / returns denied verdict.
    There is deliberately NO legacy passthrough in strict mode.
  - `strict=False` (explicit opt-in, tests/local dev only): gates that are
    unconfigured are recorded as `enforced=False` in the verdict trail
    instead of blocking, so existing non-production callers keep working.

Only stdlib + leaf platform modules are used. No network calls here.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


class EnforcementError(RuntimeError):
    """Raised when a sensitive action is attempted without enforcement."""


SENSITIVE_ACTIONS = frozenset({
    "tool.execute",
    "http.fetch",
    "filesystem.write",
    "mcp.call",
    "browser.act",
    "n8n.execute",
    "database.write",
    "deployment.promote",
    "memory.write",
    "external.call",
    "workflow.execute",
    "code.execute",
    "net.fetch",
})


@dataclass
class EnforcementVerdict:
    allowed: bool
    action: str
    gates: dict = field(default_factory=dict)
    reason: str = ""
    audit_id: Any = None


class EnforcedExecutor:
    """Fail-closed gate chain around any sensitive callable.

    Parameters mirror `platform_wiring.EnforcementProfile` plus:
      - `strict`: True = fail closed on unconfigured gates (production).
      - `verifier`: optional `tool_result_verifier.ResultVerifier`-compatible
        object with `.verify(tool, claimed, checker, evidence)`.
      - `invariants`: optional `business_invariants.InvariantEngine`-like
        object with `.evaluate(domain, payload)`.
      - `invariant_domain`: domain name used for invariant evaluation.
      - `audit_sink` / `provenance_sink`: optional sinks; every decision
        (allow AND deny) is recorded when present.
    """

    def __init__(
        self,
        profile=None,
        *,
        strict: bool = True,
        verifier=None,
        invariants=None,
        invariant_domain: str = "",
        audit_sink=None,
        provenance_sink=None,
    ):
        self.profile = profile
        self.strict = bool(strict)
        self.verifier = verifier
        self.invariants = invariants
        self.invariant_domain = invariant_domain
        self.audit_sink = audit_sink
        self.provenance_sink = provenance_sink

    # -- internal helpers -------------------------------------------------
    def _record(self, kind: str, actor: str, subject: str, detail: str = ""):
        if self.audit_sink is None:
            return None
        try:
            return self.audit_sink.append(
                kind=kind, actor=actor, subject=subject, detail=detail)
        except Exception:
            return None

    def _deny(self, action: str, gates: dict, reason: str) -> EnforcementVerdict:
        self._record("enforcement_denial", "enforced_executor",
                     action, reason[:200])
        if self.strict:
            raise EnforcementError(f"denied {action}: {reason}")
        return EnforcementVerdict(False, action, gates, reason)

    # -- main entry --------------------------------------------------------
    def execute(
        self,
        *,
        action: str,
        actor: str = "orchestrator",
        resource: str = "",
        urls: list[str] | None = None,
        skill_records: list | None = None,
        capability_token: str | None = None,
        capability_issuer=None,
        run: Callable[[], Any] | None = None,
        verify_checker: Callable | None = None,
        verify_tool: str = "",
        invariant_payload: dict | None = None,
        tenant: str = "",
    ) -> tuple[EnforcementVerdict, Any]:
        """Run the full gate chain, then `run()` exactly once on allow.

        Returns (verdict, result). In strict mode a denial raises
        `EnforcementError` instead of returning.
        """
        import platform_wiring

        gates: dict = {}
        sensitive = action in SENSITIVE_ACTIONS

        # 1. Policy gate — REQUIRED in strict mode for sensitive actions.
        if self.profile is None or not getattr(self.profile, "policy", None):
            gates["policy"] = {"enforced": False}
            if sensitive and self.strict:
                return self._deny(action, gates,
                                  "no policy configured (strict mode)"), None
        else:
            v = platform_wiring.policy_gate(
                self.profile, agent=actor, action=action, resource=resource)
            gates["policy"] = v
            if v.get("enforced") and not v.get("allowed") \
                    and not v.get("needs_approval"):
                return self._deny(
                    action, gates,
                    f"policy denial rule={v.get('rule')} {v.get('reason')}"), None
            if v.get("enforced") and v.get("needs_approval"):
                return self._deny(
                    action, gates,
                    f"policy requires approval rule={v.get('rule')}"), None

        # 2. Capability — REQUIRED in strict mode for sensitive actions.
        if capability_issuer is not None and capability_token:
            chk = platform_wiring.check_capability(
                capability_issuer, capability_token,
                action=action, resource=resource or "*")
            gates["capability"] = chk
            if not chk["ok"]:
                return self._deny(
                    action, gates,
                    f"capability rejected: {chk['reason']}"), None
        elif sensitive and self.strict:
            gates["capability"] = {"ok": False,
                                   "reason": "no capability presented"}
            return self._deny(action, gates,
                              "no capability presented (strict mode)"), None
        else:
            gates["capability"] = {"ok": True, "reason": "not required"}

        # 3. Skill trust — only when skill records are supplied.
        if skill_records is not None:
            allowed, report = platform_wiring.skill_filter(
                self.profile, skill_records)
            gates["skill_trust"] = {"mode": report.get("mode"),
                                    "excluded": report.get("excluded", [])}
            if report.get("mode") == "enforce" and report.get("excluded"):
                return self._deny(
                    action, gates,
                    f"untrusted skills excluded: {report['excluded']}"), None

        # 4. Egress — only when outbound URLs are declared.
        if urls:
            eg = platform_wiring.egress_guard(self.profile, urls)
            gates["egress"] = {"enforced": eg["enforced"],
                               "blocked": eg["blocked"]}
            if eg["enforced"] and eg["blocked"]:
                return self._deny(
                    action, gates,
                    f"egress blocked: {eg['blocked'][:2]}"), None
            if not eg["enforced"] and sensitive and self.strict:
                return self._deny(action, gates,
                                  "egress not enforced (strict mode)"), None

        # 5. Execution (exactly once).
        result = run() if run is not None else None
        gates["execution"] = {"ran": run is not None}

        # 6. Tool-result verification — required when a checker is supplied.
        if verify_checker is not None:
            if self.verifier is None:
                gates["tool_verify"] = {"verified": False,
                                        "reason": "no verifier configured"}
                if sensitive and self.strict:
                    return self._deny(
                        action, gates,
                        "no tool-result verifier (strict mode)"), None
            else:
                out = self.verifier.verify(
                    tool=verify_tool or action, claimed=result,
                    checker=verify_checker, evidence="")
                gates["tool_verify"] = {"verified": bool(out["verified"])}
                if not out["verified"]:
                    return self._deny(action, gates,
                                      "tool result failed verification"), None

        # 7. Business invariants — required when a payload is supplied.
        if invariant_payload is not None:
            if self.invariants is None or not self.invariant_domain:
                gates["invariants"] = {"ok": False,
                                       "reason": "no invariant engine"}
                if sensitive and self.strict:
                    return self._deny(
                        action, gates,
                        "no business invariants (strict mode)"), None
            else:
                inv = self.invariants.evaluate(self.invariant_domain,
                                               invariant_payload)
                gates["invariants"] = {"ok": bool(inv["ok"]),
                                       "failed": inv.get("failed", [])}
                if not inv["ok"]:
                    return self._deny(
                        action, gates,
                        f"invariant failure: {inv.get('failed', [])[:2]}"), None

        # 8. Audit + provenance (never mutate the allow verdict).
        entry = self._record("enforcement_allow", actor,
                             f"{tenant + ':' if tenant else ''}{action}",
                             f"resource={resource[:80]}")
        if self.provenance_sink is not None:
            try:
                self.provenance_sink.link(action, "enforcement",
                                          f"actor={actor} tenant={tenant}")
            except Exception:
                pass
        verdict = EnforcementVerdict(True, action, gates, "all gates passed",
                                     entry)
        return verdict, result
