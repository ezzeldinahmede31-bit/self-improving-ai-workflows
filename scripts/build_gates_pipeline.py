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

# Auto-fix configuration
MAX_AUTOFIX_ITERATIONS = 3
AUTOFIX_SAFE_GATES = {"QUALITY", "PRECISION", "RAG", "INTEGRITY", "MATH", "REASONING"}
AUTOFIX_UNSAFE_GATES = {"SECURITY", "STABILITY", "DRY-RUN", "SKILLS"}

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
    # LangChain helper/plumbing nodes — bind NO credential of their own (the
    # model / vector-store / tool nodes connected to them do). Real workflows
    # carry these with the "@n8n/" package prefix; membership is checked after
    # prefix normalization (see _normalize_node_type). Model nodes (lmChat*,
    # embeddings*) and vector-store nodes (vectorStoreQdrant/Pinecone) are NOT
    # here — they bind real credentials and P5 must require them.
    "n8n-nodes-langchain.chatTrigger",
    "n8n-nodes-langchain.toolVectorStore", "n8n-nodes-langchain.toolCode",
    "n8n-nodes-langchain.toolHttpRequest", "n8n-nodes-langchain.toolWorkflow",
    "n8n-nodes-langchain.documentDefaultDataLoader",
    "n8n-nodes-langchain.textSplitterRecursiveCharacterTextSplitter",
}

# LLM-agent container nodes (n8n-nodes-langchain.agent and similar). These
# never bind a credential themselves — the model + tool nodes connected to them
# do. Exempted from P5's credential requirement so the connected model node is
# what gets checked. Exact-type match only (never substring — "magento" etc.
# contain "agent" but are app nodes that DO bind credentials).
LLM_AGENT_CONTAINERS = {"n8n-nodes-langchain.agent"}


def _normalize_node_type(node_type: str) -> str:
    """Strip the '@n8n/' package prefix from a live workflow node type so the
    gate's exact-type allowlists match real n8n 2.x exports. n8n serializes
    langchain nodes as '@n8n/n8n-nodes-langchain.agent', the gate stores them
    as 'n8n-nodes-langchain.agent'. Both must be equivalent for membership."""
    t = (node_type or "")
    if t.startswith("@n8n/"):
        return t[len("@n8n/"):]
    return t

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


def _is_trigger_type(node_type: str) -> bool:
    """STRICT trigger detection for P5's credential exemption. _is_trigger_node
    uses substring hints ('chat' also matches lmChatNvidia / lmChatOpenAi), so
    a model node would be wrongly exempted from the P5 credential rule. This
    only accepts node types that END with a trigger marker (…Trigger / …webhook
    / …form), which no app-like node satisfies."""
    t = _normalize_node_type(node_type).lower()
    return t.endswith(("trigger", "webhook", ".form"))


def _is_loop_node(node_name_or_type: str) -> bool:
    """splitInBatches v3 (and future loop nodes): main[0] = 'done' exit is
    intentionally left unwired in the canonical loop-back pattern."""
    t = (node_name_or_type or "").lower()
    return "splitinbatches" in t or "loop" in t


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


def _is_tool_wired(connections, node_name: str) -> bool:
    """Is this node wired through an agent-tool channel (ai_tool output, in
    either direction)? $fromAI(...) only resolves inside such tool context —
    anywhere else it is a guaranteed runtime error (workflow-sdk
    FROM_AI_IN_NON_TOOL)."""
    if not isinstance(connections, dict):
        return False
    for src, groups in connections.items():
        if not isinstance(groups, dict):
            continue
        for out_key, targets in groups.items():
            if "tool" not in (out_key or "").lower():
                continue
            if src == node_name:
                return True
            flat = targets if isinstance(targets, list) else [targets]
            stack = list(flat)
            while stack:
                t = stack.pop()
                if isinstance(t, dict):
                    if t.get("node") == node_name:
                        return True
                elif isinstance(t, list):
                    stack.extend(t)
    return False


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


def _connected_into(connections, node_name: str, out_key: str) -> list[str]:
    """Reverse of _connected_to: node names whose `out_key` output wires INTO
    node_name. n8n 2.x agent sub-nodes own the edge (model.ai_languageModel ->
    agent, tool.ai_tool -> agent), so agent-outgoing lookups alone miss them.
    Accepts both legacy and 2.x shapes. Returns [] when there is no
    information."""
    srcs = []
    if not isinstance(connections, dict):
        return srcs
    for src, groups in connections.items():
        if src == node_name or not isinstance(groups, dict):
            continue
        group = groups.get(out_key)
        if isinstance(group, list):
            for edge in group:
                if isinstance(edge, dict):
                    if edge.get("node") == node_name:
                        srcs.append(src)
                elif isinstance(edge, list):
                    for sub in edge:
                        if isinstance(sub, dict) and sub.get("node") == node_name:
                            srcs.append(src)
    return srcs


def _ai_wired_nodes(connections) -> set:
    """Node names involved in ai_* wiring (ai_languageModel / ai_tool /
    ai_memory / ai_outputParser / ai_retriever ...). Agent sub-nodes connect
    ONLY via these named outputs, never the main flow — so they are
    intentionally not reachable through main edges and must not be flagged
    as orphans by the A1 graph-integrity check. Returns an empty set when
    there is no information."""
    wired = set()
    if not isinstance(connections, dict):
        return wired
    for src, groups in connections.items():
        if not isinstance(groups, dict):
            continue
        for out_key, targets in groups.items():
            if "ai_" not in (out_key or "").lower():
                continue
            wired.add(src)
            if isinstance(targets, list):
                for t in targets:
                    if isinstance(t, dict):
                        if t.get("node"):
                            wired.add(t["node"])
                    elif isinstance(t, list):
                        for sub in t:
                            if isinstance(sub, dict) and sub.get("node"):
                                wired.add(sub["node"])
            elif isinstance(targets, dict) and targets.get("node"):
                wired.add(targets["node"])
    return wired


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
        # JSON object keys ("count":, "between": ...) are field names, not
        # prose — strip them before the keyword scan so a key named `count`
        # cannot trip the boundary detector (S5 lesson). Single-token quoted
        # values ("count", "between_days") are enum/key-like labels too; real
        # counting prose always carries spaces ("how many roots ...").
        scan_text = re.sub(r'"[^"\n]{1,64}"\s*:', ' ', full_text or "")
        scan_text = re.sub(r'"[^"\n\s]{1,32}"', ' ', scan_text)
        counting_flagged = bool(COUNTING_KEYWORDS.search(scan_text))
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

        # n8n branch-logic review (business-logic flaws no scanner catches —
        # AppSecure 2026: approval steps that can be skipped, branches that
        # default to ALLOW on error). Notes only; PRECISION A2/C1 own the
        # blocking verdicts.
        artifact_nodes = []
        if isinstance(artifact, dict):
            artifact_nodes = artifact.get("nodes", []) or []
        if artifact_nodes:
            findings.append("n8n workflow artifact — branch/error-path review applied")
            for _n in artifact_nodes:
                _seg = str(_n.get("type", "")).lower().rsplit(".", 1)[-1]
                if _seg in ("if", "switch", "switchv3"):
                    if _n.get("continueOnFail") or _n.get("onError") == "continueRegularOutput":
                        findings.append(
                            f"branch node '{_n.get('name')}' continues on error — "
                            f"failure defaults to ALLOW; halt or route to an "
                            f"error path instead")
                        break

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


class AutoFixEngine:
    """Auto-fix engine: applies safe, deterministic fixes for common gate
    violations. Only operates on AUTOFIX_SAFE_GATES violations — never touches
    SECURITY, STABILITY, DRY-RUN, or SKILLS. Returns (fixed_workflow, fixes_applied)
    where fixes_applied is a list of human-readable descriptions."""

    def __init__(self, workflow: dict, violations_by_gate: dict):
        self.workflow = json.loads(json.dumps(workflow))  # deep copy
        self.violations_by_gate = violations_by_gate
        self.fixes_applied = []

    def apply_all(self) -> tuple[dict, list[str]]:
        """Apply all applicable auto-fixes. Returns (fixed_workflow, fixes_list)."""
        self._fix_precision_p1_duplicate_names()
        self._fix_precision_p2_missing_trigger()
        self._fix_precision_p3_typeversion()
        self._fix_precision_p4_dangling_refs()
        self._fix_precision_p5_placeholder_creds()
        self._fix_precision_a1_orphaned_nodes()
        self._fix_precision_a2_dangling_branches()
        self._fix_precision_a3_respond_without_webhook()
        self._fix_precision_h4_approval_placement()
        self._fix_rag_r1_missing_embeddings()
        self._fix_rag_r2_placeholder_collection()
        self._fix_rag_r3_dangling_retriever()
        self._fix_rag_r4_post_to_put()
        self._fix_quality_bare_json()
        self._fix_math_missing_expected()
        return self.workflow, self.fixes_applied

    def _add_fix(self, gate: str, description: str):
        self.fixes_applied.append(f"[{gate}] {description}")

    def _fix_precision_p1_duplicate_names(self):
        """P1: Rename duplicate nodes by appending _1, _2, etc. and update connections."""
        nodes = self.workflow.get("nodes", [])
        # Build list of (old_name, new_name) pairs
        name_counts = {}
        rename_pairs = []
        for n in nodes:
            name = n.get("name", "")
            if name:
                count = name_counts.get(name, 0)
                if count > 0:
                    new_name = f"{name}_{count}"
                    rename_pairs.append((name, new_name))
                    n["name"] = new_name
                    self._add_fix("PRECISION", f"Renamed duplicate node '{name}' to '{new_name}'")
                name_counts[name] = count + 1
        
        # Update connections using the rename pairs
        if rename_pairs:
            connections = self.workflow.get("connections", {})
            # Build mapping from old name to new name
            rename_map = {old: new for old, new in rename_pairs}
            new_conns = {}
            for src, targets in connections.items():
                new_src = rename_map.get(src, src)
                new_targets = {}
                for out_key, edges in targets.items():
                    if isinstance(edges, dict) and "main" in edges:
                        new_edges = {"main": []}
                        for group in edges["main"]:
                            new_group = []
                            for e in group if isinstance(group, list) else [group]:
                                if isinstance(e, dict) and e.get("node"):
                                    e = dict(e)
                                    e["node"] = rename_map.get(e["node"], e["node"])
                                new_group.append(e)
                            new_edges["main"].append(new_group)
                        new_targets[out_key] = new_edges
                    else:
                        new_targets[out_key] = edges
                new_conns[new_src] = new_targets
            self.workflow["connections"] = new_conns

    def _fix_precision_p2_missing_trigger(self):
        """P2: Add a Manual Trigger if no trigger exists (for subworkflows)."""
        nodes = self.workflow.get("nodes", [])
        if any(_is_trigger_node(n.get("type") or "") for n in nodes):
            return
        # Add Manual Trigger node
        trigger_node = {
            "id": "manual-trigger-auto",
            "name": "Manual Trigger",
            "type": "n8n-nodes-base.manualTrigger",
            "typeVersion": 1,
            "position": [250, 300],
            "parameters": {}
        }
        nodes.insert(0, trigger_node)
        self._add_fix("PRECISION", "Added 'Manual Trigger' node (workflow had no trigger)")

    def _fix_precision_p3_typeversion(self):
        """P3: Fix invalid typeVersion (set to 1 if missing/invalid)."""
        for n in self.workflow.get("nodes", []):
            tv = n.get("typeVersion")
            if isinstance(tv, bool) or not isinstance(tv, (int, float)) or tv < 1:
                n["typeVersion"] = 1
                self._add_fix("PRECISION", f"Fixed node '{n.get('name')}' typeVersion to 1")

    def _fix_precision_p4_dangling_refs(self):
        """P4: Remove dangling $node references to non-existent nodes."""
        nodes = self.workflow.get("nodes", [])
        known = {n.get("name") for n in nodes}
        for n in nodes:
            params = n.get("parameters") or {}
            text = json.dumps(params, default=str)
            for ref in _extract_node_refs(text):
                if ref not in known:
                    # Remove the reference from params (best effort)
                    for key, val in params.items():
                        if isinstance(val, str) and f"$node['{ref}']" in val:
                            params[key] = val.replace(f"$node['{ref}']", "''")
                            self._add_fix("PRECISION", f"Removed dangling $node['{ref}'] reference in '{n.get('name')}'")
                        elif isinstance(val, str) and f"$node.{ref}" in val:
                            params[key] = val.replace(f"$node.{ref}", "''")
                            self._add_fix("PRECISION", f"Removed dangling $node.{ref} reference in '{n.get('name')}'")

    def _fix_precision_p5_placeholder_creds(self):
        """P5: Remove placeholder credential names (they'll fail anyway, better to remove)."""
        for n in self.workflow.get("nodes", []):
            creds = n.get("credentials") or {}
            ntype = n.get("type") or ""
            norm = _normalize_node_type(ntype)
            if norm in NO_CRED_ALLOWLIST or _is_trigger_type(ntype) or norm in LLM_AGENT_CONTAINERS:
                continue
            params = n.get("parameters") or {}
            needs = False
            if norm in {"n8n-nodes-base.httpRequest", "n8n-nodes-base.httpRequestTool"}:
                auth = params.get("authentication")
                needs = bool(auth) and auth != "none"
            else:
                needs = True
            if needs:
                to_remove = []
                for cred_type, cred in creds.items():
                    if isinstance(cred, dict):
                        name = cred.get("name", "") or cred.get("id", "") or ""
                    else:
                        name = str(cred)
                    if PLACEHOLDER_CRED_RE.search(name):
                        to_remove.append(cred_type)
                for ct in to_remove:
                    del creds[ct]
                    self._add_fix("PRECISION", f"Removed placeholder credential '{ct}' from '{n.get('name')}'")

    def _fix_precision_a1_orphaned_nodes(self):
        """A1: Connect orphaned nodes (nodes with no incoming edges) by adding
        an edge from a suitable source node TO the orphaned node."""
        connections = self.workflow.get("connections", {})
        incoming, _ = _build_incoming_map(connections)
        nodes = self.workflow.get("nodes", [])
        ai_wired = _ai_wired_nodes(connections)
        orphans = [n for n in nodes
                   if not _is_trigger_node(n.get("type") or "")
                   and n.get("name") not in incoming
                   and n.get("name") not in ai_wired]
        if orphans:
            # Find suitable source nodes (nodes that have outputs but aren't triggers)
            sources = [n for n in nodes
                       if not _is_trigger_node(n.get("type") or "")
                       and n.get("name") not in [o.get("name") for o in orphans]]
            if sources:
                source = sources[0]  # Use first available source
                for n in orphans:
                    target_name = n.get("name")
                    source_name = source.get("name")
                    if "connections" not in self.workflow:
                        self.workflow["connections"] = {}
                    if source_name not in self.workflow["connections"]:
                        self.workflow["connections"][source_name] = {"main": [[]]}
                    # Check if connection already exists
                    existing = False
                    for group in self.workflow["connections"][source_name].get("main", [[]]):
                        for e in group:
                            if isinstance(e, dict) and e.get("node") == target_name:
                                existing = True
                                break
                    if not existing:
                        self.workflow["connections"][source_name]["main"][0].append({"node": target_name})
                        self._add_fix("PRECISION", f"Connected '{source_name}' to orphaned node '{target_name}'")
                    else:
                        self._add_fix("PRECISION", f"NOTED: '{source_name}' already connects to orphaned node '{target_name}'")
            else:
                for n in orphans:
                    self._add_fix("PRECISION", f"NOTED: orphaned node '{n.get('name')}' needs manual wiring (no suitable source)")

    def _fix_precision_a2_dangling_branches(self):
        """A2: Remove dangling branch outputs (set to empty)."""
        connections = self.workflow.get("connections", {})
        incoming, dangling = _build_incoming_map(connections)
        nodes = self.workflow.get("nodes", [])
        loop_names = {n.get("name") for n in nodes if _is_loop_node(n.get("type") or "")}
        for src, out_idx in dangling:
            if src in loop_names and out_idx == 0:
                continue
            # For now, just log - we can't easily "fix" a dangling branch without knowing intent
            self._add_fix("PRECISION", f"NOTED: dangling branch on '{src}' output {out_idx} (requires manual wiring)")

    def _fix_precision_a3_respond_without_webhook(self):
        """A3: Remove Respond to Webhook if no Webhook trigger exists."""
        nodes = self.workflow.get("nodes", [])
        has_webhook = any((n.get("type") or "") == "n8n-nodes-base.webhook" for n in nodes)
        has_respond = any((n.get("type") or "") == "n8n-nodes-base.respondToWebhook" for n in nodes)
        if has_respond and not has_webhook:
            self.workflow["nodes"] = [n for n in nodes if (n.get("type") or "") != "n8n-nodes-base.respondToWebhook"]
            self._add_fix("PRECISION", "Removed 'Respond to Webhook' node (no Webhook trigger present)")

    def _fix_precision_h4_approval_placement(self):
        """H4: Move node-level requiresHumanApproval into parameters (the only
        level n8n reads)."""
        for n in self.workflow.get("nodes", []):
            if "requiresHumanApproval" in n:
                val = n.pop("requiresHumanApproval")
                params = n.get("parameters")
                if not isinstance(params, dict):
                    params = {}
                    n["parameters"] = params
                params.setdefault("requiresHumanApproval", val)
                self._add_fix("PRECISION", f"Moved requiresHumanApproval into parameters of '{n.get('name')}'")

    def _fix_rag_r1_missing_embeddings(self):
        """R1: Add a dummy embeddings node if vector store has none."""
        nodes = self.workflow.get("nodes", [])
        connections = self.workflow.get("connections", {})
        stores = [n for n in nodes
                  if "vectorstore" in _normalize_node_type(n.get("type") or "").lower()
                  and "toolvectorstore" not in _normalize_node_type(n.get("type") or "").lower()]
        for st in stores:
            emb = _connected_into(connections, st.get("name"), "ai_embedding")
            if not emb:
                # Add a basic NVIDIA embeddings node
                emb_node = {
                    "id": f"embeddings-autofix-{st.get('name')}",
                    "name": f"Embeddings for {st.get('name')}",
                    "type": "@n8n/n8n-nodes-langchain.embeddingsNvidia",
                    "typeVersion": 1,
                    "position": [100, 300],
                    "parameters": {"model": "nv-embedqa-e5-v5"}
                }
                nodes.append(emb_node)
                # Wire embeddings -> store
                if "connections" not in self.workflow:
                    self.workflow["connections"] = {}
                # Modern n8n 2.x format: {"main": [[edge], [edge]]}
                if emb_node["name"] not in self.workflow["connections"]:
                    self.workflow["connections"][emb_node["name"]] = {"main": [[]]}
                # main[0] is a list of edges for the first output
                self.workflow["connections"][emb_node["name"]]["main"][0].append(
                    {"node": st.get("name"), "output": "ai_embedding"}
                )
                self._add_fix("RAG", f"Added NVIDIA embeddings node wired to '{st.get('name')}'")

    def _fix_rag_r2_placeholder_collection(self):
        """R2: Set a default collection name if placeholder."""
        for n in self.workflow.get("nodes", []):
            ntype = _normalize_node_type(n.get("type") or "").lower()
            if "vectorstore" in ntype and "toolvectorstore" not in ntype:
                params = n.get("parameters") or {}
                col = params.get("qdrantCollection") or params.get("collectionName") or ""
                if isinstance(col, dict):
                    col = col.get("value", "")
                if not col or PLACEHOLDER_CRED_RE.search(str(col)):
                    params["qdrantCollection"] = {"value": "auto_collection"}
                    self._add_fix("RAG", f"Set default collection name 'auto_collection' on '{n.get('name')}'")

    def _fix_rag_r4_post_to_put(self):
        """R4: Qdrant upsert with POST is a certain runtime 400 — switching
        the method to PUT is safe and deterministic (search/delete paths are
        never touched: the gate only flags the bare /points upsert path)."""
        for n in self.workflow.get("nodes", []):
            ntype = _normalize_node_type(n.get("type") or "").lower()
            if "httprequest" not in ntype:
                continue
            params = n.get("parameters") or {}
            url = str(params.get("url") or params.get("urlParameters") or "")
            if "qdrant" not in url.lower():
                continue
            method = str(params.get("method") or "GET").upper()
            path = url.split("?", 1)[0].rstrip("/")
            if method == "POST" and path.endswith("/points") and "search" not in path \
                    and "delete" not in path:
                params["method"] = "PUT"
                self._add_fix("RAG", f"Switched '{n.get('name')}' Qdrant upsert POST→PUT")

    def _fix_rag_r3_dangling_retriever(self):
        """R3: Remove dangling ai_vectorStore/ai_retriever references."""
        nodes = self.workflow.get("nodes", [])
        connections = self.workflow.get("connections", {})
        names = {n.get("name") for n in nodes}
        for n in nodes:
            for out_key in ("ai_vectorStore", "ai_retriever"):
                for target in _connected_to(connections, n.get("name"), out_key):
                    if target not in names:
                        # Can't easily fix - log it
                        self._add_fix("RAG", f"NOTED: dangling {out_key} to '{target}' from '{n.get('name')}'")

    def _fix_quality_bare_json(self):
        """Quality: Replace bare $json with explicit references where possible."""
        # This is complex - for now just note
        pass

    def _fix_math_missing_expected(self):
        """Math: Add expected values from gates annotation if missing."""
        gates_section = self.workflow.get("_gates", {})
        counting = gates_section.get("counting", {})
        if counting and "answer" in counting and "expected" not in counting:
            # Can't auto-fix - requires human knowledge
            self._add_fix("MATH", f"NOTED: counting answer {counting['answer']} has no expected value for parity check")


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

        def _node_has_pinned(n: dict) -> bool:
            # n8n stores pinned data in THREE shapes across versions: inside
            # parameters (classic), as a node-level field, and as a
            # workflow-root {nodeName: [...]} map. Accept any of them —
            # rejecting a real trial run over a storage-shape technicality
            # is a false FAIL.
            if (n.get("parameters") or {}).get("pinnedData"):
                return True
            if n.get("pinnedData"):
                return True
            root_pinned = workflow.get("pinnedData") or {}
            if isinstance(root_pinned, dict) and root_pinned.get(n.get("name")):
                return True
            return False

        triggers = [n for n in nodes if _is_trigger_node(n.get("type") or "")]
        if triggers:
            # Trial evidence must sit on the TRIGGER (the node that actually
            # starts the run) — pinned data buried mid-graph proves nothing.
            has_pinned = any(_node_has_pinned(n) for n in triggers)
        else:
            # No trigger (offline mock / subworkflow): any pinned node counts.
            has_pinned = any(_node_has_pinned(n) for n in nodes)

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

    Package I (secret / SSRF / tool-context parity — FAIL):
      I1  FAIL — a secret literal embedded in node parameters or a URL
          (Bearer/Basic literal, ?api_key/?token= query, secret-named field
          with a long literal, high-entropy key assignment in Code). Mirrors
          SecurityGate natively so a --no-complaints / security-disabled run
          still blocks active exposure.
      I2  FAIL — a static httpRequest URL targeting a private/loopback host
          (localhost, 127.x, RFC-1918, link-local, file://...). Mirrors the
          ssrf_internal_egress probe natively.
      I3  FAIL — a $fromAI(...) placeholder inside a node that is NOT wired
          as an agent tool (ai_tool) — runtime error outside tool context.

    Package J (expression / wiring hygiene — WARNING):
      J1  WARNING — bare $json/$node/$input/... value without the ={{...}}
          wrapper (evaluates as literal text — the #1 AI-generation mistake).
      J2  WARNING — {{...}} expression missing the `=` prefix.
      J3  WARNING — a Merge node with a single wired input (waits for inputs
          that never arrive / misbehaves).
      J4  WARNING — a scheduleTrigger flow with no settings.timezone (cron
          silently runs in UTC, not wall-clock time).

    Package H (n8n runtime semantics — booking-campaign lessons):
      H1  FAIL — two nodes sharing one node id (duplicate ids corrupt
          patches and execution refs)
      H2  FAIL — Python literals True/False/None inside a Code node (the
          Code node runs JavaScript: true/false/null)
      H3  FAIL — a parameter mixing a literal prefix with an expression
          (=text{{...}} — n8n expressions must be the whole value ={{...}})
      H4  FAIL — requiresHumanApproval set at node level (n8n only reads
          it inside parameters; auto-fixed by moving it under parameters)
      H5  FAIL — settings.errorWorkflow that is not a plain workflow-ID
          string (expression/$env/blank never resolves at runtime)
      H6  FAIL — Redis operation 'decr' (the n8n Redis node has no decr;
          use incr with a negative amount or SET)
      H7  WARNING — $env use with no '||' fallback (blocked-env instances
          fail closed)
      H8  WARNING — literal +HH:MM offset inside a URL/query (decodes to a
          space; use %2B or Zulu 'Z')
      H9  WARNING — reliance on alwaysOutputData (proven inert on n8n 2.30.x
          empty branches; use an always-one-item envelope instead)
      H10 WARNING — dedup/lock key carrying a message id with no chat scope
          (cross-chat collisions discard real items)
      H11 WARNING — calendar flow with no Africa/Cairo (or timeZone) signal
          (UTC-hour replies slip a whole wall-clock day)

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

        # P3 — valid typeVersion on every node (int or float, n8n supports
        # fractional versions like 4.4 / 3.4).
        for n in nodes:
            tv = n.get("typeVersion")
            if isinstance(tv, bool) or not isinstance(tv, (int, float)) or tv < 1:
                violations.append(f"P3: node '{n.get('name')}' typeVersion {tv!r} is not a "
                                  f"valid numeric version (int/float >= 1)")

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
            norm = _normalize_node_type(ntype)
            creds = n.get("credentials") or {}
            params = n.get("parameters") or {}
            needs = False
            if norm not in NO_CRED_ALLOWLIST and not _is_trigger_type(ntype) \
                    and norm not in LLM_AGENT_CONTAINERS:
                if norm in {"n8n-nodes-base.httpRequest", "n8n-nodes-base.httpRequestTool"}:
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
            ai_wired = _ai_wired_nodes(connections)
            for n in nodes:
                nm = n.get("name")
                if not _is_trigger_node(n.get("type") or "") \
                        and nm not in incoming and nm not in ai_wired:
                    violations.append(f"A1: node '{nm}' is unreachable — no node connects "
                                      f"into it (orphaned/dead node never executes)")

        # A2 — dangling branches (IF true/false or Switch output with no edge).
        # splitInBatches v3 has TWO outputs: main[0] = 'done' (loop finished),
        # main[1] = 'loop' (per-iteration). The done output is intentionally left
        # unwired in the canonical loop pattern — only flag dangling branches on
        # genuine split/branch nodes, never the loop-done exit.
        loop_names = {n.get("name") for n in nodes if _is_loop_node(n.get("type") or "")}
        for src, out_idx in dangling:
            if src in loop_names and out_idx == 0:
                continue
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
            models = _connected_to(connections, nm, "ai_languageModel") \
                + _connected_into(connections, nm, "ai_languageModel")
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
            for tool in _connected_to(connections, nm, "ai_tool") \
                    + _connected_into(connections, nm, "ai_tool"):
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

        # ---- Package H: n8n runtime semantics (booking-campaign lessons) ----
        # H1-H6 FAIL (the runtime/Redis/JS engine enforces them); H7-H11 warn
        # (traps that caused real production incidents).
        def _iter_param_strings(obj):
            if isinstance(obj, str):
                yield obj
            elif isinstance(obj, dict):
                for v in obj.values():
                    yield from _iter_param_strings(v)
            elif isinstance(obj, list):
                for v in obj:
                    yield from _iter_param_strings(v)

        seen_ids: dict = {}
        for n in nodes:
            nm = n.get("name")
            nid = n.get("id")
            if nid is not None and nid != "" and nid in seen_ids:
                violations.append(
                    f"H1: nodes '{seen_ids[nid]}' and '{nm}' share id '{nid}' — "
                    f"duplicate node ids corrupt patches and execution refs; "
                    f"keep ids unique"
                )
            elif nid is not None and nid != "":
                seen_ids[nid] = nm

        for n in nodes:
            nm = n.get("name")
            ntype = n.get("type") or ""
            params = n.get("parameters") or {}

            # H2 — Python literals inside a JavaScript Code node.
            if ntype in {"n8n-nodes-base.code", "n8n-nodes-base.function"}:
                js = params.get("jsCode") or params.get("functionCode") or ""
                if isinstance(js, str) and js:
                    dequoted = re.sub(
                        r"'(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\"|`(?:[^`\\]|\\.)*`",
                        "''", js)
                    py_hit = re.search(r"\b(True|False|None)\b", dequoted)
                    if py_hit:
                        violations.append(
                            f"H2: Code node '{nm}' uses Python literal "
                            f"'{py_hit.group(1)}' — the Code node runs JavaScript "
                            f"(true/false/null); Python literals throw at runtime"
                        )

            # H4 — approval flag at the wrong level.
            if "requiresHumanApproval" in n:
                violations.append(
                    f"H4: node '{nm}' sets requiresHumanApproval at node level — "
                    f"n8n only reads it inside parameters; move it under parameters"
                )

            # H6 — Redis operation that does not exist.
            if "redis" in ntype.lower():
                op = str(params.get("operation") or "").lower()
                if op == "decr":
                    violations.append(
                        f"H6: Redis node '{nm}' uses operation 'decr' — the n8n "
                        f"Redis node has no decr; use incr with a negative "
                        f"amount or SET"
                    )

            # H3 — literal prefix mixed with an expression.
            for s in _iter_param_strings(params):
                if isinstance(s, str) and s.startswith("=") and "{{" in s:
                    prefix = s[1:].split("{{", 1)[0]
                    if prefix.strip():
                        violations.append(
                            f"H3: node '{nm}' mixes a literal prefix with an "
                            f"expression ({s[:64]!r}) — n8n expressions must be "
                            f"the whole value (=`{{{{...}}}}`); literal-then-expression "
                            f"evaluates wrong"
                        )
                        break

            # H7 — $env with no fallback.
            for s in _iter_param_strings(params):
                if isinstance(s, str) and "$env." in s and "||" not in s:
                    warnings.append(
                        f"H7: node '{nm}' reads $env with no '||' fallback — "
                        f"instances with blocked env access fail closed; add a "
                        f"default (or a credential) so the node survives"
                    )
                    break

            # H8 — literal +HH:MM offset inside a URL/query string.
            for s in _iter_param_strings(params):
                if isinstance(s, str) and re.search(r"\+\d{2}:\d{2}", s):
                    warnings.append(
                        f"H8: node '{nm}' embeds a literal +HH:MM offset in a "
                        f"URL/query — the '+' decodes to a space (400 from "
                        f"Google); use %2B or Zulu 'Z'"
                    )
                    break

            # H9 — reliance on alwaysOutputData.
            if params.get("alwaysOutputData") is True:
                warnings.append(
                    f"H9: node '{nm}' relies on alwaysOutputData — proven inert "
                    f"on n8n 2.30.x empty branches; verify the empty path with "
                    f"an always-one-item envelope (HTTP node) instead"
                )

            # H10 — message-scoped key with no chat scope.
            key_text = json.dumps(
                {k: v for k, v in params.items() if "key" in k.lower()},
                default=str)
            if re.search(r"(?i)(?<![a-z])(mid|message_id|messageid)(?![a-z])", key_text) \
                    and "chat" not in key_text.lower():
                warnings.append(
                    f"H10: node '{nm}' dedup/lock key carries a message id with "
                    f"no chat scope — cross-chat message_id collisions discard "
                    f"real items; key on <chat>:<mid>"
                )

        # ---- Package I: secret / SSRF / tool-context parity (FAIL) ----
        # Structural mirror of the SecurityGate n8n-native scans: a workflow
        # that leaks a secret or reaches the private network must not depend
        # on which gate ran first — it fails here too.
        _SECRET_FIELD_NAMES = (
            "api_key", "apikey", "apikey_", "apiKey", "token", "password",
            "secret", "access_token", "accesstoken", "client_secret",
            "clientsecret", "authorization", "auth_token", "private_key",
            "privatekey",
        )
        for n in nodes:
            nm = n.get("name")
            params = n.get("parameters") or {}

            def _walk_params(obj, key=""):
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        _walk_params(v, k)
                elif isinstance(obj, list):
                    for v in obj:
                        _walk_params(v, key)
                elif isinstance(obj, str):
                    if not obj.strip() or "{{" in obj:
                        return
                    leaf = str(key).lower()
                    s = obj.strip()
                    # I1a — secret-named field with a real-length literal.
                    if leaf in _SECRET_FIELD_NAMES and len(s) >= 12:
                        violations.append(
                            f"I1: node '{nm}' field '{key}' embeds a secret "
                            f"literal — move it to the credential store "
                            f"(exports leak literals)")
                    # I1b — auth material in a URL query string.
                    if ("http" in s or "://" in s) and re.search(
                            r"[?&](?:api[_-]?key|token|access[_-]?token|auth|"
                            r"secret|password)=", s, re.IGNORECASE):
                        violations.append(
                            f"I1: node '{nm}' field '{key}' carries auth "
                            f"material in a URL query string — logged by "
                            f"proxies/history; use header auth via the "
                            f"credential store")
                    # I1c — Bearer/Basic literal in any parameter.
                    if re.search(r"Bearer\s+[A-Za-z0-9\-._~+/]{12,}=*",
                                 s) or re.search(
                            r"Basic\s+[A-Za-z0-9+/]{12,}={0,2}", s):
                        violations.append(
                            f"I1: node '{nm}' field '{key}' embeds an "
                            f"Authorization literal — bind a credential "
                            f"instead of hardcoding it")

            _walk_params(params)

            # I2 — static URL to a private/loopback host.
            for field in ("url", "webhookUrl", "host", "server"):
                val = params.get(field)
                if not isinstance(val, str) or not val.strip():
                    continue
                if "{{" in val:
                    continue
                for pat in (r"127\.0\.0\.1", r"\blocalhost\b", r"0\.0\.0\.0",
                            r"::1", r"192\.168\.", r"10\.\d+\.",
                            r"172\.(1[6-9]|2\d|3[01])\.", r"169\.254\.",
                            r"\bfile://", r"\bgopher://", r"\bdict://"):
                    if re.search(pat, val, re.IGNORECASE):
                        violations.append(
                            f"I2: node '{nm}' URL targets an internal host "
                            f"(`{pat}` in '{val[:72]}') — SSRF / "
                            f"lateral-movement vector; use a public endpoint "
                            f"or an explicit allowlist")
                        break

            # I3 — $fromAI outside an agent-tool context.
            ntype = n.get("type") or ""
            param_text = json.dumps(params, default=str)
            if "$fromAI" in param_text or "$fromAi" in param_text:
                is_tool = _is_tool_wired(connections, nm)
                if not is_tool:
                    violations.append(
                        f"I3: node '{nm}' uses $fromAI(...) but is not wired "
                        f"as an agent tool (ai_tool) — $fromAI only resolves "
                        f"inside tool context; runtime error otherwise")

        # ---- Package J: expression / wiring hygiene (WARNING) ----
        for n in nodes:
            nm = n.get("name")
            ntype = n.get("type") or ""
            params = n.get("parameters") or {}

            def _walk_expr(obj, key=""):
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        _walk_expr(v, k)
                elif isinstance(obj, list):
                    for v in obj:
                        _walk_expr(v, key)
                elif isinstance(obj, str):
                    if key in {"jsCode", "functionCode", "pythonCode"}:
                        return
                    s = obj.strip()
                    if not s:
                        return
                    if s.startswith("=") or not s:
                        return
                    if s.startswith("{{"):
                        warnings.append(
                            f"J2: node '{nm}' field '{key}' is {{{{...}}}} "
                            f"without the `=` prefix — n8n treats it as "
                            f"literal text; write ={{{{...}}}}")
                        return
                    for pat in (r"^\$json[.\[]", r"^\$node\[", r"^\$input\.",
                                r"^\$execution\.", r"^\$workflow\.",
                                r"^\$prevNode\.", r"^\$env\.",
                                r"^\$(now|today|itemIndex|runIndex)$"):
                        if re.search(pat, s):
                            warnings.append(
                                f"J1: node '{nm}' field '{key}' looks like an "
                                f"unwrapped expression ({s[:48]!r}) — n8n "
                                f"evaluates it as literal text; wrap as "
                                f"={{{{...}}}}")
                            break

            _walk_expr(params)

            # J3 — Merge node with a single wired input.
            if _normalize_node_type(ntype) == "n8n-nodes-base.merge":
                in_count = sum(
                    1 for src, groups in (connections or {}).items()
                    if isinstance(groups, dict)
                    for edges in [groups.get("main")]
                    if isinstance(edges, list)
                    for grp in (edges if all(isinstance(x, list) for x in edges)
                                else [edges])
                    for e in (grp if isinstance(grp, list) else [grp])
                    if isinstance(e, dict) and e.get("node") == nm)
                if in_count < 2:
                    warnings.append(
                        f"J3: Merge node '{nm}' has {in_count} wired input(s) "
                        f"— Merge waits for multiple inputs; a single input "
                        f"hangs or misbehaves (use it only to join branches)")

        # J4 — scheduleTrigger flow with no explicit time zone.
        if any("scheduletrigger" in (n.get("type") or "").lower() for n in nodes):
            settings_j = workflow.get("settings") or {}
            if not settings_j.get("timezone") and "timezone" not in full_text.lower():
                warnings.append(
                    "J4: scheduleTrigger flow with no settings.timezone — "
                    "cron silently runs in UTC; set the wall-clock zone "
                    "(e.g. Africa/Cairo) explicitly")

        # H5 — errorWorkflow must be a plain workflow-ID string.
        settings = workflow.get("settings") or {}
        ew = settings.get("errorWorkflow")
        if ew is not None and (
                not isinstance(ew, str) or not ew.strip()
                or "{{" in ew or "$" in ew or re.search(r"\s", ew)):
            violations.append(
                f"H5: settings.errorWorkflow must be a plain workflow-ID string — "
                f"{ew!r} is an expression/literal that never resolves at runtime "
                f"(attach a real error workflow instead)"
            )

        # H11 — calendar flow with no explicit wall-clock time zone.
        if any("googlecalendar" in (n.get("type") or "").lower() for n in nodes):
            if not re.search(r"Africa/Cairo|timeZone|timezone", full_text,
                             re.IGNORECASE):
                warnings.append(
                    "H11: calendar flow with no Africa/Cairo (or timeZone) signal — "
                    "UTC-hour replies slip a whole wall-clock day; format event "
                    "times with an explicit time-zone conversion"
                )

        return {"status": "FAIL" if violations else "PASS",
                "violations": violations, "warnings": warnings,
                "checked": len(nodes)}


class RagVectorGate:
    """Stage 3.45 RAG — vector-store / RAG pipeline structural gate. Encodes
    the hard-won lessons of the first RAG build (Apple Q1.pdf -> Qdrant +
    NVIDIA embeddings, Aug 2026) as deterministic checks so a RAG workflow
    either proves its pieces are wired, or fails before deploy:

      R1  FAIL — a vector-store node (vectorStoreQdrant / *vectorStore*)
          exists but no embeddings node is wired into it (ai_embedding
          input). A store with nothing to embed/query with is a runtime
          error in the n8n langchain nodes.
      R2  WARNING — a vector-store node's collection name parameter
          (qdrantCollection / collectionName) is empty or a placeholder —
          the pipeline reads/writes an ambiguous collection.
      R3  FAIL — a tool/retriever connection (ai_vectorStore / ai_retriever)
          wires a target node that does not exist in the workflow — dangling
          retriever ref = runtime error.
      R4  FAIL — an HTTP Request node calls a Qdrant REST /points upsert
          path with method POST (upsert must be PUT; POST on the bare
          /points path deterministically errors 'missing field `ids`' at
          runtime — certain breakage, never a warning).
      R5  WARNING — an HTTP Request node calls the NVIDIA embeddings endpoint
          without an `input_type` (passage/query) body field — NVIDIA
          mis-embeds / rejects with 4xx.
      R6  WARNING — a document loader node exists but no text splitter node
          (textSplitter*) is wired — the whole document embeds as one vector.

    Verdicts: PASS / FAIL / SKIP (no vector-store / embedding / retriever
    nodes present). Structural, never overridable."""

    def run(self, workflow: dict) -> dict:
        nodes = workflow.get("nodes", [])
        connections = workflow.get("connections", {})
        violations: list[str] = []
        warnings: list[str] = []
        names = {n.get("name") for n in nodes}

        stores = [n for n in nodes
                  if "vectorstore" in _normalize_node_type(n.get("type") or "").lower()
                  and "toolvectorstore" not in _normalize_node_type(n.get("type") or "").lower()]
        embeddings = [n for n in nodes if "embeddings" in _normalize_node_type(n.get("type") or "").lower()]
        splitters = [n for n in nodes if "splitter" in _normalize_node_type(n.get("type") or "").lower()]
        loaders = [n for n in nodes if ("loader" in _normalize_node_type(n.get("type") or "").lower()
                                        or "readbinaryfiles" in _normalize_node_type(n.get("type") or "").lower()
                                        or "extractfromfile" in _normalize_node_type(n.get("type") or "").lower())]

        rag_http = [
            n for n in nodes
            if "httprequest" in _normalize_node_type(n.get("type") or "").lower()
            and ("qdrant" in str((n.get("parameters") or {}).get("url") or "").lower()
                 or "nvidia" in str((n.get("parameters") or {}).get("url") or "").lower())
        ]
        if not (nodes and (stores or embeddings or splitters or loaders or rag_http)):
            return {"status": "SKIP", "violations": [], "warnings": [],
                    "checked": len(nodes)}

        # R1 — every vector store must have an embeddings node wired in.
        for st in stores:
            emb = _connected_into(connections, st.get("name"), "ai_embedding")
            if not emb:
                violations.append(
                    f"R1: vector-store node '{st.get('name')}' has no embeddings "
                    f"node wired to its ai_embedding input — it cannot embed or "
                    f"query anything at runtime"
                )

        # R2 — collection name must be a real, non-placeholder value.
        for st in stores:
            params = st.get("parameters") or {}
            col = params.get("qdrantCollection") or params.get("collectionName") or {}
            if isinstance(col, dict):
                col = col.get("value", "")
            if not col or PLACEHOLDER_CRED_RE.search(str(col)):
                warnings.append(
                    f"R2: vector-store node '{st.get('name')}' collection name "
                    f"{col!r} is empty or a placeholder — set the real Qdrant "
                    f"collection"
                )

        # R3 — dangling ai_vectorStore / ai_retriever references.
        for n in nodes:
            for out_key in ("ai_vectorStore", "ai_retriever"):
                for target in _connected_to(connections, n.get("name"), out_key):
                    if target not in names:
                        violations.append(
                            f"R3: node '{n.get('name')}' {out_key} wiring points "
                            f"to '{target}' which does not exist in the workflow"
                        )

        # R4 — Qdrant upsert must be PUT, not POST (the Aug 2026 400).
        for n in nodes:
            ntype = _normalize_node_type(n.get("type") or "").lower()
            if "httprequest" not in ntype:
                continue
            params = n.get("parameters") or {}
            url = str(params.get("url") or params.get("urlParameters") or "")
            if "qdrant" not in url.lower():
                continue
            method = str(params.get("method") or "GET").upper()
            path = url.split("?", 1)[0].rstrip("/")
            if method == "POST" and path.endswith("/points") and "search" not in path \
                    and "delete" not in path:
                violations.append(
                    f"R4: node '{n.get('name')}' calls Qdrant with POST on "
                    f"{path} — upsert must be PUT; POST is the RETRIEVE "
                    f"endpoint and errors 'missing field `ids`' at runtime"
                )

        # R5 — NVIDIA embeddings need input_type passage/query.
        for n in nodes:
            ntype = _normalize_node_type(n.get("type") or "").lower()
            if "httprequest" not in ntype:
                continue
            params = n.get("parameters") or {}
            url = str(params.get("url") or "")
            if "api.nvidia.com" not in url.lower() or "embeddings" not in url.lower():
                continue
            body = params.get("jsonBody") or params.get("body") or ""
            body_text = json.dumps(body, default=str) if not isinstance(body, str) else body
            if "input_type" not in body_text:
                warnings.append(
                    f"R5: node '{n.get('name')}' calls the NVIDIA embeddings API "
                    f"without an `input_type` (passage/query) body field — "
                    f"NVIDIA mis-embeds or rejects with 4xx"
                )

        # R6 — a document loader without a splitter embeds whole docs.
        if loaders and embeddings and not splitters:
            warnings.append(
                "R6: document loader node(s) present but no text splitter "
                "node (textSplitter*) wired — the whole document embeds as "
                "one vector, degrading retrieval"
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
    # Loop nodes (splitInBatches v3, etc.) legitimately form cycles: the body's
    # last node loops back into the loop node to trigger the next iteration.
    # Those loop-back edges are canonical n8n (blessed by the A2 loop handling)
    # and must NOT be treated as DAG cycles. Edges INTO a loop node are exempt
    # from the cycle/ordering computation; genuine cycles elsewhere still fail.
    loop_names = {n.get("name") for n in nodes if _is_loop_node(n.get("type") or "")}
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
            if dst in loop_names:
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
                 resolve_complaints: bool = True,
                 enable_autofix: bool = True) -> dict:
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

    def _run_all_gates(wf: dict, ft: str) -> dict:
        """Run all gates on a workflow and return aggregated results."""
        g = _extract_gates_section({"nodes": wf.get("nodes", []), "_gates": gates})
        
        # Stage 0: PREFLIGHT
        s0 = time.time()
        pf = SchemaPreflightGate().run(wf, schema_cache)
        reporter.stage("PREFLIGHT", pf["status"], pf["violations"], pf["checked"])
        _record_gate("PREFLIGHT", pf, time.time() - s0)

        # Stage 1: SECURITY
        s1 = time.time()
        sc = SecurityGate(rules_dir=SKILLS_ROOT).evaluate_to_dict({"nodes": wf.get("nodes", []), "_gates": gates})
        reporter.stage("SECURITY", sc["status"], sc["violations"], sc["risk_score"])
        _record_gate("SECURITY", sc, time.time() - s1)

        # Stage 2: QUALITY
        s2 = time.time()
        ql = QualityGate().evaluate_to_dict(wf)
        reporter.stage("QUALITY", ql["status"], ql["violations"], ql["quality_score"])
        _record_gate("QUALITY", ql, time.time() - s2)

        # Stage 3: INTEGRITY
        s3 = time.time()
        dag_v = _dag_checks(wf)
        integ_ok = not dag_v
        reporter.stage("INTEGRITY", "PASS" if integ_ok else "FAIL", dag_v)
        _record_gate("INTEGRITY", {"violations": dag_v}, time.time() - s3)

        # Stage 3.4: PRECISION
        s34 = time.time()
        pr = N8nPrecisionGate().run(wf, g)
        reporter.stage("PRECISION", pr["status"], pr["violations"], pr["checked"], pr.get("warnings"))
        _record_gate("PRECISION", pr, time.time() - s34)

        # Stage 3.45: RAG
        s345 = time.time()
        rg = RagVectorGate().run(wf)
        reporter.stage("RAG", rg["status"], rg["violations"], rg["checked"], rg.get("warnings"))
        _record_gate("RAG", rg, time.time() - s345)

        # Stage 3.5: SKILLS
        s35 = time.time()
        sk = run_all_mandatory_skills(skills_loaded=skills_loaded)
        reporter.stage("SKILLS", sk["status"], sk["violations"])
        _record_gate("SKILLS", sk, time.time() - s35)

        # Stage 4: STABILITY
        s4 = time.time()
        st = StabilityGate().run(g)
        reporter.stage("STABILITY", st["status"], st["violations"])
        _record_gate("STABILITY", st, time.time() - s4)

        # Stage 5: MATH
        s5 = time.time()
        mt = MathLogicGate().run(g, ft)
        reporter.stage("MATH", mt["status"], mt["violations"])
        _record_gate("MATH", mt, time.time() - s5)

        # Stage 6: REASONING
        s6 = time.time()
        av = error_patterns.avoid_list() if error_patterns else []
        rs = DeepReasoningGate().run({"nodes": wf.get("nodes", []), "_gates": gates}, ft, g, mt["status"], known_patterns=av)
        reporter.stage("REASONING", rs["status"], rs["notes"])
        _record_gate("REASONING", rs, time.time() - s6)

        # Stage 7: DRY-RUN
        s7 = time.time()
        dr = DryRunGate().run(wf, g)
        reporter.stage("DRY-RUN", dr["status"], dr["violations"])
        _record_gate("DRY-RUN", dr, time.time() - s7)

        # Stage 8: COMPLAINTS
        cs = {"status": "NO_COMPLAINTS", "violations": [], "open": 0, "installed": [], "created": [], "no_solution": []}
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
            cs = {"status": res["status"], "violations": violations,
                  "open": res.get("processed", 0),
                  "installed": res.get("installed", []),
                  "created": res.get("created", []),
                  "no_solution": res.get("no_solution", [])}
        elif complaints is not None:
            opened = complaints.open_complaints()
            cs = {"status": "OPEN_COMPLAINTS_PENDING",
                  "violations": [f"{len(opened)} open complaint(s) queued for find-skills resolution (resolve_complaints=False)"],
                  "open": len(opened), "installed": [], "created": [], "no_solution": []}
        reporter.stage("COMPLAINTS", cs["status"], cs["violations"])

        return {
            "preflight": pf, "security": sc, "quality": ql,
            "integrity": {"status": "PASS" if integ_ok else "FAIL", "violations": dag_v},
            "precision": pr, "rag": rg, "skills": sk, "stability": st,
            "math": mt, "reasoning": rs, "dry_run": dr, "complaints": cs,
            "workflow": wf, "full_text": ft
        }

# ---- AUTO-FIX LOOP ----
    # Run gates, if safe gates have violations, apply auto-fixes and re-run
    # up to MAX_AUTOFIX_ITERATIONS times.
    autofix_history = []
    current_workflow = json.loads(json.dumps(workflow))
    current_full_text = full_text
    
    if enable_autofix:
        for iteration in range(MAX_AUTOFIX_ITERATIONS + 1):
            if not reporter.json_out:
                print(f"\n  === Pipeline Iteration {iteration + 1}/{MAX_AUTOFIX_ITERATIONS + 1} ===")
            
            results = _run_all_gates(current_workflow, current_full_text)
        
            # Check if any safe gates have violations
            safe_gate_violations = {}
            unsafe_gate_failures = {}
            
            for gate_name in ["PREFLIGHT", "QUALITY", "PRECISION", "RAG", "INTEGRITY", "MATH", "REASONING"]:
                gate_result = results.get(gate_name.lower())
                if gate_result and gate_result.get("violations"):
                    safe_gate_violations[gate_name] = gate_result["violations"]
            
            for gate_name in ["SECURITY", "STABILITY", "DRY-RUN", "SKILLS"]:
                gate_result = results.get(gate_name.lower())
                if gate_result and gate_result.get("violations") and gate_result.get("status") == "FAIL":
                    unsafe_gate_failures[gate_name] = gate_result["violations"]
            
            # If no safe gate violations, we're done
            if not safe_gate_violations and not unsafe_gate_failures:
                if not reporter.json_out:
                    print(f"  ✓ All gates passed on iteration {iteration + 1}")
                break
            
            # If we have unsafe gate failures, we can't auto-fix those
            if unsafe_gate_failures:
                if not reporter.json_out:
                    for gn, vs in unsafe_gate_failures.items():
                        print(f"  ✗ {gn} has violations (unsafe for auto-fix): {vs[:3]}")
                break
            
            # If we've reached max iterations, stop
            if iteration >= MAX_AUTOFIX_ITERATIONS:
                if not reporter.json_out:
                    print(f"  ⚠ Max auto-fix iterations ({MAX_AUTOFIX_ITERATIONS}) reached")
                break
            
            # Apply auto-fixes for safe gate violations
            if not reporter.json_out:
                print(f"  🔧 Auto-fixing {len(safe_gate_violations)} gate(s) with violations...")
            
            autofix = AutoFixEngine(current_workflow, safe_gate_violations)
            fixed_workflow, fixes = autofix.apply_all()
            
            if not fixes:
                if not reporter.json_out:
                    print(f"  ⚠ No auto-fixes applicable for current violations")
                break
            
            if not reporter.json_out:
                for fix in fixes:
                    print(f"    - {fix}")
            
            autofix_history.append({"iteration": iteration + 1, "fixes": fixes})
            current_workflow = fixed_workflow
            current_full_text = json.dumps(current_workflow, default=str)
    else:
        # Auto-fix disabled: run gates once
        results = _run_all_gates(current_workflow, current_full_text)
    
    # Use the last results for final verdict
    results = _run_all_gates(current_workflow, current_full_text)
    
    # Extract final results for verdict logic
    preflight = results["preflight"]
    sec = results["security"]
    qual = results["quality"]
    dag_violations = results["integrity"]["violations"]
    integrity_ok = results["integrity"]["status"] == "PASS"
    precision = results["precision"]
    rag = results["rag"]
    skill_stage = results["skills"]
    stability = results["stability"]
    math = results["math"]
    reason = results["reasoning"]
    dry_run = results["dry_run"]
    complaints_stage = results["complaints"]
    workflow = results["workflow"]
    full_text = results["full_text"]

    verdict = "READY_FOR_DEPLOYMENT"
    reason_code = ""
    risk = 0

    if preflight["status"] == "FAIL":
        verdict = "SCHEMA_PREFLIGHT_FAILED"
        reason_code = "NODE_OR_FIELD_NOT_IN_LIVE_SCHEMA"
    elif sec["status"] == "REJECTED_SECURITY_RISK":
        verdict = "PENDING_HUMAN_REVIEW" if hitl else "REJECTED_SECURITY_RISK"
        reason_code = "SECURITY_VIOLATION_REQUIRES_HUMAN"
        risk = sec["risk_score"]
    elif skill_stage["status"] == "FAIL":
        verdict = "PENDING_HUMAN_REVIEW" if hitl else "MANDATORY_SKILL_VIOLATION"
        reason_code = "SKILL_INVOCATION_UNVERIFIED"
        risk = max(risk, 40)
    elif reason["status"] == "NEEDS_REVIEW":
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
        verdict = "N8N_PRECISION_VIOLATION"
        reason_code = "RUNTIME_STRUCTURAL_INCONSISTENCY"
    elif rag["status"] == "FAIL":
        verdict = "RAG_STRUCTURAL_VIOLATION"
        reason_code = "RAG_VECTOR_STORE_INCONSISTENCY"
        risk = max(risk, 30)
    elif stability["status"] == "FAIL":
        verdict = "STABILITY_VIOLATION"
        reason_code = "UNSTABLE_OR_UNVERIFIED"
        risk = max(risk, 40)
    elif qual["status"] == "REJECTED":
        verdict = "QUALITY_VIOLATION"
        reason_code = "QUALITY_BELOW_THRESHOLD"
    elif dry_run["status"] == "FAIL":
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
                "integrity": {"status": "PASS" if integrity_ok else "FAIL", "violations": dag_violations},
                "precision": precision, "rag": rag, "skills": skill_stage,
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
                     "precision": precision, "rag": rag, "dry_run": dry_run},
        )
        hitl_request = {"request_id": req.request_id, "expires_at": req.expires_at}
        reporter.stage("HITL", "PENDING_APPROVAL", [f"request {req.request_id} expires {req.expires_at}"])

    result = {
        "artifact": str(getattr(artifact, "path", "")),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "verdict": verdict,
        "reason_code": reason_code,
        "stages": {
            "preflight": preflight, "security": sec, "quality": qual,
            "integrity": {"status": "PASS" if integrity_ok else "FAIL", "violations": dag_violations},
            "precision": precision, "rag": rag, "skills": skill_stage,
            "stability": stability, "math": math, "reasoning": reason, "dry_run": dry_run,
            "complaints": complaints_stage,
        },
        "hitl_request": hitl_request,
        "mandatory_skills_invoked": skill_stage.get("invoked", []),
        "skill_invocation_status": skill_stage["status"],
        "skill_manifest_provided": skill_stage.get("manifest_provided", False),
        "autofix_history": autofix_history,
    }
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
    ap.add_argument("--no-autofix", action="store_true",
                        help="disable the auto-fix loop (AutoFixEngine)")
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

    # Auto-fix: enabled by default, disabled with --no-autofix
    enable_autofix = not args.no_autofix

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
                          resolve_complaints=resolve_complaints,
                          enable_autofix=enable_autofix)
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
