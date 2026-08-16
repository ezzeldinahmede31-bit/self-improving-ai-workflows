#!/usr/bin/env python3
"""Build Gates Pipeline — runs ALL project gates over any build artifact
(workflow JSON / script / agent design) before deployment, mirroring the
stages the Python system itself enforces:

  Stage 1 SECURITY  — SecurityGate: hardcoded secrets, SSRF/metadata egress,
                      banned code-execution (subprocess/eval/child_process),
                      privileged containers, promoted auto-rules. Risk >= 40
                      is ALWAYS fatal and routes to human review, never a
                      silent auto-fix.
  Stage 2 QUALITY   — QualityGate: Schema V2 expression syntax, graph
                      integrity, reliability (error handling / pinned data),
                      size, cyclomatic complexity. Score >= 80 required.
  Stage 3 INTEGRITY — ChainIntegrityChecker: deterministic DAG closure over
                       the workflow connections (orphans, duplicates,
                       self-deps, cycles). Structural violations are a hard
                       stop and can never be overridden.
  Stage 3.4 PRECISION — N8nPrecisionGate: n8n runtime-precision structural
                       invariants the static gates miss but the n8n runtime
                       enforces — unique node names, at least one trigger
                       (unless `_gates.subworkflow`), valid typeVersion >= 1,
                       every $node[...] / $('...') / $nodes.X expression ref
                       resolving to an existing node, and real (non-
                       placeholder) credential binding on app-like nodes.
                       Hard stop, never overridable.
  Stage 4 STABILITY — StabilityGate (new): real live-instance verification on
                      the n8n instance. Requires REQUIRED_CONSECUTIVE_PASSES
                      consecutive executions whose output exactly matches the
                      expected output defined at design time (`_gates.stability`
                      block). Distinguishes FLAT_FAILURE (deterministic bug from
                      the first attempt) from FLAKY (reached N consecutive then
                      regressed — intermittent) as a separate report signal.
                      Opt-in; SKIPs when the annotation is absent.
  Stage 5 MATH      — MathLogicGate (new): deterministic math/logic
                      verification via math-verify (answer equivalence),
                      Z3 (SAT/SMT constraints, prove-by-UNSAT), sympy
                      (symbolic simplify), and self-consistency voting
                      over parallel candidates (test-time-compute-scaling).
  Stage 6 REASONING — DeepReasoningGate (new): encodes the reasoning skills'
                      gates as deterministic checks — counting/boundary
                      detection (off-by-one-boundary-guard), brute-force
                      cross-validation requirement, two-method parity; when a
                      problem is flagged but unverifiable mechanically, it
                      escalates to human review instead of bluffing
                      (elite-verifier-delegation: fall back to internal
                      deterministic verifiers, label confidence honestly).
  Stage 6 HITL      — HITLGate: any security rejection or reasoning flag
                      freezes as PENDING_APPROVAL in audit.db with a 15-min
                      timeout; default policy is DENY (EXPIRED_REJECTED).
                      Approval requires the operator token; forged tokens are
                      logged.
  Stage 7 AUDIT     — audit_log_entry row in audit.db + full JSON report
                      written under memory/audits/.

Note: DRY-RUN (real trial-execution evidence before HITL) is Stage 7 of the
runtime chain (after REASONING). STABILITY (Stage 4) runs after QUALITY +
INTEGRITY pass and before HITL, as requested.

CLI:
  python scripts/build_gates_pipeline.py <artifact> [--no-hitl] [--json]
      artifact: path to workflow JSON, script file, or an annotated artifact
      with a `_gates` section (see GATES_SCHEMA in this module).
  python scripts/build_gates_pipeline.py --approve <request_id> <token>
  python scripts/build_gates_pipeline.py --reject <request_id> <reason>

Exit code 0 = READY_FOR_DEPLOYMENT. 1 = any violation or pending human review.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from security_gate import SecurityGate, RISK_THRESHOLD
from quality_gate import QualityGate, QUALITY_THRESHOLD
from chain_integrity_checker import structural_integrity_check
from hitl_gate import HITLGate, DEFAULT_DB_PATH
from auto_self_evolver import SKILLS_ROOT
from scripts.n8n_stability_verifier import (
    verify_stability, N8N_API_KEY, N8N_BASE_URL, REQUIRED_CONSECUTIVE_PASSES,
)
from scripts.gate_skill_invoker import run_all_mandatory_skills
from scripts.gate_complaints import ComplaintsRegistry

# Math/logic engine availability (installed in venv: math-verify, z3, sympy,
# python-sat). If any engine is missing the gate degrades honestly to SKIP.
try:
    from math_verify import parse, verify as mv_verify
    _HAS_MV = True
except Exception:
    _HAS_MV = False
try:
    import z3
    _HAS_Z3 = True
except Exception:
    _HAS_Z3 = False
try:
    import sympy
    _HAS_SYMPY = True
except Exception:
    _HAS_SYMPY = False

HITL_TIMEOUT_MINUTES = 15
AUDITS_DIR = ROOT / "memory" / "audits"

# Counting / boundary keywords (off-by-one-boundary-guard trigger set).
COUNTING_KEYWORDS = re.compile(
    r"\bcount\b|how many|number of (solutions|roots|ways)|in the interval|"
    r"inclusive|exclusive|at most|at least|how often|fence-?post|"
    r"open-?closed|\bperiods\b|\bbetween\b", re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# n8n runtime-precision rules (N8nPrecisionGate, Stage 3.4 PRECISION)
# ---------------------------------------------------------------------------
# Node types that NEVER bind credentials (control-flow / data / trigger /
# response nodes). Every other node type is 'app-like' and must carry a real
# credential (httpRequest may declare authentication: none explicitly).
NO_CRED_ALLOWLIST = {
    "n8n-nodes-base.code", "n8n-nodes-base.webhook",
    "n8n-nodes-base.respondToWebhook",
    "n8n-nodes-base.scheduleTrigger", "n8n-nodes-base.manualTrigger",
    "n8n-nodes-base.formTrigger", "n8n-nodes-base.chatTrigger",
    "n8n-nodes-base.form",
    "n8n-nodes-base.set", "n8n-nodes-base.if", "n8n-nodes-base.switch",
    "n8n-nodes-base.merge", "n8n-nodes-base.removeDuplicates",
    "n8n-nodes-base.wait", "n8n-nodes-base.stickyNote",
    "n8n-nodes-base.comment", "n8n-nodes-base.splitInBatches",
    "n8n-nodes-base.executeWorkflow", "n8n-nodes-base.noOp",
    "n8n-nodes-base.errorTrigger", "n8n-nodes-base.loop",
    "n8n-nodes-base.workflowTool", "n8n-nodes-langchain.toolWorkflow",
    "n8n-nodes-langchain.agent",
}

# LLM-agent container nodes (n8n-nodes-langchain.agent and similar). These
# never bind a credential themselves — the model + tool nodes connected to them
# do. Exempted from P5's credential requirement so the connected model node is
# what gets checked. Exact-type match only (never substring — "magento" etc.
# contain "agent" but are app nodes that DO bind credentials).
LLM_AGENT_CONTAINERS = {"n8n-nodes-langchain.agent"}

# Credential names that are clearly placeholders and must never ship.
PLACEHOLDER_CRED_RE = re.compile(
    r"(?:your|replace|example|change|xxx|changeme|todo|insert)"
    r"|(?:YOUR_[A-Z_]+)|(?:<[^>]+>)", re.IGNORECASE,
)

# Node-type hints that START an execution (webhook / schedule / manual / form /
# chat / any *Trigger). Used by both the precision gate (P2) and the dry-run
# gate (pinned data must sit on the trigger).
TRIGGER_NODE_HINTS = ("trigger", "webhook", "schedule", "chat")

# Node-type keywords that make an external network call (HTTP/API/provider).
# Used by the precision gate's C1 resilience warning (retryOnFail expected).
NETWORK_NODE_KEYWORDS = (
    "httprequest", "httprequesttool", "sendemail", "telegram", "slack",
    "discord", "gmail", "twilio", "whatsapp", "instagram", "facebook",
    "tiktok", "youtube", "twitter", "notion", "airtable", "sheets", "openai",
    "anthropic", "stripe", "github", "hubspot", "salesforce", "zendesk",
    "mysql", "postgres", "mongodb", "redis", "s3", "googledrive",
    "googlecalendar", "asana", "jira", "linear", "trello", "clickup",
    "monday", "mailchimp",
)

# Node-type keywords whose operation is a side-effect write (create/update/
# delete/append/send). Used by the precision gate's C2 idempotency warning
# (writes must consume a dedup key so redeliveries do not duplicate effects).
WRITE_NODE_KEYWORDS = (
    "create", "update", "upsert", "insert", "append", "delete", "write",
    "send",
)

# Idempotency/dedup signal names commonly available on webhook triggers.
IDEMPOTENCY_HINTS = (
    "idempotency", "dedup", "dedupe", "webhook-id", "request-id", "event-id",
    "executionId", "execution_id",
)

# Webhook integrity signals (Package D): HMAC signature verification + timestamp
# freshness / replay protection. Expected on webhooks that trigger writes —
# without a sender signature the endpoint cannot prove who called it, and
# without a freshness check a captured signed payload is replayable.
HMAC_SIGNATURE_SIGNALS = (
    "hmac", "createhmac", "x-hub-signature", "x-signature", "stripe-signature",
    "sha256=", "signature",
)
TIMESTAMP_FRESHNESS_SIGNALS = (
    "timestamp", "x-timestamp", "skew", "replay", "tolerance", "date.now",
)

# OWASP Agentic AI Top 10 2026 (AA0x) — used by the audit log (Package G) to map
# every gate violation onto the industry-standard agentic-security taxonomy so
# compliance reports can be generated from a single audit artifact.
OWASP_AA0X = {
    "AA01": ("Prompt Injection",
             ("prompt injection", "prompt_injection", "prompt-injection", "injection")),
    "AA02": ("Improper Output Handling",
             ("output handling", "output validation", "llm output", "llm_controlled")),
    "AA03": ("Insecure Agent Communication",
             ("agent communication", "insecure agent", "agent comm", "tool_scope")),
    "AA04": ("Inadequate Access Control",
             ("access control", "webhook_no_auth", "no auth", "unauth", "credential",
              "authentication")),
    "AA05": ("Sensitive Information Disclosure",
             ("secret", "sensitive", "disclosure", "api key", "token")),
    "AA06": ("Improper Input Validation",
             ("input validation", "ssrf", "metadata", "injection")),
    "AA07": ("Unsafe Data & System Usage",
             ("unsafe", "system usage", "data usage", "destructive")),
    "AA08": ("Insecure Memory & State Management",
             ("memory", "state management", "agent memory")),
    "AA09": ("Unbounded Autonomy",
             ("unbounded", "autonomy", "iteration", "ceiling", "oversight",
              "approval", "scope")),
    "AA10": ("Agent Spoofing",
             ("spoof", "impersonat", "forged", "forgery")),
}


def _map_owasp_aa0x(stages: dict) -> dict:
    """Map every gate violation onto the OWASP Agentic AI Top 10 2026 (AA0x)
    taxonomy. Returns {code: {"title": str, "findings": [str]}} keyed only by the
    codes actually matched, ready to embed in the audit JSON + tiered_pipeline
    audit_log_entry call (Package G)."""
    mapped: dict = {}
    for stage_name, stage in (stages or {}).items():
        for v in (stage.get("violations") or []):
            if not isinstance(v, str):
                continue
            vl = v.lower()
            for code, (title, kws) in OWASP_AA0X.items():
                if any(k in vl for k in kws):
                    finding = f"{stage_name}: {v}"
                    if finding not in mapped.setdefault(code, {"title": title, "findings": []})["findings"]:
                        mapped[code]["findings"].append(finding)
    return mapped


def _is_network_calling(node_type: str) -> bool:
    t = (node_type or "").lower()
    return any(k in t for k in NETWORK_NODE_KEYWORDS)


def _is_write_operation(node_type: str, params: dict) -> bool:
    """Heuristic: does this node perform a side-effecting write?

    n8n signals the write nature via either the node TYPE (sendEmail,
    googleSheets) or the operation param (create/update/upsert/insert/
    append/delete/send). Read-only ops (get/list/read) never count.
    """
    t = (node_type or "").lower()
    op = str((params or {}).get("operation", "")).lower()
    type_signal = any(k in t for k in WRITE_NODE_KEYWORDS)
    op_signal = op and any(k in op for k in WRITE_NODE_KEYWORDS)
    if op_signal:
        return True
    if not type_signal:
        return False
    # type signals write (e.g. sendEmail); an explicit read-only op vetoes it
    read_only = any(k in op for k in ("get", "list", "read", "search", "fetch"))
    return not read_only


def _build_incoming_map(connections) -> tuple[dict, list]:
    """Walk an n8n connections object in BOTH legacy and 2.x shape:
      {src: {"main": [edge, edge, ...]}}          # legacy: one output group
      {src: {"main": [ [edge,...], [edge,...] ]}} # 2.x: index i = branch i
    Returns (incoming: {target_node: [src,...]}, dangling: [(src, out_idx),...]).
    Branch groups (IF true/false, Switch) live at different indices of "main".
    Empty output arrays = dangling branches. A missing/empty connections object
    returns ({}, []) — callers treat that as 'no information', never FAIL."""
    incoming: dict = {}
    dangling: list = []
    if not isinstance(connections, dict) or not connections:
        return incoming, dangling
    for src, groups in connections.items():
        main = groups.get("main") if isinstance(groups, dict) else None
        if not isinstance(main, list):
            continue
        for out_idx, group in enumerate(main):
            if not isinstance(group, list):
                group = [group] if isinstance(group, dict) else []
            if not group:
                dangling.append((src, out_idx))
                continue
            for e in group:
                if isinstance(e, dict) and e.get("node"):
                    incoming.setdefault(e["node"], []).append(src)
    return incoming, dangling


def _is_trigger_node(node_type: str) -> bool:
    t = (node_type or "").lower()
    return (any(h in t for h in TRIGGER_NODE_HINTS)
            or t.endswith(".form"))


def _extract_node_refs(text: str) -> list[str]:
    """Every node name referenced by n8n expression syntax:
    $node.Name, $node['Name'], $node["Name"], $('Name'), $nodes.Name.
    Non-node expressions ($json[...], $input, $now, ...) are ignored."""
    refs = []
    for m in re.finditer(r"\$node\s*(?:\.|\[[\"'])\s*([A-Za-z0-9_\- ]+)", text):
        refs.append(m.group(1).strip())
    for m in re.finditer(r"\$\(\s*[\"']([A-Za-z0-9_\- ]+)[\"']\s*\)", text):
        refs.append(m.group(1).strip())
    for m in re.finditer(r"\$nodes\.([A-Za-z0-9_]+)", text):
        refs.append(m.group(1).strip())
    return [r for r in refs if r]


def _is_agent_node(node_type: str) -> bool:
    """LLM-agent-maturity target (Package E): the AGENT CONTAINER node that
    orchestrates a model + tools + memory (n8n-nodes-langchain.agent and
    similar). Deliberately NOT the broad langchain/openai substring test —
    model/tool/memory sub-nodes (n8n-nodes-langchain.openAi, .toolCode, ...)
    are parts wired to the container, not agents themselves."""
    t = (node_type or "").lower()
    return t.endswith(".agent") or t in {"n8n-nodes-langchain.agent"}


def _connected_to(connections, node_name: str, out_key: str) -> list[str]:
    """Target node names wired to a specific connection output of a node
    (e.g. the `ai_languageModel` / `ai_tool` outputs of an n8n agent node).
    Accepts both legacy and 2.x shapes: {out_key: [edge, ...]} or
    {out_key: [[edge,...],...]}. Returns [] when there is no information."""
    out = []
    if not isinstance(connections, dict):
        return out
    node_out = connections.get(node_name)
    if not isinstance(node_out, dict):
        return out
    group = node_out.get(out_key)
    if isinstance(group, list):
        for edge in group:
            if isinstance(edge, dict):
                if edge.get("node"):
                    out.append(edge["node"])
            elif isinstance(edge, list):
                for sub in edge:
                    if isinstance(sub, dict) and sub.get("node"):
                        out.append(sub["node"])
    return out


def _load_artifact(path: str) -> tuple[Any, str]:
    p = Path(path)
    if not p.exists():
        raise SystemExit(f"artifact not found: {path}")
    text = p.read_text(encoding="utf-8", errors="replace")
    if p.suffix.lower() == ".json":
        try:
            return json.loads(text), text
        except json.JSONDecodeError as e:
            return {"_parse_error": str(e)}, text
    return text, text


def _extract_gates_section(artifact: Any) -> dict:
    """Optional `_gates` annotation block on any artifact:
      _gates:
        math: {answer: "...", expected: "..."}              # math-verify grade
        z3:   {vars: {...}, assertions: [ "...", ... ]}     # prove-by-model
        counting: {answer: 149}                              # boundary answer check
        vote:  {candidates: [{answer: "..."}, ...], key: "answer"}
        expected_result: "..."                               # textual parity
    """
    if isinstance(artifact, dict):
        gates = artifact.get("_gates") or {}
        return gates if isinstance(gates, dict) else {}
    return {}


class MathLogicGate:
    """Deterministic math/logic verification (formal-math-logic-verification-
    engine). Verdicts: PASS / FAIL / SKIP / NEEDS_REVIEW."""

    def run(self, gates: dict, full_text: str) -> dict:
        checks = []
        failed = []
        needs_review = False

        if gates.get("math") and _HAS_MV:
            m = gates["math"]
            try:
                ok = mv_verify(parse(str(m.get("expected", ""))), parse(str(m.get("answer", ""))))
            except Exception:
                ok = False
            checks.append({"gate": "math_verify", "ok": ok, "detail": m})
            if not ok:
                failed.append(f"math-verify: answer {m.get('answer')!r} != expected {m.get('expected')!r}")
        elif gates.get("math") and not _HAS_MV:
            needs_review = True
            checks.append({"gate": "math_verify", "ok": False, "detail": "engine missing"})
            failed.append("math-verify engine not installed — cannot grade mechanically")

        if gates.get("z3") and _HAS_Z3:
            z = gates["z3"]
            solver = z3.Solver()
            env = {}
            for name, domain in (z.get("vars") or {}).items():
                if isinstance(domain, int):
                    env[name] = z3.Int(name)
                else:
                    env[name] = z3.Real(name)
            for a in z.get("assertions", []):
                try:
                    solver.add(eval(a, {"__builtins__": {}}, env))  # noqa: S307 — trusted local annotations
                except Exception as e:
                    failed.append(f"z3 assertion parse error: {a} ({e})")
            sat = solver.check()
            checks.append({"gate": "z3_sat", "ok": sat == z3.sat, "detail": str(sat)})
            if sat != z3.sat:
                failed.append(f"z3: constraints are {sat} — logic is unsatisfiable")
        elif gates.get("z3") and not _HAS_Z3:
            needs_review = True
            failed.append("z3 engine not installed — cannot verify logic constraints")

        if gates.get("counting"):
            c = gates["counting"]
            answer = c.get("answer")
            # Boundary sanity: report whether N and N±1 are all mechanically
            # distinguishable; without an independent method we require the
            # expected answer (two-method parity) to confirm.
            checks.append({"gate": "boundary_sanity", "ok": True, "detail": {"answer": answer}})
            if "expected" not in c and not gates.get("math"):
                needs_review = True
                checks[-1]["ok"] = False
                failed.append("counting answer present but no independent expected value — "
                              "off-by-one boundary class cannot be ruled out mechanically")

        if gates.get("vote"):
            v = gates["vote"]
            key = v.get("key", "answer")
            candidates = [str(c.get(key, "")).strip() for c in v.get("candidates", [])]
            counts = Counter(candidates)
            top, top_n = counts.most_common(1)[0] if counts else ("", 0)
            total = len(candidates)
            checks.append({"gate": "self_consistency_vote", "ok": top_n > total / 2,
                           "detail": {"votes": dict(counts), "winner": top}})
            if top_n > total / 2:
                pass
            else:
                failed.append(f"self-consistency: no majority among {total} candidates "
                              f"({dict(counts)}) — escalating")
                needs_review = True

        if gates.get("expected_result"):
            er = gates["expected_result"]
            hit = er in full_text
            checks.append({"gate": "expected_text_parity", "ok": hit})
            if not hit:
                failed.append(f"expected result {er!r} not present in artifact")

        status = "FAIL" if failed and not needs_review else (
            "NEEDS_REVIEW" if needs_review else ("PASS" if checks else "SKIP"))
        return {"status": status, "checks": checks, "violations": failed}


class DeepReasoningGate:
    """Encodes the reasoning-skill gates as deterministic checks:
      - algorithmic-math-reasoner: formal restatement + brute-force
        cross-validation are required before a counting answer ships.
      - off-by-one-boundary-guard: counting keywords trigger the boundary scan
        (open/closed intervals, fence-post, period-crossing).
      - test-time-compute-scaling: hard problems need >= 3 parallel
        candidates; fewer means the answer is single-pass (honest label).
      - elite-verifier-delegation: no stronger model connected here, so
        verification falls back to internal deterministic engines.
    Verdicts: PASS / HEURISTIC / NEEDS_REVIEW.
    """

    def run(self, artifact: Any, full_text: str, gates: dict, math_status: str,
            known_patterns: list[str] | None = None) -> dict:
        findings = []
        for pat in (known_patterns or [])[:8]:
            findings.append(f"AVOID previous rejection: {pat}")
        counting_flagged = bool(COUNTING_KEYWORDS.search(full_text))
        has_candidates = bool(gates.get("vote"))
        has_expected = bool(gates.get("math") or gates.get("counting", {}).get("expected"))

        if counting_flagged:
            findings.append("counting/boundary problem detected — boundary scan required")
            if has_expected:
                findings.append("independent expected value present — two-method parity satisfied")
            elif has_candidates:
                findings.append("candidates present — self-consistency vote is the parity method")
            else:
                findings.append("NEEDS_REVIEW: counting problem without independent verification")
        else:
            findings.append("no counting/boundary trigger — off-by-one class not flagged")

        if math_status == "FAIL":
            findings.append("math gate failed — artifact must not ship")

        depth = "multi-candidate" if has_candidates else "single-pass"
        findings.append(f"reasoning depth: {depth}")

        need_review = counting_flagged and not has_expected and not has_candidates
        if math_status == "NEEDS_REVIEW":
            need_review = True
        if need_review:
            return {"status": "NEEDS_REVIEW", "notes": findings}
        if math_status == "FAIL":
            return {"status": "FAIL", "notes": findings}
        return {"status": "HEURISTIC" if counting_flagged else "PASS", "notes": findings}


ERROR_PATTERNS_PATH = ROOT / "memory" / "n8n_error_patterns.json"
ATTEMPTS_STATE_PATH = ROOT / "memory" / "gate_attempts.json"
SCHEMA_CACHE_PATH = ROOT / "memory" / "n8n_schema_cache.json"
MAX_SAME_REASON_REJECTIONS = 2
GATE_TIMEOUT_SECONDS = 60


class ErrorPatternDB:
    """Feature 5 — accumulated error-pattern memory. Every gate rejection is
    appended here (deduped, counted); before the next build the patterns load
    as an 'avoid these errors' list that gets injected into the reasoning
    pass, so repeated failures genuinely decline over time."""

    def __init__(self, path: Path = ERROR_PATTERNS_PATH):
        self.path = Path(path)

    def _load(self) -> list[dict]:
        try:
            if self.path.exists():
                data = json.loads(self.path.read_text(encoding="utf-8"))
                return data if isinstance(data, list) else []
        except (OSError, json.JSONDecodeError):
            pass
        return []

    def _save(self, patterns: list[dict]):
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps(patterns, ensure_ascii=False, indent=2),
                                 encoding="utf-8")
        except OSError:
            pass

    def record(self, gate: str, violation: str):
        if not violation:
            return
        key = re.sub(r"\s+", " ", violation.strip())[:200]
        patterns = self._load()
        for p in patterns:
            if p.get("pattern") == key:
                p["count"] = int(p.get("count", 0)) + 1
                p["last_seen"] = datetime.now(timezone.utc).isoformat()
                break
        else:
            patterns.append({
                "gate": gate, "pattern": key, "count": 1,
                "first_seen": datetime.now(timezone.utc).isoformat(),
                "last_seen": datetime.now(timezone.utc).isoformat(),
            })
        patterns.sort(key=lambda p: -int(p.get("count", 0)))
        self._save(patterns[:100])

    def record_violations(self, result: dict):
        for gate, stage in (result.get("stages") or {}).items():
            for v in (stage.get("violations") or []):
                if isinstance(v, str):
                    self.record(gate, v)

    def avoid_list(self, limit: int = 10) -> list[str]:
        return [p["pattern"] for p in self._load()[:limit]]


class AttemptGuard:
    """Feature 6 — per-gate time/attempt budget. If the SAME rejection reason
    fires more than MAX_SAME_REASON_REJECTIONS times for the same artifact, or
    a gate runs longer than GATE_TIMEOUT_SECONDS, the pipeline STOPS and asks
    the user instead of looping forever."""

    def __init__(self, state_path: Path = ATTEMPTS_STATE_PATH):
        self.state_path = Path(state_path)

    def _load(self) -> dict:
        try:
            if self.state_path.exists():
                data = json.loads(self.state_path.read_text(encoding="utf-8"))
                return data if isinstance(data, dict) else {}
        except (OSError, json.JSONDecodeError):
            pass
        return {}

    def _save(self, state: dict):
        try:
            self.state_path.parent.mkdir(parents=True, exist_ok=True)
            self.state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2),
                                       encoding="utf-8")
        except OSError:
            pass

    def register(self, artifact_id: str, gate: str, reason: str, elapsed: float) -> str:
        """Returns 'STOP' when the loop budget is blown, else 'CONTINUE'."""
        if elapsed > GATE_TIMEOUT_SECONDS:
            return "STOP"
        state = self._load()
        entry = state.setdefault(artifact_id, {})
        reason = re.sub(r"\s+", " ", reason.strip())[:120]
        key = f"{gate}::{reason}"
        entry[key] = int(entry.get(key, 0)) + 1
        state[artifact_id] = {k: v for k, v in entry.items()}
        self._save(state)
        return "STOP" if entry[key] > MAX_SAME_REASON_REJECTIONS else "CONTINUE"


class SchemaPreflightGate:
    """Feature 1 — zero gate BEFORE generation: validates every node against a
    real schema cache (fetched from the n8n API or a saved cache file) instead
    of memory. A node type/field that is not in the live schema is a hard
    FAIL before any workflow ships."""

    def run(self, workflow: dict, schema_cache: dict | None = None) -> dict:
        violations = []
        if not schema_cache:
            violations.append("no schema cache present — run n8n-schema-preflight "
                              "first (fetch node schemas from the n8n API)")
            return {"status": "NEEDS_REVIEW", "violations": violations, "checked": 0}

        nodes = workflow.get("nodes", [])
        node_types = {n.get("type") for n in nodes if n.get("type")}
        unknown = [t for t in sorted(node_types) if t not in schema_cache]
        for t in unknown:
            violations.append(f"node type '{t}' not found in live schema cache")
        # required-parameter check against cached schemas
        for n in nodes:
            ntype = n.get("type")
            req = (schema_cache.get(ntype) or {}).get("required", [])
            params = (n.get("parameters") or {})
            missing = [r for r in req if r not in params and not any(
                r in str(k) for k in params)]
            if missing:
                violations.append(f"node '{n.get('name')}' ({ntype}) missing required "
                                  f"parameter(s): {', '.join(missing)}")
        return {"status": "FAIL" if violations else "PASS",
                "violations": violations, "checked": len(nodes)}


class DryRunGate:
    """Feature 3 — real trial-execution evidence BEFORE human review: a build
    is only eligible for HITL/deployment when it carries dry-run evidence
    (pinned data for offline runs, or an expected_result parity from a real
    trial run). Without it the gate stops: 'code looks fine' is not 'code
    returns the expected result'."""

    def run(self, workflow: dict, gates: dict) -> dict:
        violations = []
        nodes = workflow.get("nodes", [])
        if not nodes:
            return {"status": "SKIP", "violations": [], "dry_run": None}

        dry = gates.get("dry_run") or {}
        expected = dry.get("expected_result")
        full_text = json.dumps(workflow, default=str)
        has_expected_parity = bool(expected) and str(expected) in full_text

        triggers = [n for n in nodes if _is_trigger_node(n.get("type") or "")]
        if triggers:
            # Trial evidence must sit on the TRIGGER (the node that actually
            # starts the run) — pinned data buried mid-graph proves nothing.
            has_pinned = any((n.get("parameters") or {}).get("pinnedData")
                             for n in triggers)
        else:
            # No trigger (offline mock / subworkflow): any pinned node counts.
            has_pinned = any((n.get("parameters") or {}).get("pinnedData")
                             for n in nodes)

        if not has_pinned and not has_expected_parity:
            violations.append("no dry-run evidence: nodes carry no pinned data and no "
                              "expected_result from a trial run — run the workflow on the "
                              "n8n instance (n8n-pinned-data-mocking) before delivery")
            return {"status": "FAIL", "violations": violations,
                    "dry_run": {"pinned": has_pinned, "expected_parity": has_expected_parity}}

        return {"status": "PASS", "violations": violations,
                "dry_run": {"pinned": has_pinned, "expected_parity": has_expected_parity}}


class N8nPrecisionGate:
    """Stage 3.4 PRECISION — n8n runtime-precision structural gate. Encodes the
    invariants the n8n runtime enforces at deploy/run time that static
    syntax/quality checks miss:

      P1  node names must be unique                       (n8n requires it)
      P2  a workflow needs >= 1 trigger node              (subworkflows:
                                                           _gates.subworkflow)
      P3  every node needs a valid typeVersion (int >= 1)
      P4  every $node[...] / $('...') / $nodes.X expression reference must
          resolve to an existing node name (dangling refs = runtime error)
      P5  app-like nodes must bind a real credential; httpRequest may declare
          authentication: none explicitly; placeholder credential names are
          rejected.
      A1  dead/unreachable nodes: any non-trigger node with ZERO incoming
          edges (clearly orphaned) when a connections graph exists
      A2  dangling branches: IF/Switch/etc output branch (main array index)
          with no wired edge — the payload on that branch silently drops
      A3  Respond to Webhook node present but NO Webhook trigger node —
          n8n raises 'Webhook node not found' at runtime

    Warning channel (non-blocking; status stays PASS but `warnings` is
    returned so the reporter/audit can surface best-practice gaps that a real
    execution would flag as flakiness or silent drift):
      B1  bare `$json` on a node with >1 incoming edge (silently rebinds to the
          wrong upstream — require explicit $('Node') refs)
      B2  Set node consumed by <=1 downstream node (inline indirection)
      B3  Code node that is a pure identity/passthrough (.map/.filter/.find
          returning upstream unchanged) — should be an expression
      C1  network-calling node without retryOnFail (transient 429/5xx turns a
          stable workflow flaky)
      C2  write side-effect node but workflow has no idempotency/dedup signal
          (webhook redelivery duplicates the effect)

    Package D (webhook integrity):
      D1  FAIL — write-triggering Webhook trigger(s) with no authentication
          (missing or 'none') = an open endpoint anyone can fire
      D2  WARNING — webhook-triggered writes but no HMAC signature-verification
          signal (createHmac / x-hub-signature / x-signature) — the sender is
          not proven
      D3  WARNING — signature signal present but no timestamp-freshness /
          replay-protection check — a captured signed request stays replayable

    Package E (LLM agent maturity):
      E1  FAIL — an LLM agent node (langchain/openAI/agent family) with no
          language-model node wired to its ai_languageModel output — the agent
          has nothing to reason with
      E2  WARNING — an LLM agent node with no system prompt (systemMessage /
          text empty) — undefined behavior, prompt-injection surface
      E3  WARNING — an LLM agent node with no maxIterations bound — unbounded
          autonomy / runaway-cost risk
      E4  WARNING — an LLM agent node wiring ai_tool outputs whose target node
          names do not exist in the workflow — dangling tool refs = runtime error

    Package F (generic linting):
      F1  WARNING — an HTTP Request node whose URL is a bare literal with no
          {{expression}} and no credential/auth — a hardcoded endpoint that
          ignores instance config
      F2  WARNING — a webhook path that is empty or a placeholder (your-,
          replace, <...>, xxx, changeme) — indistinguishable endpoint
      F3  WARNING — a Code node containing console.log / print() debug residue
          (spurious output in execution logs)
      F4  WARNING — a Code node containing TODO/FIXME/HACK markers — unfinished
          logic shipped into a deployable workflow
      F5  WARNING — a node using an insecure http:// (non-TLS) URL literal —
          credentials/data ride plaintext if this is ever reached

    Verdicts: PASS / FAIL / SKIP (empty workflow). Structural, never
    overridable — mirrors INTEGRITY (automation-known-issues-compass,
    n8n-schema-guardrail, n8n-credential-security-guard)."""

    def run(self, workflow: dict, gates: dict) -> dict:
        nodes = workflow.get("nodes", [])
        if not nodes:
            return {"status": "SKIP", "violations": [], "checked": 0}
        violations = []
        names = [n.get("name") for n in nodes]

        # P1 — unique node names (n8n rejects duplicate names at save/deploy).
        dups = sorted({name for name in names if name and names.count(name) > 1})
        for d in dups:
            violations.append(f"P1: duplicate node name '{d}' — n8n requires unique node names")

        # P2 — at least one trigger (subworkflows may opt out via _gates).
        if not (gates or {}).get("subworkflow"):
            if not any(_is_trigger_node(n.get("type") or "") for n in nodes):
                violations.append("P2: workflow has no trigger node (webhook / schedule / "
                                  "manual / form / chat) — add one or set _gates.subworkflow: true")

        # P3 — valid typeVersion on every node.
        for n in nodes:
            tv = n.get("typeVersion")
            if not isinstance(tv, int) or tv < 1:
                violations.append(f"P3: node '{n.get('name')}' typeVersion {tv!r} is not a "
                                  f"positive integer")

        # P4 — every expression node reference must resolve to a real node.
        known = set(names)
        for n in nodes:
            text = json.dumps(n.get("parameters") or {}, default=str)
            for ref in _extract_node_refs(text):
                if ref not in known:
                    violations.append(f"P4: node '{n.get('name')}' references '$node['{ref}']' "
                                      f"but no node named '{ref}' exists")

        # P5 — credential binding on app-like nodes.
        for n in nodes:
            ntype = n.get("type") or ""
            creds = n.get("credentials") or {}
            params = n.get("parameters") or {}
            needs = False
            if ntype not in NO_CRED_ALLOWLIST and not _is_trigger_node(ntype) \
                    and ntype not in LLM_AGENT_CONTAINERS:
                if ntype in {"n8n-nodes-base.httpRequest", "n8n-nodes-base.httpRequestTool"}:
                    auth = params.get("authentication")
                    needs = bool(auth) and auth != "none"
                else:
                    needs = True
            if needs:
                if not creds:
                    violations.append(f"P5: node '{n.get('name')}' ({ntype}) requires a "
                                      f"credential but none is bound")
                else:
                    for cred_type, cred in creds.items():
                        if isinstance(cred, dict):
                            name = cred.get("name", "") or cred.get("id", "") or ""
                        else:
                            name = str(cred)
                        if PLACEHOLDER_CRED_RE.search(name):
                            violations.append(f"P5: node '{n.get('name')}' binds placeholder "
                                              f"credential '{name}' — replace with a real credential")

        # ---- Package A: graph integrity (FAIL) ----
        connections = workflow.get("connections")
        incoming, dangling = _build_incoming_map(connections)

        # A1 — dead/unreachable nodes (only meaningful when a graph exists).
        if isinstance(connections, dict) and connections:
            for n in nodes:
                nm = n.get("name")
                if not _is_trigger_node(n.get("type") or "") and nm not in incoming:
                    violations.append(f"A1: node '{nm}' is unreachable — no node connects "
                                      f"into it (orphaned/dead node never executes)")

        # A2 — dangling branches (IF true/false or Switch output with no edge).
        for src, out_idx in dangling:
            violations.append(f"A2: node '{src}' output branch {out_idx} is dangling — no "
                              f"edge wired from it (items on that branch are silently dropped)")

        # A3 — Respond to Webhook node without a Webhook trigger.
        if any((n.get("type") or "") == "n8n-nodes-base.respondToWebhook" for n in nodes):
            if not any((n.get("type") or "") == "n8n-nodes-base.webhook" for n in nodes):
                violations.append("A3: workflow has a 'Respond to Webhook' node but no "
                                  "'Webhook' trigger — n8n raises 'Webhook node not found' "
                                  "at runtime")

        # ---- Package B + C: best-practice warnings (non-blocking) ----
        warnings = []
        downstream_count = {nm: 0 for nm in names}
        for src, edges in (connections or {}).items():
            main = edges.get("main") if isinstance(edges, dict) else None
            if not isinstance(main, list):
                continue
            for group in main:
                if not isinstance(group, list):
                    group = [group] if isinstance(group, dict) else []
                for e in group:
                    if isinstance(e, dict) and e.get("node") in downstream_count:
                        downstream_count[e["node"]] += 1

        full_text = json.dumps(workflow, default=str)
        has_idem = any(h.lower() in full_text.lower() for h in IDEMPOTENCY_HINTS)

        for n in nodes:
            nm = n.get("name")
            ntype = n.get("type") or ""
            params = n.get("parameters") or {}
            text = json.dumps(params, default=str)

            # B1 — bare $json with multiple upstream sources.
            in_degree = len(incoming.get(nm, []))
            if in_degree > 1 and "$json" in text and "$('" not in text and '$node' not in text:
                warnings.append(f"B1: node '{nm}' has {in_degree} incoming edges and uses "
                                f"bare $json — upstream renames silently rebind it; prefer "
                                f"explicit $('NodeName') references")

            # B2 — Set node with <=1 consumer (inline indirection).
            if ntype == "n8n-nodes-base.set" and downstream_count.get(nm, 0) <= 1:
                warnings.append(f"B2: Set node '{nm}' is consumed by "
                                f"{downstream_count.get(nm, 0)} node(s) — inline its fields "
                                f"as expressions instead of an indirection node")

            # B3 — identity/passthrough Code node.
            if ntype in {"n8n-nodes-base.code", "n8n-nodes-base.function"}:
                js = params.get("jsCode") or params.get("functionCode") or ""
                if isinstance(js, str) and re.search(
                        r"return\s+\$input\.(?:all|first|map|filter|find)\(\s*\)", js):
                    warnings.append(f"B3: Code node '{nm}' is a pure passthrough "
                                    f"(returns upstream unchanged) — replace with an "
                                    f"expression / Edit Fields")

            # C1 — network node without retryOnFail.
            if _is_network_calling(ntype) and not n.get("retryOnFail"):
                warnings.append(f"C1: network node '{nm}' ({ntype}) has no retryOnFail — a "
                                f"transient 429/5xx turns a stable workflow flaky; add "
                                f"retryOnFail + retry cap with backoff")

            # C2 — write node but no idempotency/dedup signal anywhere.
            if _is_write_operation(ntype, params) and not has_idem:
                warnings.append(f"C2: write node '{nm}' ({ntype}) but the workflow carries "
                                f"no idempotency/dedup signal — webhook redelivery or a "
                                f"manual re-run duplicates the side effect")

        # ---- Package D: webhook integrity (HMAC signature + timestamp) ----
        # D1 is FAIL (write-triggering webhook with no auth = open endpoint);
        # D2/D3 are best-practice warnings so existing minimal webhook fixtures
        # (headerAuth + write, no signature) still PASS.
        webhook_nodes = [n for n in nodes if (n.get("type") or "") == "n8n-nodes-base.webhook"]
        if webhook_nodes:
            has_write = any(
                _is_write_operation(n.get("type") or "", n.get("parameters") or {})
                for n in nodes
            )
            unauthed = [
                n.get("name")
                for n in webhook_nodes
                if not (n.get("parameters") or {}).get("authentication")
                or (n.get("parameters") or {}).get("authentication") == "none"
            ]
            if unauthed and has_write:
                violations.append(
                    f"D1: webhook(s) {', '.join(sorted(unauthed))} have no authentication "
                    f"but the workflow performs writes — an unauthenticated "
                    f"write-triggering endpoint anyone can fire; bind "
                    f"httpHeaderAuth/query auth or verify an HMAC-signed token"
                )
            if has_write:
                has_sig = any(s in full_text.lower() for s in HMAC_SIGNATURE_SIGNALS)
                if not has_sig:
                    warnings.append(
                        f"D2: webhook-triggered writes but no HMAC signature-verification "
                        f"signal (createHmac / x-hub-signature / x-signature / sha256=) — "
                        f"verify the sender before applying a side effect"
                    )
                elif not any(s in full_text.lower() for s in TIMESTAMP_FRESHNESS_SIGNALS):
                    warnings.append(
                        f"D3: webhook signature present but no timestamp-freshness / "
                        f"replay-protection check (x-timestamp + skew/tolerance) — a "
                        f"captured signed request stays replayable"
                    )

        # ---- Package E: LLM agent maturity (langchain/openAI/agent family) ----
        # E1 FAIL: agent with no language model wired (nothing to reason with).
        # E2-E4 warnings: missing system prompt, unbounded iterations, dangling
        # tool refs. Agent model/tool/memory nodes connect via named outputs
        # (ai_languageModel / ai_tool / ai_memory), not via node parameters.
        known = set(names)
        for n in nodes:
            nm = n.get("name")
            ntype = n.get("type") or ""
            if not _is_agent_node(ntype):
                continue
            params = n.get("parameters") or {}
            options = params.get("options") if isinstance(params.get("options"), dict) else {}
            prompt = (options.get("systemMessage") or params.get("systemMessage")
                      or params.get("text") or "")
            max_iter = options.get("maxIterations", params.get("maxIterations"))
            models = _connected_to(connections, nm, "ai_languageModel")
            if not models:
                violations.append(
                    f"E1: agent node '{nm}' ({ntype}) has no language-model node "
                    f"connected (ai_languageModel output) — the agent has nothing "
                    f"to reason with; wire a model node or it fails at runtime"
                )
            if not str(prompt).strip():
                warnings.append(
                    f"E2: agent node '{nm}' has no system prompt (systemMessage/"
                    f"text empty) — undefined behavior and a prompt-injection "
                    f"surface; define the agent's role and guardrails"
                )
            try:
                max_iter_val = int(max_iter) if max_iter is not None else None
            except (TypeError, ValueError):
                max_iter_val = None
            if max_iter_val is None or max_iter_val <= 0:
                warnings.append(
                    f"E3: agent node '{nm}' has no maxIterations bound — unbounded "
                    f"autonomy / runaway-cost risk; set a small iteration ceiling"
                )
            for tool in _connected_to(connections, nm, "ai_tool"):
                if tool not in known:
                    warnings.append(
                        f"E4: agent node '{nm}' wires ai_tool output to '{tool}' "
                        f"but no node named '{tool}' exists — dangling tool ref, "
                        f"runtime error"
                    )

        # ---- Package F: generic linting (bare URLs, placeholder paths, debug
        # residue, insecure transport). All warnings: style/maintainability
        # drift that should be cleaned but does not block a run. ----
        for n in nodes:
            nm = n.get("name")
            ntype = n.get("type") or ""
            params = n.get("parameters") or {}

            # F1 — HTTP Request node URL is a bare literal (no expression) and
            # the node carries no auth/credential → hardcoded endpoint.
            if ntype in {"n8n-nodes-base.httpRequest",
                         "n8n-nodes-base.httpRequestTool"}:
                url = params.get("url")
                if isinstance(url, str) and "{{" not in url and url.strip():
                    auth = params.get("authentication")
                    has_cred = bool(n.get("credentials")) or (auth and auth != "none")
                    if not has_cred:
                        warnings.append(
                            f"F1: httpRequest node '{nm}' uses a hardcoded URL "
                            f"'{url}' with no {{expression}} and no "
                            f"credential/auth — configuration is frozen into the "
                            f"workflow; prefer instance config / expressions"
                        )

            # F2 — webhook path empty or a placeholder.
            if ntype == "n8n-nodes-base.webhook":
                path = params.get("path")
                if not path or (isinstance(path, str) and PLACEHOLDER_CRED_RE.search(path)):
                    warnings.append(
                        f"F2: webhook node '{nm}' has an empty or placeholder path "
                        f"({path!r}) — an indistinguishable endpoint anyone can guess"
                    )

            # F3 — debug logging residue in Code nodes.
            if ntype in {"n8n-nodes-base.code", "n8n-nodes-base.function"}:
                js = params.get("jsCode") or params.get("functionCode") or ""
                if isinstance(js, str):
                    if re.search(r"\bconsole\.log\s*\(|\bprint\s*\(", js):
                        warnings.append(
                            f"F3: Code node '{nm}' contains console.log/print() "
                            f"debug residue — spurious output in execution logs"
                        )
                    if re.search(r"\b(TODO|FIXME|HACK)\b", js):
                        warnings.append(
                            f"F4: Code node '{nm}' contains TODO/FIXME/HACK markers "
                            f"— unfinished logic shipped into a deployable workflow"
                        )

            # F5 — insecure http:// literal anywhere in the node config.
            text = json.dumps(params, default=str)
            if '"http://' in text:
                warnings.append(
                    f"F5: node '{nm}' ({ntype}) contains an insecure http:// "
                    f"(non-TLS) URL literal — credentials/data ride plaintext "
                    f"if this is ever reached"
                )

        return {"status": "FAIL" if violations else "PASS",
                "violations": violations, "warnings": warnings,
                "checked": len(nodes)}


class StabilityGate:
    """Real live-instance stability verification (n8n_stability_verifier):
    runs the deployed workflow REQUIRED_CONSECUTIVE_PASSES times on the actual
    n8n instance and demands every execution's output to exactly match the
    expected output defined at design time (`_gates.stability` block). A single
    mismatch resets the counter. Opt-in via the annotation:

      _gates:
        stability:
          workflow_id: "abc123"
          test_input: {...}
          expected_output: {...}      # REQUIRED at design time — rule 5
          method: "webhook"           # optional: webhook | cli | (None=legacy REST)

    If the block is absent → SKIP. If present but expected_output missing →
    FAIL (a workflow whose output was never specified cannot be declared
    stable). If N8N_API_KEY is not configured → FAIL fail-closed (unable to
    verify). Distinguishes a FLAT_FAILURE (failed from the first attempt —
    deterministic bug) from a FLAKY failure (reached N consecutive then
    regressed — intermittent bug) as a separate signal in the report."""

    def run(self, gates: dict) -> dict:
        st = gates.get("stability")
        if not isinstance(st, dict) or not st:
            return {"status": "SKIP", "violations": [], "stability": None}

        workflow_id = st.get("workflow_id")
        test_input = st.get("test_input") or {}
        expected_output = st.get("expected_output")

        if not workflow_id:
            return {"status": "FAIL",
                    "violations": ["stability annotation present but no workflow_id"],
                    "stability": None}
        if expected_output is None:
            return {"status": "FAIL",
                    "violations": ["stability annotation present but no expected_output — "
                                   "the expected output MUST be defined at design time (rule 5)"],
                    "stability": None}
        if not N8N_API_KEY:
            return {"status": "FAIL",
                    "violations": [f"N8N_API_KEY not configured — cannot verify stability on "
                                   f"{N8N_BASE_URL} (fail-closed)"],
                    "stability": None}

        result = verify_stability(workflow_id, test_input, expected_output,
                                  method=st.get("method"),
                                  webhook_path=st.get("webhook_path"))
        d = result.to_dict()
        if result.status == "STABLE_VERIFIED":
            return {"status": "PASS",
                    "violations": [f"STABLE_VERIFIED — {REQUIRED_CONSECUTIVE_PASSES} consecutive "
                                   f"real executions matched the expected output"],
                    "stability": d}

        # UNSTABLE_REJECTED: classify FLAT vs FLAKY as a distinct signal.
        if result.pattern == "FLAT_FAILURE":
            msg = (f"FLAT_FAILURE — never reached a single success (deterministic bug, "
                   f"max consecutive={result.max_consecutive_reached}/"
                   f"{REQUIRED_CONSECUTIVE_PASSES}, attempts={len(result.attempts_log)})")
        else:
            msg = (f"FLAKY — reached {result.max_consecutive_reached}/"
                   f"{REQUIRED_CONSECUTIVE_PASSES} consecutive then regressed "
                   f"(intermittent bug, attempts={len(result.attempts_log)})")
        return {"status": "FAIL", "violations": [f"UNSTABLE_REJECTED — {msg}"],
                "stability": d}


def _dag_checks(workflow: dict) -> list[str]:
    """Deterministic DAG closure over connections, reusing
    structural_integrity_check semantics (chain-integrity-checker)."""
    nodes = workflow.get("nodes", [])
    connections = workflow.get("connections", {})
    violations = []
    node_names = {n.get("name") for n in nodes}

    incoming: dict[str, list[str]] = {name: [] for name in node_names}
    for src, outs in connections.items():
        if src not in node_names:
            violations.append(f"connection source '{src}' is not a node")
            continue
        for group in outs.get("main", []):
            dst = group.get("node") if isinstance(group, dict) else None
            if dst is None:
                continue
            if dst not in node_names:
                violations.append(f"step depends on unknown node '{dst}'")
                continue
            incoming.setdefault(dst, []).append(src)

    # Topological order (Kahn) — cycle detection.
    indeg = {n: len(incoming.get(n, [])) for n, _ in ((x.get("name"), x) for x in nodes)}
    order = []
    queue = [n for n, d in indeg.items() if d == 0]
    while queue:
        n = queue.pop(0)
        order.append(n)
        for src, outs in connections.items():
            if src != n:
                continue
            for group in outs.get("main", []):
                dst = group.get("node") if isinstance(group, dict) else None
                if dst and dst in indeg:
                    indeg[dst] -= 1
                    if indeg[dst] == 0:
                        queue.append(dst)
    if len(order) != len(indeg):
        cycle_nodes = [n for n, d in indeg.items() if d > 0]
        violations.append(f"cycle detected among nodes: {sorted(cycle_nodes)}")

    # Per-node structural review in topological order (orphans/dups/self-deps).
    completed: list[dict] = []
    for name in order:
        deps = incoming.get(name, [])
        check = structural_integrity_check(
            [{"id": c} for c in completed], {"id": name, "deps": deps})
        if not check["ok"]:
            violations.append(check["structural_issue"])
        completed.append(name)
    return violations


def run_pipeline(artifact: Any, full_text: str, hitl: bool, reporter,
                 schema_cache: dict | None = None,
                 error_patterns: ErrorPatternDB | None = None,
                 attempt_guard: AttemptGuard | None = None,
                 artifact_id: str | None = None,
                 skills_loaded: set[str] | list[str] | None = None,
                 complaints: ComplaintsRegistry | None = None,
                 resolve_complaints: bool = True) -> dict:
    gates = _extract_gates_section(artifact)
    workflow = artifact if isinstance(artifact, dict) and "nodes" in artifact else {"nodes": []}
    t0 = time.time()
    if artifact_id is None:
        artifact_id = hashlib.sha1(full_text.encode("utf-8", "replace")).hexdigest()[:12]

    def _record_gate(gate_name: str, result: dict, elapsed: float):
        """Per-gate complaints recording (immediate, no network): a SKILL_GAP
        complaint for every rejection whose topic no local skill covers, and a
        SLOW complaint when the gate blew the timeout budget."""
        if complaints is None:
            return
        for v in (result.get("violations") or []):
            if isinstance(v, str):
                complaints.record_skill_gap(gate_name, v)
        complaints.record_slow(gate_name, elapsed, gate_name.lower())

    # ---- Stage 0: SCHEMA PREFLIGHT (zero gate before generation, Feature 1) ----
    s0 = time.time()
    preflight = SchemaPreflightGate().run(workflow, schema_cache)
    reporter.stage("PREFLIGHT", preflight["status"], preflight["violations"], preflight["checked"])
    _record_gate("PREFLIGHT", preflight, time.time() - s0)

    # ---- Stage 1: SECURITY ----
    s1 = time.time()
    sec = SecurityGate(rules_dir=SKILLS_ROOT).evaluate_to_dict(artifact)
    reporter.stage("SECURITY", sec["status"], sec["violations"], sec["risk_score"])
    _record_gate("SECURITY", sec, time.time() - s1)

    # ---- Stage 2: QUALITY ----
    s2 = time.time()
    qual = QualityGate().evaluate_to_dict(workflow)
    reporter.stage("QUALITY", qual["status"], qual["violations"], qual["quality_score"])
    _record_gate("QUALITY", qual, time.time() - s2)

    # ---- Stage 3: INTEGRITY ----
    s3 = time.time()
    dag_violations = _dag_checks(workflow)
    integrity_ok = not dag_violations
    reporter.stage("INTEGRITY", "PASS" if integrity_ok else "FAIL", dag_violations)
    _record_gate("INTEGRITY", {"violations": dag_violations}, time.time() - s3)

    # ---- Stage 3.4: PRECISION (n8n runtime-precision structural gate) ----
    # Runtime invariants n8n enforces at deploy/run that static quality misses:
    # unique node names, a trigger, valid typeVersion, resolvable expression
    # refs, and real credential binding (automation-known-issues-compass).
    s34 = time.time()
    precision = N8nPrecisionGate().run(workflow, gates)
    reporter.stage("PRECISION", precision["status"], precision["violations"],
                   precision["checked"], precision.get("warnings"))
    _record_gate("PRECISION", precision, time.time() - s34)

    # ---- Stage 3.5: SKILLS (mandatory-skill invocation, fail-closed) ----
    # Every gate must PROVE its mandatory router skills are consultable; when a
    # --skills-loaded manifest is provided, it must prove they were ACTUALLY
    # loaded by the agent. Any failure blocks — the gate never continues as if
    # nothing happened (GateSkillInvoker, gate_skill_invoker.py).
    s35 = time.time()
    skill_stage = run_all_mandatory_skills(skills_loaded=skills_loaded)
    reporter.stage("SKILLS", skill_stage["status"], skill_stage["violations"])
    _record_gate("SKILLS", skill_stage, time.time() - s35)

    # ---- Stage 4: STABILITY (real live-instance verification, after QUALITY+INTEGRITY, before HITL) ----
    s4 = time.time()
    stability = StabilityGate().run(gates)
    reporter.stage("STABILITY", stability["status"], stability["violations"])
    _record_gate("STABILITY", stability, time.time() - s4)

    # ---- Stage 5: MATH (new) ----
    s5 = time.time()
    math = MathLogicGate().run(gates, full_text)
    reporter.stage("MATH", math["status"], math["violations"])
    _record_gate("MATH", math, time.time() - s5)

    # ---- Stage 6: REASONING (new) — inject accumulated error patterns (Feature 5) ----
    s6 = time.time()
    avoid = error_patterns.avoid_list() if error_patterns else []
    reason = DeepReasoningGate().run(artifact, full_text, gates, math["status"], known_patterns=avoid)
    reporter.stage("REASONING", reason["status"], reason["notes"])
    _record_gate("REASONING", reason, time.time() - s6)

    # ---- Stage 7: DRY-RUN (real trial-execution evidence before HITL, Feature 3) ----
    s7 = time.time()
    dry_run = DryRunGate().run(workflow, gates)
    reporter.stage("DRY-RUN", dry_run["status"], dry_run["violations"])
    _record_gate("DRY-RUN", dry_run, time.time() - s7)

    # ---- Stage 8: COMPLAINTS — find-skills resolution of every OPEN complaint ----
    # Problems with no local skill (SKILL_GAP) or that took too long (SLOW) are
    # sent to the find-skills gate: search npx skills, auto-install a good hit,
    # else generate a dedicated skill inside the gate's complaints folder.
    complaints_stage = {"status": "NO_COMPLAINTS", "violations": [],
                        "open": 0, "installed": [], "created": [], "no_solution": []}
    if complaints is not None and resolve_complaints:
        res = complaints.resolve_open()
        violations = []
        if res["status"] == "COMPLAINTS_RESOLVED":
            for it in res.get("installed", []):
                violations.append(f"installed skill '{it['spec']}' for {it['gate']} complaint {it['id']}")
            for it in res.get("created", []):
                violations.append(f"created skill at {it['skill_path']} for {it['gate']} complaint {it['id']}")
            for cid in res.get("no_solution", []):
                violations.append(f"complaint {cid}: no installable skill found — retry later")
            if not violations:
                violations = ["no open complaints resolved"]
        complaints_stage = {"status": res["status"], "violations": violations,
                            "open": res.get("processed", 0),
                            "installed": res.get("installed", []),
                            "created": res.get("created", []),
                            "no_solution": res.get("no_solution", [])}
    elif complaints is not None:
        opened = complaints.open_complaints()
        complaints_stage = {"status": "OPEN_COMPLAINTS_PENDING",
                            "violations": [f"{len(opened)} open complaint(s) queued for find-skills "
                                           f"resolution (resolve_complaints=False)"],
                            "open": len(opened), "installed": [], "created": [], "no_solution": []}
    reporter.stage("COMPLAINTS", complaints_stage["status"], complaints_stage["violations"])

    verdict = "READY_FOR_DEPLOYMENT"
    reason_code = ""
    risk = 0

    if preflight["status"] == "FAIL":
        verdict = "SCHEMA_PREFLIGHT_FAILED"
        reason_code = "NODE_OR_FIELD_NOT_IN_LIVE_SCHEMA"
    elif sec["status"] == "REJECTED_SECURITY_RISK":
        # Security is a hard gate — human review is mandatory regardless of
        # dry-run evidence (a real secret/SSRF must be seen by a human first).
        verdict = "PENDING_HUMAN_REVIEW" if hitl else "REJECTED_SECURITY_RISK"
        reason_code = "SECURITY_VIOLATION_REQUIRES_HUMAN"
        risk = sec["risk_score"]
    elif skill_stage["status"] == "FAIL":
        # Mandatory skill(s) for a gate are missing/broken (or, with a manifest,
        # were not actually loaded). The gate MUST refuse — a gate that cannot
        # consult its mandated skills never passes on the quiet. Forced to a
        # fatal risk and routed to human review (mirrors security handling).
        verdict = "PENDING_HUMAN_REVIEW" if hitl else "MANDATORY_SKILL_VIOLATION"
        reason_code = "SKILL_INVOCATION_UNVERIFIED"
        risk = max(risk, 40)
    elif reason["status"] == "NEEDS_REVIEW":
        # Soft path: reasoning uncertainty is arbitrated by real trial
        # evidence. Without dry-run evidence no human-review request is made —
        # go collect pinned data / a trial result first (Feature 3).
        if dry_run["status"] == "FAIL":
            verdict = "DRY_RUN_EVIDENCE_MISSING"
            reason_code = "RUN_TRIAL_EXECUTION_FIRST"
        else:
            verdict = "PENDING_HUMAN_REVIEW" if hitl else "HEURISTIC_APPROVED"
            reason_code = "REASONING_REVIEW_REQUIRED"
            risk = max(risk, 20)
    elif math["status"] == "FAIL":
        verdict = "MATH_VIOLATION"
        reason_code = "MATH_VERIFICATION_FAILED"
    elif not integrity_ok:
        verdict = "CHAIN_INTEGRITY_VIOLATION"
        reason_code = "DAG_STRUCTURAL_VIOLATION"
    elif precision["status"] == "FAIL":
        # n8n runtime-precision violation: unique names / trigger / typeVersion
        # / resolvable refs / real credentials. Hard stop like INTEGRITY.
        verdict = "N8N_PRECISION_VIOLATION"
        reason_code = "RUNTIME_STRUCTURAL_INCONSISTENCY"
    elif stability["status"] == "FAIL":
        # A real live-instance stability failure (or unverifiable because the
        # expected output / API key is missing) is a hard stop — a workflow
        # that does not reproduce its expected output must not ship.
        verdict = "STABILITY_VIOLATION"
        reason_code = "UNSTABLE_OR_UNVERIFIED"
        risk = max(risk, 40)
    elif qual["status"] == "REJECTED":
        verdict = "QUALITY_VIOLATION"
        reason_code = "QUALITY_BELOW_THRESHOLD"
    elif dry_run["status"] == "FAIL":
        # Otherwise-clean build still must carry trial evidence (pinned data or
        # an expected_result from a real run) before it is deployable (Feature 3).
        verdict = "DRY_RUN_EVIDENCE_MISSING"
        reason_code = "RUN_TRIAL_EXECUTION_FIRST"

    # Attempt guard (Feature 6): same reason rejected too many times or timeout -> STOP
    if attempt_guard and verdict != "READY_FOR_DEPLOYMENT":
        primary = next((v for v in (sec["violations"] or reason["notes"]) if isinstance(v, str)), "rejected")
        if attempt_guard.register(artifact_id, reason_code, primary, time.time() - t0) == "STOP":
            verdict = "LOOP_STOP_REQUIRES_USER"
            reason_code = "REPEATED_SAME_REASON_OR_TIMEOUT"

    # Accumulate error patterns on any rejection (Feature 5)
    if error_patterns and verdict != "READY_FOR_DEPLOYMENT":
        error_patterns.record_violations({
            "stages": {
                "preflight": preflight, "security": sec, "quality": qual,
                "integrity": {"status": "PASS" if integrity_ok else "FAIL",
                              "violations": dag_violations},
                "precision": precision,
                "stability": stability, "math": math, "reasoning": reason, "dry_run": dry_run,
            }
        })

    hitl_request = None
    if verdict == "PENDING_HUMAN_REVIEW":
        gate = HITLGate(db_path=DEFAULT_DB_PATH, timeout_minutes=HITL_TIMEOUT_MINUTES)
        if sec["status"] == "REJECTED_SECURITY_RISK":
            violations = sec["violations"]
        elif skill_stage["status"] == "FAIL":
            violations = skill_stage["violations"]
        else:
            violations = reason["notes"]
        req = gate.create_pending(
            raw_input=full_text[:4000],
            risk_score=risk,
            violations=violations,
            payload={"verdict": verdict, "reason_code": reason_code,
                     "security": sec, "quality": qual, "math": math, "reasoning": reason,
                     "skills": skill_stage, "preflight": preflight, "stability": stability,
                     "precision": precision, "dry_run": dry_run},
        )
        hitl_request = {"request_id": req.request_id, "expires_at": req.expires_at}
        reporter.stage("HITL", "PENDING_APPROVAL",
                       [f"request {req.request_id} expires {req.expires_at}"])

    result = {
        "artifact": str(getattr(artifact, "path", "")),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "verdict": verdict,
        "reason_code": reason_code,
        "stages": {
            "preflight": preflight,
            "security": sec, "quality": qual,
            "integrity": {"status": "PASS" if integrity_ok else "FAIL",
                          "violations": dag_violations},
            "precision": precision,
            "skills": skill_stage,
            "stability": stability,
            "math": math, "reasoning": reason, "dry_run": dry_run,
            "complaints": complaints_stage,
        },
        "hitl_request": hitl_request,
        # audit-exposed skill-invocation evidence (verifiable in the report)
        "mandatory_skills_invoked": skill_stage.get("invoked", []),
        "skill_invocation_status": skill_stage["status"],
        "skill_manifest_provided": skill_stage.get("manifest_provided", False),
    }
    # Package G — OWASP Agentic AI Top 10 2026 mapping for compliance/audit.
    result["owasp_aa0x"] = _map_owasp_aa0x(result["stages"])
    return result


class _Reporter:
    def __init__(self, json_out: bool = False):
        self.json_out = json_out

    def stage(self, name: str, status: str, violations: list[str], score=None,
              warnings: list[str] | None = None):
        if self.json_out:
            return
        score_txt = f" [{score}]" if score is not None else ""
        print(f"  [{name:10s}] {status}{score_txt}")
        for v in (violations or [])[:12]:
            print(f"      - {v}")
        if violations and len(violations) > 12:
            print(f"      ... and {len(violations) - 12} more")
        for w in (warnings or [])[:8]:
            print(f"      ! {w}")
        if warnings and len(warnings) > 8:
            print(f"      ... and {len(warnings) - 8} more warnings")


def _persist_audit(result: dict, full_text: str):
    try:
        AUDITS_DIR.mkdir(parents=True, exist_ok=True)
        ts = result["timestamp"].replace(":", "-")
        (AUDITS_DIR / f"{ts}.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
    except OSError:
        pass
    try:
        from tiered_pipeline import audit_log_entry
        ok = result["verdict"] == "READY_FOR_DEPLOYMENT"
        audit_log_entry(
            raw_input=full_text[:2000],
            classification="workflow_verification",
            triager_confidence=0.95,
            execution_result={"verdict": result["verdict"], "reason": result["reason_code"],
                              "owasp_aa0x": result.get("owasp_aa0x") or {}},
            verification_status="passed" if ok else "failed",
            verification_score=1.0 if ok else 0.0,
            escalation_decision="approved" if ok else (
                "escalated" if result["verdict"] == "PENDING_HUMAN_REVIEW" else "rejected"),
            escalation_reason=result["reason_code"],
        )
    except Exception:
        pass


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Build Gates Pipeline")
    ap.add_argument("artifact", nargs="?", help="path to workflow JSON / script / annotated artifact")
    ap.add_argument("--no-hitl", action="store_true", help="no human approval — verdict only")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--schema-cache", metavar="PATH", default=None,
                    help="n8n schema cache JSON (default: memory/n8n_schema_cache.json if it exists)")
    ap.add_argument("--no-patterns", action="store_true",
                    help="disable accumulated error-pattern memory (ErrorPatternDB)")
    ap.add_argument("--no-attempt-guard", action="store_true",
                    help="disable per-artifact loop/attempt guard (AttemptGuard)")
    ap.add_argument("--no-complaints", action="store_true",
                    help="disable the per-gate complaints sections (ComplaintsRegistry)")
    ap.add_argument("--no-resolve", action="store_true",
                    help="record complaints but do NOT resolve them via find-skills "
                         "(no npx skills search/install)")
    ap.add_argument("--skills-loaded", metavar="PATH", default=None,
                    help="JSON manifest of the skills the agent ACTUALLY loaded via the "
                         "skill tool during this build (list, or {'skills_loaded': [...]}). "
                         "When provided, every mandatory gate skill must appear in it, "
                         "else the gate BLOCKS (SKILL_INVOCATION_UNVERIFIED).")
    ap.add_argument("--approve", nargs=2, metavar=("REQUEST_ID", "TOKEN"))
    ap.add_argument("--reject", nargs=2, metavar=("REQUEST_ID", "REASON"))
    args = ap.parse_args(argv)

    if args.approve:
        gate = HITLGate(db_path=DEFAULT_DB_PATH)
        res = gate.approve(*args.approve)
        print(json.dumps(res, ensure_ascii=False))
        return 0 if res.get("status") == "OVERRIDE_APPROVED" else 1

    if args.reject:
        gate = HITLGate(db_path=DEFAULT_DB_PATH)
        res = gate.reject(*args.reject)
        print(json.dumps(res, ensure_ascii=False))
        return 0 if res.get("status") == "HARD_REJECT" else 1

    if not args.artifact:
        ap.error("artifact path required (or --approve/--reject)")

    artifact, full_text = _load_artifact(args.artifact)
    if isinstance(artifact, dict) and "_parse_error" in artifact:
        print("INVALID_JSON: cannot run gates safely")
        return 1

    if not args.json:
        print(f"Build Gates Pipeline — {Path(args.artifact).name}")
        print("=" * 60)

    # Feature 1: schema cache (explicit --schema-cache or the default cache file).
    schema_cache = None
    cache_path = Path(args.schema_cache) if args.schema_cache else SCHEMA_CACHE_PATH
    if cache_path.exists():
        try:
            schema_cache = json.loads(cache_path.read_text(encoding="utf-8"))
            if not isinstance(schema_cache, dict):
                schema_cache = None
        except (OSError, json.JSONDecodeError):
            schema_cache = None
    if schema_cache:
        print(f"[SCHEMA] cache loaded: {cache_path} ({len(schema_cache)} node types)")

    # Features 5 & 6: persistent error-pattern memory + loop guard, on by default.
    error_patterns = None if args.no_patterns else ErrorPatternDB()
    attempt_guard = None if args.no_attempt_guard else AttemptGuard()

    # Complaints sections: per-gate skill-gap/slow ledger + find-skills
    # resolution (record always unless disabled; resolve unless --no-resolve).
    complaints = None if args.no_complaints else ComplaintsRegistry()
    resolve_complaints = not args.no_resolve

    # GateSkillInvoker: manifest of skills the agent actually loaded (if any).
    skills_loaded = None
    if args.skills_loaded:
        skills_path = Path(args.skills_loaded)
        if not skills_path.is_file():
            print(f"[SKILLS] ERROR: --skills-loaded manifest not found: {skills_path}")
            return 1
        try:
            data = json.loads(skills_path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                skills_loaded = {str(s).strip() for s in data}
            elif isinstance(data, dict):
                skills_loaded = {str(s).strip() for s in (data.get("skills_loaded") or [])}
            else:
                print("[SKILLS] ERROR: manifest must be a JSON list or {skills_loaded: [...]}")
                return 1
        except (OSError, json.JSONDecodeError) as e:
            print(f"[SKILLS] ERROR: cannot read --skills-loaded manifest: {e}")
            return 1
        print(f"[SKILLS] manifest loaded: {len(skills_loaded)} skills — "
              f"every mandatory gate skill must be in it")

    reporter = _Reporter(json_out=args.json)
    result = run_pipeline(artifact, full_text, hitl=not args.no_hitl, reporter=reporter,
                          schema_cache=schema_cache,
                          error_patterns=error_patterns,
                          attempt_guard=attempt_guard,
                          artifact_id=Path(args.artifact).name,
                          skills_loaded=skills_loaded,
                          complaints=complaints,
                          resolve_complaints=resolve_complaints)
    _persist_audit(result, full_text)

    if not args.json:
        print("=" * 60)
        print(f"VERDICT: {result['verdict']}" + (f" — {result['reason_code']}" if result["reason_code"] else ""))
        if result.get("hitl_request"):
            print(f"  pending request: {result['hitl_request']['request_id']} (expires {result['hitl_request']['expires_at']})")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["verdict"] == "READY_FOR_DEPLOYMENT" else 1


if __name__ == "__main__":
    sys.exit(main())
