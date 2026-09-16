"""Tests for N8nPrecisionGate Package H (Stage 3.4 PRECISION extension) — the
n8n runtime-semantics rules mined from the clinic booking campaign: duplicate
node ids, Python literals in Code nodes, literal/expression mixing, approval
placement, errorWorkflow shape, Redis decr, $env fallbacks, +HH:MM offsets,
alwaysOutputData reliance, chat-scoped dedup keys, and calendar time zones.
Plus the two false-positive fixes: respondToWebhook exempt from
WEBHOOK_NO_AUTH, and JSON object keys no longer trip the counting detector.
Deterministic, no network, no audit.db writes.
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.build_gates_pipeline import (
    run_pipeline, N8nPrecisionGate, DeepReasoningGate, AutoFixEngine,
)
from security_gate import SecurityGate


class _SilentReporter:
    def __init__(self):
        self.json_out = False

    def stage(self, name, status, violations, score=None, warnings=None):
        pass


def _run(artifact, hitl=False, enable_autofix=False):
    full_text = json.dumps(artifact, default=str)
    return run_pipeline(artifact, full_text, hitl=hitl, reporter=_SilentReporter(), enable_autofix=enable_autofix)


def _wf(nodes, connections=None, extra=None):
    wf = {"name": "T", "nodes": nodes, "connections": connections or {}}
    if extra:
        wf.update(extra)
    return wf


def _node(name, ntype="n8n-nodes-base.code", nid=None, **params):
    return {"id": nid if nid is not None else name, "name": name, "type": ntype,
            "typeVersion": 2, "position": [0, 0], "parameters": params or {}}


def _trigger():
    return _node("Receive Webhook", "n8n-nodes-base.webhook",
                 path="h", authentication="headerAuth")


def _run_h(nodes, extra=None):
    wf = _wf([_trigger()] + nodes, extra=extra)
    return N8nPrecisionGate().run(wf, {})


def _has(violations, prefix):
    return any(v.startswith(prefix + ":") for v in violations)


# ---------------------------------------------------------------------------
# H1 — duplicate node ids
# ---------------------------------------------------------------------------

def test_h1_duplicate_ids_fail():
    r = _run_h([_node("A", nid="x"), _node("B", nid="x")])
    assert r["status"] == "FAIL"
    assert _has(r["violations"], "H1")


def test_h1_unique_ids_pass():
    r = _run_h([_node("A", nid="a"), _node("B", nid="b")])
    assert not _has(r["violations"], "H1")


# ---------------------------------------------------------------------------
# H2 — Python literals in Code nodes
# ---------------------------------------------------------------------------

def test_h2_python_true_fails():
    r = _run_h([_node("Calc", jsCode="return {ok: True};")])
    assert _has(r["violations"], "H2")


def test_h2_python_none_fails():
    r = _run_h([_node("Calc", jsCode="const x = None; return [{json:{x}}];")])
    assert _has(r["violations"], "H2")


def test_h2_js_literals_pass():
    r = _run_h([_node("Calc", jsCode="return [{json:{ok: true, v: null}}];")])
    assert not _has(r["violations"], "H2")


def test_h2_python_word_inside_string_passes():
    r = _run_h([_node("Calc", jsCode='return [{json:{note: "None of your business"}}];')])
    assert not _has(r["violations"], "H2")


# ---------------------------------------------------------------------------
# H3 — literal prefix mixed with an expression
# ---------------------------------------------------------------------------

def test_h3_mixed_literal_expression_fails():
    r = _run_h([_node("Mix", "n8n-nodes-base.set", v="=Today is {{$json.d}}")])
    assert _has(r["violations"], "H3")


def test_h3_pure_expression_passes():
    r = _run_h([_node("Mix", "n8n-nodes-base.set", v="={{ $json.d }}")])
    assert not _has(r["violations"], "H3")


def test_h3_plain_static_passes():
    r = _run_h([_node("Mix", "n8n-nodes-base.set", v="Today is fine")])
    assert not _has(r["violations"], "H3")


# ---------------------------------------------------------------------------
# H4 — approval placement (+ autofix)
# ---------------------------------------------------------------------------

def test_h4_node_level_approval_fails():
    n = _node("Appr", "n8n-nodes-base.httpRequest",
              url="https://x.test/", authentication="none")
    n["requiresHumanApproval"] = True
    r = _run_h([n])
    assert _has(r["violations"], "H4")


def test_h4_parameters_level_approval_passes():
    r = _run_h([_node("Appr", "n8n-nodes-base.httpRequest",
                       url="https://x.test/", authentication="none",
                       requiresHumanApproval=True)])
    assert not _has(r["violations"], "H4")


def test_h4_autofix_moves_approval_into_parameters():
    n = _node("Appr", "n8n-nodes-base.code", jsCode="return [];")
    n["requiresHumanApproval"] = True
    wf = _wf([_trigger(), n])
    engine = AutoFixEngine(wf, {"PRECISION": ["H4: node 'Appr' sets requiresHumanApproval"]})
    fixed, fixes = engine.apply_all()
    appr = next(x for x in fixed["nodes"] if x["name"] == "Appr")
    assert "requiresHumanApproval" not in appr
    assert appr["parameters"].get("requiresHumanApproval") is True
    assert any("requiresHumanApproval" in f for f in fixes)
    r2 = N8nPrecisionGate().run(fixed, {})
    assert not _has(r2["violations"], "H4")


# ---------------------------------------------------------------------------
# H5 — errorWorkflow shape
# ---------------------------------------------------------------------------

def test_h5_expression_error_workflow_fails():
    r = _run_h([], extra={"settings": {"errorWorkflow": "={{ $json.e }}"}})
    assert _has(r["violations"], "H5")


def test_h5_plain_id_passes():
    r = _run_h([], extra={"settings": {"errorWorkflow": "AbC123xYz"}})
    assert not _has(r["violations"], "H5")


def test_h5_absent_passes():
    r = _run_h([])
    assert not _has(r["violations"], "H5")


# ---------------------------------------------------------------------------
# H6 — Redis decr
# ---------------------------------------------------------------------------

def _redis(name, op, cred=True):
    n = _node(name, "n8n-nodes-base.redis", operation=op, key="k")
    if cred:
        n["credentials"] = {"redis": {"id": "1", "name": "R"}}
    return n


def test_h6_redis_decr_fails():
    r = _run_h([_redis("Dec", "decr")])
    assert _has(r["violations"], "H6")


def test_h6_redis_incr_passes():
    r = _run_h([_redis("Inc", "incr")])
    assert not _has(r["violations"], "H6")


# ---------------------------------------------------------------------------
# H7-H11 — warnings (non-blocking)
# ---------------------------------------------------------------------------

def test_h7_env_without_fallback_warns():
    r = _run_h([_node("Env", jsCode="const k=$env.K; return [{json:{k}}];")])
    assert r["status"] == "PASS"
    assert _has(r.get("warnings", []), "H7")


def test_h7_env_with_fallback_clean():
    r = _run_h([_node("Env", jsCode="const k=$env.K || 'd'; return [{json:{k}}];")])
    assert not _has(r.get("warnings", []), "H7")


def test_h8_plus_offset_warns():
    r = _run_h([_node("Q", "n8n-nodes-base.httpRequest",
                       url="https://x.test/?t=2026-01-01T00:00:00+03:00",
                       authentication="none")])
    assert _has(r.get("warnings", []), "H8")


def test_h8_zulu_offset_clean():
    r = _run_h([_node("Q", "n8n-nodes-base.httpRequest",
                       url="https://x.test/?t=2026-01-01T00:00:00Z",
                       authentication="none")])
    assert not _has(r.get("warnings", []), "H8")


def test_h9_always_output_data_warns():
    r = _run_h([_node("Empty", alwaysOutputData=True, jsCode="return [{json:{}}];")])
    assert _has(r.get("warnings", []), "H9")


def test_h10_mid_without_chat_warns():
    r = _run_h([_redis("Lock", "incr")])
    n = _node("Lock2", "n8n-nodes-base.redis", operation="incr",
              key="slot:mid123")
    n["credentials"] = {"redis": {"id": "1", "name": "R"}}
    r = _run_h([n])
    assert _has(r.get("warnings", []), "H10")


def test_h10_chat_scoped_key_clean():
    n = _node("Lock", "n8n-nodes-base.redis", operation="incr",
              key="tg:<chat>:<mid>")
    n["credentials"] = {"redis": {"id": "1", "name": "R"}}
    r = _run_h([n])
    assert not _has(r.get("warnings", []), "H10")


def test_h11_calendar_without_timezone_warns():
    n = _node("Cal", "n8n-nodes-base.googleCalendar", operation="create")
    n["credentials"] = {"googleCalendarOAuth2Api": {"id": "1", "name": "G"}}
    r = _run_h([n])
    assert _has(r.get("warnings", []), "H11")


def test_h11_calendar_with_cairo_signal_clean():
    n = _node("Cal", "n8n-nodes-base.googleCalendar", operation="create",
              start="={{ $json.start }}", timeZone="Africa/Cairo")
    n["credentials"] = {"googleCalendarOAuth2Api": {"id": "1", "name": "G"}}
    r = _run_h([n])
    assert not _has(r.get("warnings", []), "H11")


# ---------------------------------------------------------------------------
# Pipeline wiring — Package H blocks like the rest of PRECISION
# ---------------------------------------------------------------------------

def test_pipeline_h1_blocks_with_precision_verdict():
    wf = _wf([_node("A", nid="dup"), _node("B", nid="dup")])
    res = _run(wf, enable_autofix=False)
    assert res["verdict"] == "N8N_PRECISION_VIOLATION"
    assert res["stages"]["precision"]["status"] == "FAIL"


def test_warnings_do_not_block_pipeline():
    n = _node("Env", jsCode="const k=$env.K; return [{json:{k}}];")
    wf = _wf([_trigger(), n],
             {"Receive Webhook": {"main": [{"node": "Env"}]}})
    res = _run(wf, enable_autofix=False)
    assert res["stages"]["precision"]["status"] == "PASS"
    assert any(w.startswith("H7:") for w in res["stages"]["precision"].get("warnings", []))


# ---------------------------------------------------------------------------
# FP fix 1 — respondToWebhook exempt from WEBHOOK_NO_AUTH
# ---------------------------------------------------------------------------

def test_r5_respond_to_webhook_exempt():
    wf = {"nodes": [
        {"name": "Hook", "type": "n8n-nodes-base.webhook",
         "parameters": {"path": "h", "authentication": "headerAuth"}},
        {"name": "Reply", "type": "n8n-nodes-base.respondToWebhook",
         "parameters": {"responseMode": "lastNode"}},
    ], "connections": {}}
    d = SecurityGate().evaluate_to_dict(wf)
    assert not any("WEBHOOK_NO_AUTH" in v for v in d["violations"])


def test_r5_unauthed_webhook_trigger_still_flagged():
    wf = {"nodes": [
        {"name": "Hook", "type": "n8n-nodes-base.webhook",
         "parameters": {"path": "h"}},
    ], "connections": {}}
    d = SecurityGate().evaluate_to_dict(wf)
    assert any("WEBHOOK_NO_AUTH" in v for v in d["violations"])


# ---------------------------------------------------------------------------
# FP fix 2 — JSON object keys do not trip the counting detector
# ---------------------------------------------------------------------------

def test_reasoning_json_count_key_does_not_flag():
    full_text = '{"key": "count", "total": 5, "limit": 250}'
    r = DeepReasoningGate().run({"nodes": []}, full_text, {}, "SKIP")
    assert r["status"] == "PASS"


def test_reasoning_real_counting_prose_still_flags():
    full_text = "how many roots are in the interval without verification"
    r = DeepReasoningGate().run({"nodes": []}, full_text, {}, "SKIP")
    assert r["status"] == "NEEDS_REVIEW"
