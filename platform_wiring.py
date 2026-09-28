"""Production wiring: compose platform subsystems into enforced paths.

This module adds NO new security logic. It wires the 41 audited leaf
modules into the orchestrator/scheduler/evolver execution paths:
policy -> capability -> sandbox -> egress -> tools -> verification ->
invariants -> audit/provenance, plus deployment, promotion, incident,
skill-trust, and AI-verification runners. Every runner returns data
and writes audit evidence; every enforcement point degrades to legacy
behavior when its profile section is absent (backward compatible).

Only stdlib plus the leaf modules is used. No network calls here.
"""

from __future__ import annotations

import hashlib
import os
import tempfile
import time
from dataclasses import dataclass, field

from agent_sandbox import SandboxResult, run_python as _sandbox_run
from business_invariants import InvariantEngine
from capability import CapabilityIssuer
from deployment import DeploymentController, FeatureFlags
from egress_firewall import EgressPolicy, check_url
from golden_corpus import GoldenCorpus
from immutable_audit import AuditChain
from incident import IncidentResponse, RedTeamLoop, correlate
from policy_engine import PolicyEngine
from promotion_pipeline import PromotionPipeline
from provenance import ProvenanceLog
from skill_trust import TrustRegistry
from tool_result_verifier import ResultVerifier
from tracing import Tracer


@dataclass
class EnforcementProfile:
    """ Knobs for the enforced path. Absent sections stay legacy. """
    policy: dict | None = None
    capability_secret: bytes | None = None
    egress: EgressPolicy | None = None
    sandbox_docker: bool = True
    trust_registry_path: str | None = None
    trust_secret: bytes | None = None
    tenant: str | None = None
    incident_actions: dict | None = None

    @staticmethod
    def from_dict(spec: dict | None | "EnforcementProfile") -> "EnforcementProfile | None":
        if not spec:
            return None
        if isinstance(spec, EnforcementProfile):
            return spec
        return EnforcementProfile(
            policy=spec.get("policy"),
            capability_secret=spec.get("capability_secret"),
            egress=spec.get("egress"),
            sandbox_docker=bool(spec.get("sandbox_docker", True)),
            trust_registry_path=spec.get("trust_registry_path"),
            trust_secret=spec.get("trust_secret"),
            tenant=spec.get("tenant"),
            incident_actions=spec.get("incident_actions"),
        )


def build_sinks(evidence_dir: str | None = None,
                audit_secret: bytes | None = None) -> dict:
    """Evidence sinks. Tmpdir when unset (volatile); caller dir when set.

    `audit_secret` signs the audit chain (HMAC). When None, the
    `AUDIT_HMAC_KEY` env var (hex, 16+ bytes) is tried; unsigned chains
    are allowed here ONLY for tests/local dev — production must use
    `build_production_sinks()` which fails closed without a key.
    """
    root = evidence_dir or tempfile.mkdtemp(prefix="plat_ev_")
    os.makedirs(root, exist_ok=True)
    secret = audit_secret
    if secret is None:
        hexkey = os.environ.get("AUDIT_HMAC_KEY", "")
        try:
            secret = bytes.fromhex(hexkey) if hexkey else None
        except ValueError:
            secret = None
        if secret is not None and len(secret) < 16:
            secret = None
    return {
        "dir": root,
        "audit": AuditChain(os.path.join(root, "audit_chain.db"),
                            secret=secret),
        "signed": secret is not None,
        "provenance": ProvenanceLog(
            os.path.join(root, "provenance_chain.jsonl")),
        "golden": GoldenCorpus(os.path.join(root, "golden_corpus.json")),
        "tracer": Tracer(os.path.join(root, "traces.jsonl")),
        "verifier": ResultVerifier(
            os.path.join(root, "tool_verdicts.jsonl")),
        "incidents": IncidentResponse(),
        "redteam": RedTeamLoop(),
    }


def build_production_sinks(evidence_dir: str | None = None,
                           audit_secret: bytes | None = None) -> dict:
    """Production sinks: SIGNED audit is mandatory (fail closed).

    Raises RuntimeError when no 16+ byte HMAC key is available from
    `audit_secret` or the `AUDIT_HMAC_KEY` env var (hex). Use this for
    every production deployment; `build_sinks()` stays for tests/dev.
    """
    secret = audit_secret
    if secret is None:
        hexkey = os.environ.get("AUDIT_HMAC_KEY", "")
        try:
            secret = bytes.fromhex(hexkey) if hexkey else None
        except ValueError:
            secret = None
    if secret is None or len(secret) < 16:
        raise RuntimeError(
            "production audit requires a 16+ byte HMAC key: set "
            "AUDIT_HMAC_KEY (hex) or pass audit_secret explicitly")
    sinks = build_sinks(evidence_dir, audit_secret=secret)
    sinks["signed"] = True
    return sinks


def audit_event(sinks: dict, *, kind: str, actor: str, subject: str,
                detail: str = "") -> dict:
    """Append one audit event; return its id + hash for result payloads."""
    return sinks["audit"].append(kind=kind, actor=actor, subject=subject,
                                 detail=detail)


def policy_gate(profile: EnforcementProfile | None, *, agent: str,
                action: str, resource: str = "") -> dict:
    """Pre-execution verdict. Unconfigured profile => not enforced."""
    if profile is None or not profile.policy:
        return {"enforced": False, "allowed": True, "needs_approval": False,
                "rule": "", "reason": "no policy configured"}
    decision = PolicyEngine(profile.policy).evaluate(
        agent=agent, action=action, resource=resource)
    return {"enforced": True, "allowed": decision.allowed,
            "needs_approval": decision.needs_approval,
            "rule": decision.rule_id, "reason": decision.reason}


def mint_task_capability(profile: EnforcementProfile | None, *,
                         actions: list[str], resource: str = "*",
                         ttl_s: int = 600) -> dict:
    """Issue a task-scoped capability (absent secret => not enforced)."""
    if profile is None or not profile.capability_secret:
        return {"enforced": False, "token": None}
    issuer = CapabilityIssuer(profile.capability_secret)
    token = issuer.issue(actions=actions, resource=resource, ttl_s=ttl_s)
    body = issuer._decode(token)
    return {"enforced": True, "token": token, "key_id": body.get("id"),
            "issuer": issuer}


def check_capability(issuer, token: str, *, action: str,
                     resource: str = "") -> dict:
    """Verify one capability use. Returns ok + reason (never raises)."""
    ok, reason = issuer.verify(token, action=action, resource=resource)
    return {"ok": bool(ok), "reason": str(reason)}


def extract_external_urls(workflow: dict) -> list[str]:
    """Collect URL strings from httpRequest-class node parameters."""
    found: list[str] = []
    for node in (workflow or {}).get("nodes", []):
        params = node.get("parameters", {}) if isinstance(node, dict) else {}
        if not isinstance(params, dict):
            continue
        for key in ("url", "webhookUrl", "callbackUrl"):
            val = params.get(key)
            if isinstance(val, str) and val.startswith(("http://",
                                                        "https://")):
                found.append(val)
    seen, unique = set(), []
    for url in found:
        if url not in seen:
            seen.add(url)
            unique.append(url)
    return unique


def egress_guard(profile: EnforcementProfile | None,
                 urls: list[str]) -> dict:
    """Validate destinations. Unconfigured profile => not enforced."""
    if profile is None or profile.egress is None:
        return {"enforced": False, "blocked": [], "allowed": list(urls)}
    blocked, allowed = [], []
    for url in urls:
        verdict = check_url(url, profile.egress)
        if verdict.allowed:
            allowed.append(url)
        else:
            blocked.append({"url": url, "reason": verdict.reason})
    return {"enforced": True, "blocked": blocked, "allowed": allowed}


class AgentSandboxShim:
    """Adapter exposing cybersec-sandbox call shape over agent_sandbox.

    save_code_nodes_runtime_check() calls sandbox.run_python(code) and
    reads result["success"]. This shim translates SandboxResult without
    touching the existing 2c code path.
    """

    def __init__(self, prefer_docker: bool = True):
        self.prefer_docker = bool(prefer_docker)

    def run_python(self, code: str) -> dict:
        res: SandboxResult = _sandbox_run(
            code, prefer_docker=self.prefer_docker)
        return {"success": bool(res.ok), "output": res.stdout,
                "stderr": res.stderr, "tier": res.tier,
                "returncode": res.returncode,
                "timed_out": bool(res.timed_out), "reason": res.reason}


def skill_filter(profile: EnforcementProfile | None,
                 records: list) -> tuple[list, dict]:
    """Trust-gate skill records. Returns (allowed, report).

    Unconfigured profile or registry => pass-through with a note (legacy
    behavior preserved). Enforcing mode excludes unknown/tampered
    verdicts; high-risk 'review' verdicts are also excluded here (the
    human-approval lane lives in HITL flows, not auto-execution).
    """
    report: dict = {"mode": "passthrough", "verdicts": {}, "excluded": []}
    if profile is None or not profile.trust_registry_path:
        return list(records), report
    registry = TrustRegistry(str(profile.trust_registry_path),
                             profile.trust_secret or b"0" * 32)
    report["mode"] = "enforce"
    allowed = []
    for rec in records:
        path = getattr(rec, "path", None)
        name = getattr(rec, "name", "?")
        if not path:
            report["verdicts"][name] = ("unknown", "no local copy")
            report["excluded"].append(name)
            continue
        verdict, reason = registry.check_load(name, path)
        report["verdicts"][name] = (verdict, reason)
        if verdict == "ok":
            allowed.append(rec)
        else:
            report["excluded"].append(name)
    return allowed, report


def ai_verify(sinks: dict, *, tool: str, claimed, checker,
              evidence: str = "", invariants=None, domain: str = "",
              payload: dict | None = None) -> dict:
    """Independent verification: tool checker, then business invariants.

    Returns {tool_ok, invariants_ok, accepted, verdict_refs}. Acceptance
    requires BOTH the independent checker and (when supplied) every
    domain invariant. Results journal + audit in one place.
    """
    tool_out = sinks["verifier"].verify(
        tool=tool, claimed=claimed, checker=checker, evidence=evidence)
    inv_out = {"ok": True, "failed": [], "skipped": True}
    if invariants is not None and domain:
        inv_out = invariants.evaluate(domain, payload or {})
        inv_out["skipped"] = False
    accepted = bool(tool_out["verified"]) and bool(inv_out["ok"])
    audit_event(sinks, kind="ai_verification",
                actor="platform_wiring",
                subject=f"{tool}:{tool_out['claim_hash'][:12]}",
                detail=f"accepted={accepted} tool={tool_out['verified']} "
                       f"invariants={inv_out['ok']}")
    return {"tool_ok": bool(tool_out["verified"]),
            "invariants_ok": bool(inv_out["ok"]),
            "invariants_failed": list(inv_out.get("failed", [])),
            "accepted": accepted,
            "claim_hash": tool_out["claim_hash"]}


def deploy_release(sinks: dict, *, release: str, previous: str,
                   gates_fn, probes: dict, promote_fn=None,
                   feature_flags=None) -> dict:
    """Gates -> canary -> promote/rollback with audit + provenance."""
    audit_event(sinks, kind="deploy_start", actor="platform_wiring",
                subject=release, detail=f"previous={previous}")
    gates_ok, gates_note = gates_fn()
    if not gates_ok:
        audit_event(sinks, kind="deploy_blocked", actor="platform_wiring",
                    subject=release, detail=f"gates: {gates_note}")
        return {"released": False, "live": previous,
                "reason": f"gates blocked: {gates_note}"}
    controller = DeploymentController(flags=feature_flags or FeatureFlags())
    out = controller.rollout(release, previous, probes,
                             promote_fn=promote_fn)
    sinks["provenance"].link(release, "deployment",
                             f"live={out['live']} "
                             f"rolled_back={out['rolled_back']}")
    audit_event(sinks, kind="deploy_result", actor="platform_wiring",
                subject=release,
                detail=f"live={out['live']} rolled_back={out['rolled_back']}")
    return {"released": not out["rolled_back"], **out}


def promote_candidate(sinks: dict, pipeline: PromotionPipeline,
                      candidate_id: str, candidate,
                      stages: dict) -> dict:
    """Governed promotion with audit trail of the full stage report."""
    report = pipeline.run(candidate_id, candidate, stages)
    audit_event(sinks, kind="promotion",
                actor="platform_wiring", subject=candidate_id,
                detail=f"promoted={report['promoted']} "
                       f"halted_at={report['halted_at']}")
    return report


def handle_failure(sinks: dict, *, incident_id: str, alert: dict,
                   actions: dict | None = None,
                   golden_case: dict | None = None) -> dict:
    """Detect -> respond -> correlate -> golden-case in one call."""
    responder = IncidentResponse(actions or {})
    response = responder.respond(incident_id, {"alert": alert})
    sinks["incidents"].runs.append(response)
    correlation = correlate([alert])
    golden_added = None
    if golden_case:
        sinks["golden"].add_case(
            golden_case["id"], reproducer=golden_case["reproducer"],
            expect=golden_case.get("expect", "must not recur"),
            incident=incident_id)
        golden_added = golden_case["id"]
    audit_event(sinks, kind="incident", actor="platform_wiring",
                subject=incident_id,
                detail=f"contained={response['contained']} "
                       f"golden={golden_added}")
    return {"response": response, "correlation": correlation,
            "golden_added": golden_added}


def task_fingerprint(task_prompt: str) -> str:
    """Stable short id for a task (audit subjects, no raw text)."""
    import hashlib as _hl
    return _hl.sha256(task_prompt.encode("utf-8")).hexdigest()[:16]
