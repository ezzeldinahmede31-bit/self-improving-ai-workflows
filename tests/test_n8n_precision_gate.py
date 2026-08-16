"""Tests for the N8nPrecisionGate (Stage 3.4 PRECISION) — the n8n runtime-
precision structural gate: unique node names, a trigger, valid typeVersion,
resolvable expression refs, and real credential binding. Deterministic, no
network, no audit.db writes (--no-hitl paths only).
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.build_gates_pipeline import (
    run_pipeline, N8nPrecisionGate, DryRunGate,
    _is_trigger_node, _extract_node_refs,
)


class _SilentReporter:
    def stage(self, name, status, violations, score=None, warnings=None):
        pass


def _run(artifact, hitl=False):
    full_text = json.dumps(artifact, default=str)
    return run_pipeline(artifact, full_text, hitl=hitl, reporter=_SilentReporter())


def _wf(nodes, connections=None, extra=None):
    wf = {"name": "T", "nodes": nodes, "connections": connections or {}}
    if extra:
        wf.update(extra)
    return wf


def _node(name, ntype="n8n-nodes-base.httpRequest", **params):
    return {"id": name, "name": name, "type": ntype, "typeVersion": 2,
            "position": [0, 0], "parameters": params or {}}


def _trigger():
    return _node("Receive Webhook", "n8n-nodes-base.webhook",
                 path="h", authentication="headerAuth")


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def test_is_trigger_node():
    assert _is_trigger_node("n8n-nodes-base.webhook")
    assert _is_trigger_node("n8n-nodes-base.scheduleTrigger")
    assert _is_trigger_node("n8n-nodes-base.manualTrigger")
    assert _is_trigger_node("n8n-nodes-base.formTrigger")
    assert _is_trigger_node("n8n-nodes-base.chatTrigger")
    assert _is_trigger_node("n8n-nodes-base.form")
    assert not _is_trigger_node("n8n-nodes-base.code")
    assert not _is_trigger_node("n8n-nodes-base.httpRequest")


def test_extract_node_refs():
    text = ("$node['Fetch Homepage'].json['email'] and $node['A'].x and "
            "$('B') and $nodes.C and $json['notA'] and $input.first().json")
    assert _extract_node_refs(text) == ["Fetch Homepage", "A", "B", "C"]


# ---------------------------------------------------------------------------
# P1 duplicate node names
# ---------------------------------------------------------------------------

def test_duplicate_node_names_fail():
    wf = _wf([_trigger(), _node("A"), _node("A")])
    res = N8nPrecisionGate().run(wf, {})
    assert res["status"] == "FAIL"
    assert any("duplicate node name 'A'" in v for v in res["violations"])


# ---------------------------------------------------------------------------
# P2 trigger required
# ---------------------------------------------------------------------------

def test_no_trigger_fails():
    wf = _wf([_node("A", "n8n-nodes-base.code", jsCode="return [];")])
    res = N8nPrecisionGate().run(wf, {})
    assert res["status"] == "FAIL"
    assert any("no trigger node" in v for v in res["violations"])


def test_subworkflow_escape_hatch_skips_p2():
    wf = _wf([_node("A", "n8n-nodes-base.code", jsCode="return [];")],
             extra={"_gates": {"subworkflow": True}})
    res = N8nPrecisionGate().run(wf, {"subworkflow": True})
    assert res["status"] == "PASS"


def test_trigger_present_passes_p2():
    wf = _wf([_trigger(), _node("A", "n8n-nodes-base.code", jsCode="return [];")])
    res = N8nPrecisionGate().run(wf, {})
    assert res["status"] == "PASS"


# ---------------------------------------------------------------------------
# P3 typeVersion
# ---------------------------------------------------------------------------

def test_missing_typeversion_fails():
    n = _node("A", "n8n-nodes-base.httpRequest", url="https://example.com")
    del n["typeVersion"]
    wf = _wf([_trigger(), n])
    res = N8nPrecisionGate().run(wf, {})
    assert res["status"] == "FAIL"
    assert any("typeVersion" in v for v in res["violations"])


def test_zero_typeversion_fails():
    n = _node("A", "n8n-nodes-base.httpRequest", url="https://example.com")
    n["typeVersion"] = 0
    wf = _wf([_trigger(), n])
    res = N8nPrecisionGate().run(wf, {})
    assert any("typeVersion" in v for v in res["violations"])


# ---------------------------------------------------------------------------
# P4 expression refs
# ---------------------------------------------------------------------------

def test_dangling_node_ref_fails():
    n = _node("B", "n8n-nodes-base.set",
              assignments={"assignments": [
                  {"name": "x", "value": "={{ $node['Ghost'].json.id }}"}]})
    wf = _wf([_trigger(), n])
    res = N8nPrecisionGate().run(wf, {})
    assert res["status"] == "FAIL"
    assert any("'Ghost'" in v for v in res["violations"])


def test_resolved_node_ref_passes():
    n = _node("A", "n8n-nodes-base.set",
              assignments={"assignments": [
                  {"name": "x", "value": "={{ $node['Receive Webhook'].json.id }}"}]})
    wf = _wf([_trigger(), n])
    res = N8nPrecisionGate().run(wf, {})
    assert res["status"] == "PASS"


# ---------------------------------------------------------------------------
# P5 credential binding
# ---------------------------------------------------------------------------

def test_http_auth_requires_credential():
    n = _node("Call API", "n8n-nodes-base.httpRequest",
              url="https://example.com", authentication="genericCredentialType")
    wf = _wf([_trigger(), n])
    res = N8nPrecisionGate().run(wf, {})
    assert res["status"] == "FAIL"
    assert any("requires a credential" in v for v in res["violations"])


def test_http_explicit_none_ok():
    n = _node("Call API", "n8n-nodes-base.httpRequest",
              url="https://example.com", authentication="none")
    wf = _wf([_trigger(), n])
    res = N8nPrecisionGate().run(wf, {})
    assert res["status"] == "PASS"


def test_http_no_auth_param_ok():
    n = _node("Call API", "n8n-nodes-base.httpRequest", url="https://example.com")
    wf = _wf([_trigger(), n])
    res = N8nPrecisionGate().run(wf, {})
    assert res["status"] == "PASS"


def test_app_node_requires_credential():
    n = _node("Send Slack", "n8n-nodes-base.slack",
              resource="message", operation="post")
    wf = _wf([_trigger(), n])
    res = N8nPrecisionGate().run(wf, {})
    assert res["status"] == "FAIL"
    assert any("requires a credential" in v for v in res["violations"])


def test_app_node_with_credential_ok():
    n = _node("Send Slack", "n8n-nodes-base.slack",
              resource="message", operation="post")
    n["credentials"] = {"slackApi": {"id": "c1", "name": "Workspace Slack"}}
    wf = _wf([_trigger(), n])
    res = N8nPrecisionGate().run(wf, {})
    assert res["status"] == "PASS"


def test_placeholder_credential_fails():
    n = _node("Send Slack", "n8n-nodes-base.slack",
              resource="message", operation="post")
    n["credentials"] = {"slackApi": {"id": "c1", "name": "YOUR_API_KEY"}}
    wf = _wf([_trigger(), n])
    res = N8nPrecisionGate().run(wf, {})
    assert res["status"] == "FAIL"
    assert any("placeholder credential" in v for v in res["violations"])


def test_empty_workflow_skips():
    res = N8nPrecisionGate().run({"nodes": []}, {})
    assert res["status"] == "SKIP"


# ---------------------------------------------------------------------------
# DryRunGate: trigger-node pinned evidence is now required
# ---------------------------------------------------------------------------

def test_dry_run_pinned_off_trigger_ok():
    wf = _wf([_node("Receive Webhook", "n8n-nodes-base.webhook",
                    path="h", authentication="headerAuth",
                    pinnedData={"1": {"json": {"id": 1}}}),
              _node("A", "n8n-nodes-base.code", jsCode="return [];")])
    res = DryRunGate().run(wf, {})
    assert res["status"] == "PASS"


def test_dry_run_pinned_off_path_fails_when_trigger_exists():
    # pinned data buried mid-graph (not on the trigger) is NOT trial evidence
    wf = _wf([_node("Receive Webhook", "n8n-nodes-base.webhook",
                    path="h", authentication="headerAuth"),
              _node("A", "n8n-nodes-base.code", jsCode="return [];",
                    pinnedData={"1": {"json": {"id": 1}}})])
    res = DryRunGate().run(wf, {})
    assert res["status"] == "FAIL"
    assert any("dry-run" in v for v in res["violations"])


def test_dry_run_pinned_any_node_ok_without_trigger():
    wf = _wf([_node("A", "n8n-nodes-base.code", jsCode="return [];",
                    pinnedData={"1": {"json": {"id": 1}}})])
    res = DryRunGate().run(wf, {})
    assert res["status"] == "PASS"


# ---------------------------------------------------------------------------
# integration: precision blocks / passes in the full pipeline
# ---------------------------------------------------------------------------

def test_pipeline_precision_violation_blocks():
    wf = _wf([_node("A", "n8n-nodes-base.code", jsCode="return [];"),
              _node("A", "n8n-nodes-base.code", jsCode="return [];")])
    res = _run(wf)
    assert res["verdict"] == "N8N_PRECISION_VIOLATION"
    assert res["reason_code"] == "RUNTIME_STRUCTURAL_INCONSISTENCY"
    assert res["stages"]["precision"]["status"] == "FAIL"


def test_pipeline_clean_workflow_passes_precision():
    wf = _wf([_trigger(), _node("Send HTTP Response")],
             {"Receive Webhook": {"main": [{"node": "Send HTTP Response"}]}})
    res = _run(wf)
    assert res["stages"]["precision"]["status"] == "PASS"
    assert res["verdict"] == "DRY_RUN_EVIDENCE_MISSING"


def test_pipeline_precision_reports_checked_count():
    wf = _wf([_trigger(), _node("A")])
    res = _run(wf)
    assert res["stages"]["precision"]["checked"] == 2


# ---------------------------------------------------------------------------
# Package A: graph integrity (FAIL rules A1/A2/A3)
# ---------------------------------------------------------------------------

def test_a1_orphaned_node_fails():
    # a real graph exists but the code node has zero incoming edges → dead
    wf = _wf([_trigger(), _node("Data", "n8n-nodes-base.code", jsCode="return [];"),
              _node("Sink")],
             {"Receive Webhook": {"main": [{"node": "Sink"}]}})
    res = N8nPrecisionGate().run(wf, {})
    assert res["status"] == "FAIL"
    assert any(v.startswith("A1: node 'Data'") for v in res["violations"])


def test_a1_all_reachable_passes():
    wf = _wf([_trigger(), _node("Sink")],
             {"Receive Webhook": {"main": [{"node": "Sink"}]}})
    res = N8nPrecisionGate().run(wf, {})
    assert res["status"] == "PASS"


def test_a1_ignored_when_no_connections_object():
    # no graph info → 'no information', must NOT fail (legacy minimal tests)
    wf = _wf([_trigger(), _node("A")])
    res = N8nPrecisionGate().run(wf, {})
    assert res["status"] == "PASS"


def test_a2_dangling_branch_fails():
    # IF true branch empty: items on that path are silently dropped
    wf = _wf([_trigger(),
              _node("Split", "n8n-nodes-base.if", conditions={}),
              _node("Sink")],
             {"Receive Webhook": {"main": [{"node": "Split"}]},
              "Split": {"main": [[{"node": "Sink"}], []]}})
    res = N8nPrecisionGate().run(wf, {})
    assert res["status"] == "FAIL"
    assert any(v.startswith("A2: node 'Split' output branch 1") for v in res["violations"])


def test_a2_all_branches_wired_passes():
    wf = _wf([_trigger(),
              _node("Split", "n8n-nodes-base.if", conditions={}),
              _node("T"), _node("F")],
             {"Receive Webhook": {"main": [{"node": "Split"}]},
              "Split": {"main": [[{"node": "T"}], [{"node": "F"}]]}})
    res = N8nPrecisionGate().run(wf, {})
    assert res["status"] == "PASS"


def test_a3_respond_to_webhook_without_trigger_fails():
    wf = _wf([_node("Reply", "n8n-nodes-base.respondToWebhook")])
    res = N8nPrecisionGate().run(wf, {})
    assert res["status"] == "FAIL"
    assert any(v.startswith("A3:") for v in res["violations"])


def test_a3_respond_to_webhook_with_trigger_passes():
    wf = _wf([_trigger(), _node("Reply", "n8n-nodes-base.respondToWebhook")],
             {"Receive Webhook": {"main": [{"node": "Reply"}]}})
    res = N8nPrecisionGate().run(wf, {})
    assert res["status"] == "PASS"


# ---------------------------------------------------------------------------
# Package B + C: best-practice warnings (non-blocking)
# ---------------------------------------------------------------------------

def test_b1_bare_json_multiple_upstreams_warns():
    wf = _wf([_trigger(),
              _node("A", "n8n-nodes-base.code", jsCode="return [];"),
              _node("B", "n8n-nodes-base.code", jsCode="return [];"),
              _node("Merge", "n8n-nodes-base.set", json={"x": "={{ $json.x }}"})],
             {"Receive Webhook": {"main": [{"node": "A"}, {"node": "B"}]},
              "A": {"main": [{"node": "Merge"}]},
              "B": {"main": [{"node": "Merge"}]}})
    res = N8nPrecisionGate().run(wf, {})
    assert res["status"] == "PASS"  # warning only, does not block
    assert any(w.startswith("B1: node 'Merge'") for w in res["warnings"])


def test_b2_set_consumed_by_one_warns():
    wf = _wf([_trigger(), _node("Shape", "n8n-nodes-base.set", json={}),
              _node("Sink")],
             {"Receive Webhook": {"main": [{"node": "Shape"}]},
              "Shape": {"main": [{"node": "Sink"}]}})
    res = N8nPrecisionGate().run(wf, {})
    assert res["status"] == "PASS"
    assert any(w.startswith("B2: Set node 'Shape'") for w in res["warnings"])


def test_b3_passthrough_code_node_warns():
    wf = _wf([_trigger(),
              _node("Pass", "n8n-nodes-base.code",
                    jsCode="return $input.all();")],
             {"Receive Webhook": {"main": [{"node": "Pass"}]}})
    res = N8nPrecisionGate().run(wf, {})
    assert res["status"] == "PASS"
    assert any(w.startswith("B3: Code node 'Pass'") for w in res["warnings"])


def test_c1_network_node_without_retry_warns():
    wf = _wf([_trigger(), _node("Call API")],
             {"Receive Webhook": {"main": [{"node": "Call API"}]}})
    res = N8nPrecisionGate().run(wf, {})
    assert res["status"] == "PASS"
    assert any(w.startswith("C1: network node 'Call API'") for w in res["warnings"])


def test_c1_retry_on_fail_clears_warning():
    node = _node("Call API")
    node["retryOnFail"] = True
    node["maxTries"] = 3
    node["waitBetweenTries"] = 1000
    wf = _wf([_trigger(), node],
             {"Receive Webhook": {"main": [{"node": "Call API"}]}})
    res = N8nPrecisionGate().run(wf, {})
    assert res["status"] == "PASS"
    assert not any(w.startswith("C1:") for w in res["warnings"])


def test_c2_write_node_without_idempotency_warns():
    node = _node("Create Row", "n8n-nodes-base.googleSheets",
                 operation="create", documentId="x", sheetName="S")
    node["credentials"] = {"googleSheetsOAuth2Api": {"id": "c1", "name": "Cred"}}
    wf = _wf([_trigger(), node],
             {"Receive Webhook": {"main": [{"node": "Create Row"}]}})
    res = N8nPrecisionGate().run(wf, {})
    assert res["status"] == "PASS"
    assert any(w.startswith("C2: write node 'Create Row'") for w in res["warnings"])


def test_c2_idempotency_signal_clears_warning():
    node = _node("Create Row", "n8n-nodes-base.googleSheets",
                 operation="create", documentId="x", sheetName="S",
                 options={"idempotencyKey": "={{ $json.webhook_id }}"})
    node["credentials"] = {"googleSheetsOAuth2Api": {"id": "c1", "name": "Cred"}}
    wf = _wf([_trigger(), node],
             {"Receive Webhook": {"main": [{"node": "Create Row"}]}})
    res = N8nPrecisionGate().run(wf, {})
    assert res["status"] == "PASS"
    assert not any(w.startswith("C2:") for w in res["warnings"])


def test_warnings_key_present_on_fail_too():
    # a FAILing workflow still carries the warnings channel
    wf = _wf([_node("Reply", "n8n-nodes-base.respondToWebhook")])
    res = N8nPrecisionGate().run(wf, {})
    assert res["status"] == "FAIL"
    assert isinstance(res.get("warnings"), list)


# ---------------------------------------------------------------------------
# Package D — webhook integrity (HMAC signature + timestamp freshness)
# ---------------------------------------------------------------------------

def _write_node(name="Create Row", **params):
    node = _node(name, "n8n-nodes-base.googleSheets",
                 operation="create", documentId="x", sheetName="S", **params)
    node["credentials"] = {"googleSheetsOAuth2Api": {"id": "c1", "name": "Cred"}}
    return node


def test_d1_unauthed_webhook_with_write_fails():
    hook = _node("Hook", "n8n-nodes-base.webhook", path="h")  # no authentication
    wf = _wf([hook, _write_node()],
             {"Hook": {"main": [{"node": "Create Row"}]}})
    res = N8nPrecisionGate().run(wf, {})
    assert res["status"] == "FAIL"
    assert any(v.startswith("D1:") for v in res["violations"])


def test_d1_explicit_none_auth_with_write_fails():
    hook = _node("Hook", "n8n-nodes-base.webhook", path="h", authentication="none")
    wf = _wf([hook, _write_node()],
             {"Hook": {"main": [{"node": "Create Row"}]}})
    res = N8nPrecisionGate().run(wf, {})
    assert res["status"] == "FAIL"
    assert any(v.startswith("D1:") for v in res["violations"])


def test_d1_authed_webhook_with_write_passes():
    wf = _wf([_trigger(), _write_node()],
             {"Receive Webhook": {"main": [{"node": "Create Row"}]}})
    res = N8nPrecisionGate().run(wf, {})
    assert res["status"] == "PASS"
    assert not any(v.startswith("D1:") for v in res["violations"])


def test_d1_unauthed_webhook_read_only_passes():
    # public read-only webhook without auth is acceptable (no side effect)
    hook = _node("Hook", "n8n-nodes-base.webhook", path="h")
    wf = _wf([hook, _node("Lookup", "n8n-nodes-base.httpRequest",
                          url="https://example.com", options={})],
             {"Hook": {"main": [{"node": "Lookup"}]}})
    res = N8nPrecisionGate().run(wf, {})
    assert res["status"] == "PASS"
    assert not any(v.startswith("D1:") for v in res["violations"])


def test_d2_webhook_write_no_signature_warns():
    wf = _wf([_trigger(), _write_node()],
             {"Receive Webhook": {"main": [{"node": "Create Row"}]}})
    res = N8nPrecisionGate().run(wf, {})
    assert res["status"] == "PASS"
    assert any(w.startswith("D2:") for w in res["warnings"])


def test_d2_signature_signal_clears_warning():
    code = _node("Verify Sig", "n8n-nodes-base.code",
                 jsCode="const h = crypto.createHmac('sha256', 's'); ...")
    wf = _wf([_trigger(), code, _write_node()],
             {"Receive Webhook": {"main": [{"node": "Verify Sig"}]},
              "Verify Sig": {"main": [{"node": "Create Row"}]}})
    res = N8nPrecisionGate().run(wf, {})
    assert res["status"] == "PASS"
    assert not any(w.startswith("D2:") for w in res["warnings"])
    assert any(w.startswith("D3:") for w in res["warnings"])


def test_d3_timestamp_freshness_clears_warning():
    code = _node("Verify Sig", "n8n-nodes-base.code",
                 jsCode="crypto.createHmac('sha256','s');"
                        "if (Math.abs(Date.now() - ts) > 300000) throw new Error('stale')")
    wf = _wf([_trigger(), code, _write_node()],
             {"Receive Webhook": {"main": [{"node": "Verify Sig"}]},
              "Verify Sig": {"main": [{"node": "Create Row"}]}})
    res = N8nPrecisionGate().run(wf, {})
    assert res["status"] == "PASS"
    assert not any(w.startswith("D2:") for w in res["warnings"])
    assert not any(w.startswith("D3:") for w in res["warnings"])


# ---------------------------------------------------------------------------
# Package G — OWASP Agentic AI Top 10 2026 mapping (audit log)
# ---------------------------------------------------------------------------

def test_owasp_mapping_classifies_violations():
    from scripts.build_gates_pipeline import _map_owasp_aa0x
    stages = {
        "security": {"status": "FAIL", "violations": [
            "Prompt injection: unsanitized prompt-injection vector from webhook body",
            "Webhook has no authentication: webhook_no_auth — anyone can trigger",
        ]},
        "precision": {"status": "PASS", "violations": []},
    }
    mapped = _map_owasp_aa0x(stages)
    assert "AA01" in mapped        # prompt injection
    assert "AA04" in mapped        # access control (webhook_no_auth)
    assert mapped["AA01"]["findings"] == ["security: Prompt injection: unsanitized "
                                          "prompt-injection vector from webhook body"]
    assert mapped["AA04"]["findings"][0].startswith("security: Webhook has no authentication")


def test_owasp_mapping_ignores_empty_stages():
    from scripts.build_gates_pipeline import _map_owasp_aa0x
    assert _map_owasp_aa0x({}) == {}
    assert _map_owasp_aa0x({"security": {"violations": []}}) == {}


def test_owasp_aa0x_in_pipeline_result():
    # a clean artifact passes with an empty mapping; a malicious one maps
    malicious = _wf(
        [_trigger(),
         _node("Create Row", "n8n-nodes-base.googleSheets", operation="create",
               documentId="x", sheetName="S")],
        {"Receive Webhook": {"main": [{"node": "Create Row"}]}})
    # P5 will also fail (no credential) — mapping still sees the write node
    res = _run(malicious)
    assert "owasp_aa0x" in res
    assert isinstance(res["owasp_aa0x"], dict)


# ---------------------------------------------------------------------------
# Package E — LLM agent maturity (langchain/openAI/agent family)
# ---------------------------------------------------------------------------
# In real n8n the agent node's model/tool/memory nodes connect ONLY through its
# ai_languageModel / ai_tool outputs (never the main flow). To keep the gate's
# A1 orphan check happy in tests, the model/tool nodes also receive a main edge
# from the webhook trigger (parallel fan-out) so every node is reachable.

def _agent(name="Agent", **params):
    return _node(name, "n8n-nodes-langchain.agent", **params)


def _model(name="Model"):
    node = _node(name, "n8n-nodes-langchain.openAi")
    node["credentials"] = {"openAiApi": {"id": "c1", "name": "OpenAI"}}
    return node


def _tool(name="Tool"):
    return _node(name, "n8n-nodes-base.workflowTool")


def _agent_conn(agent="Agent", model="Model", tool="Tool", ai_tool=None):
    conn = {"Receive Webhook": {"main": [{"node": agent}, {"node": model},
                                         {"node": tool}]},
            agent: {"ai_languageModel": [{"node": model}]}}
    if ai_tool is not None:
        conn[agent]["ai_tool"] = [{"node": ai_tool}]
    return conn


def test_e1_agent_without_model_fails():
    wf = _wf([_trigger(), _agent()],
             {"Receive Webhook": {"main": [{"node": "Agent"}]}})
    res = N8nPrecisionGate().run(wf, {})
    assert res["status"] == "FAIL"
    assert any(v.startswith("E1:") for v in res["violations"])


def test_e1_agent_with_model_passes():
    agent = _agent(options={"systemMessage": "You are helpful",
                            "maxIterations": 5})
    wf = _wf([_trigger(), agent, _model(), _tool()], _agent_conn())
    res = N8nPrecisionGate().run(wf, {})
    assert res["status"] == "PASS"
    assert not any(v.startswith("E1:") for v in res["violations"])


def test_e2_agent_without_system_prompt_warns():
    agent = _agent(options={"maxIterations": 5})
    wf = _wf([_trigger(), agent, _model(), _tool()], _agent_conn())
    res = N8nPrecisionGate().run(wf, {})
    assert res["status"] == "PASS"          # E2 is a warning, not a failure
    assert any(w.startswith("E2:") for w in res["warnings"])


def test_e2_system_prompt_clears_warning():
    agent = _agent(options={"systemMessage": "You are a helpful assistant",
                            "maxIterations": 5})
    wf = _wf([_trigger(), agent, _model(), _tool()], _agent_conn())
    res = N8nPrecisionGate().run(wf, {})
    assert res["status"] == "PASS"
    assert not any(w.startswith("E2:") for w in res["warnings"])


def test_e3_agent_without_max_iterations_warns():
    agent = _agent(options={"systemMessage": "You are helpful"})
    wf = _wf([_trigger(), agent, _model(), _tool()], _agent_conn())
    res = N8nPrecisionGate().run(wf, {})
    assert res["status"] == "PASS"
    assert any(w.startswith("E3:") for w in res["warnings"])


def test_e3_max_iterations_clears_warning():
    agent = _agent(options={"systemMessage": "You are helpful",
                            "maxIterations": 5})
    wf = _wf([_trigger(), agent, _model(), _tool()], _agent_conn())
    res = N8nPrecisionGate().run(wf, {})
    assert res["status"] == "PASS"
    assert not any(w.startswith("E3:") for w in res["warnings"])


def test_e4_agent_dangling_tool_ref_warns():
    agent = _agent(options={"systemMessage": "You are helpful",
                            "maxIterations": 5})
    wf = _wf([_trigger(), agent, _model(), _tool()],
             _agent_conn(ai_tool="Missing Tool"))
    res = N8nPrecisionGate().run(wf, {})
    assert res["status"] == "PASS"          # E4 is a warning, not a failure
    assert any(w.startswith("E4:") for w in res["warnings"])


def test_e4_agent_existing_tool_clears_warning():
    agent = _agent(options={"systemMessage": "You are helpful",
                            "maxIterations": 5})
    wf = _wf([_trigger(), agent, _model(), _tool()],
             _agent_conn(ai_tool="Tool"))
    res = N8nPrecisionGate().run(wf, {})
    assert res["status"] == "PASS"
    assert not any(w.startswith("E4:") for w in res["warnings"])


def test_pipeline_agent_without_model_blocks_precision():
    agent = _agent(options={"systemMessage": "You are a helpful assistant",
                            "maxIterations": 5},
                   tools=["webSearch"])
    wf = _wf([_trigger(), agent],
             {"Receive Webhook": {"main": [{"node": "Agent"}]}})
    res = _run(wf)
    assert res["verdict"] == "N8N_PRECISION_VIOLATION"
    assert res["reason_code"] == "RUNTIME_STRUCTURAL_INCONSISTENCY"
    assert res["stages"]["precision"]["status"] == "FAIL"
    assert any(v.startswith("E1:") for v in res["stages"]["precision"]["violations"])


# ---------------------------------------------------------------------------
# Package F — generic linting (bare URLs, placeholder paths, debug residue,
# TODO markers, insecure transport). All warnings.
# ---------------------------------------------------------------------------

def test_f1_hardcoded_url_without_cred_warns():
    node = _node("Fetch", "n8n-nodes-base.httpRequest",
                 url="https://api.example.com/v1")
    wf = _wf([_trigger(), node],
             {"Receive Webhook": {"main": [{"node": "Fetch"}]}})
    res = N8nPrecisionGate().run(wf, {})
    assert res["status"] == "PASS"          # F1 is a warning, not a failure
    assert any(w.startswith("F1:") for w in res["warnings"])


def test_f1_expression_url_clears_warning():
    node = _node("Fetch", "n8n-nodes-base.httpRequest",
                 url="https://api.example.com/v1/{{ $json.id }}")
    wf = _wf([_trigger(), node],
             {"Receive Webhook": {"main": [{"node": "Fetch"}]}})
    res = N8nPrecisionGate().run(wf, {})
    assert res["status"] == "PASS"
    assert not any(w.startswith("F1:") for w in res["warnings"])


def test_f2_webhook_placeholder_path_warns():
    node = _node("Hook", "n8n-nodes-base.webhook", path="your-webhook-path")
    wf = _wf([node])
    res = N8nPrecisionGate().run(wf, {})
    assert res["status"] == "PASS"
    assert any(w.startswith("F2:") for w in res["warnings"])


def test_f2_webhook_empty_path_warns():
    node = _node("Hook", "n8n-nodes-base.webhook", path="")
    wf = _wf([node])
    res = N8nPrecisionGate().run(wf, {})
    assert res["status"] == "PASS"
    assert any(w.startswith("F2:") for w in res["warnings"])


def test_f2_real_path_clears_warning():
    node = _node("Hook", "n8n-nodes-base.webhook", path="invoices/new")
    wf = _wf([node])
    res = N8nPrecisionGate().run(wf, {})
    assert res["status"] == "PASS"
    assert not any(w.startswith("F2:") for w in res["warnings"])


def test_f3_console_log_debug_residue_warns():
    node = _node("Transform", "n8n-nodes-base.code",
                 jsCode="console.log('debug'); return [{json: {x: 1}}];")
    wf = _wf([_trigger(), node],
             {"Receive Webhook": {"main": [{"node": "Transform"}]}})
    res = N8nPrecisionGate().run(wf, {})
    assert res["status"] == "PASS"
    assert any(w.startswith("F3:") for w in res["warnings"])


def test_f3_clean_code_clears_warning():
    node = _node("Transform", "n8n-nodes-base.code",
                 jsCode="return [{json: {x: $input.first().json.count * 2}}];")
    wf = _wf([_trigger(), node],
             {"Receive Webhook": {"main": [{"node": "Transform"}]}})
    res = N8nPrecisionGate().run(wf, {})
    assert res["status"] == "PASS"
    assert not any(w.startswith("F3:") for w in res["warnings"])


def test_f4_todo_marker_warns():
    node = _node("Transform", "n8n-nodes-base.code",
                 jsCode="// TODO: add retry handling\nreturn [{json: {x: 1}}];")
    wf = _wf([_trigger(), node],
             {"Receive Webhook": {"main": [{"node": "Transform"}]}})
    res = N8nPrecisionGate().run(wf, {})
    assert res["status"] == "PASS"
    assert any(w.startswith("F4:") for w in res["warnings"])


def test_f4_clean_code_clears_warning():
    node = _node("Transform", "n8n-nodes-base.code",
                 jsCode="return [{json: {x: 1}}];")
    wf = _wf([_trigger(), node],
             {"Receive Webhook": {"main": [{"node": "Transform"}]}})
    res = N8nPrecisionGate().run(wf, {})
    assert res["status"] == "PASS"
    assert not any(w.startswith("F4:") for w in res["warnings"])


def test_f5_insecure_http_literal_warns():
    node = _node("Fetch", "n8n-nodes-base.httpRequest",
                 url="http://insecure.example.com/api", authentication="headerAuth")
    node["credentials"] = {"httpHeaderAuth": {"id": "c1", "name": "Auth"}}
    wf = _wf([_trigger(), node],
             {"Receive Webhook": {"main": [{"node": "Fetch"}]}})
    res = N8nPrecisionGate().run(wf, {})
    assert res["status"] == "PASS"
    assert any(w.startswith("F5:") for w in res["warnings"])


def test_f5_https_only_clears_warning():
    node = _node("Fetch", "n8n-nodes-base.httpRequest",
                 url="https://secure.example.com/api", authentication="headerAuth")
    node["credentials"] = {"httpHeaderAuth": {"id": "c1", "name": "Auth"}}
    wf = _wf([_trigger(), node],
             {"Receive Webhook": {"main": [{"node": "Fetch"}]}})
    res = N8nPrecisionGate().run(wf, {})
    assert res["status"] == "PASS"
    assert not any(w.startswith("F5:") for w in res["warnings"])
