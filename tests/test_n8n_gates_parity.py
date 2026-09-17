"""n8n/code parity tests — every gate must hold n8n workflow JSON to the same
bar as programmatic code. A workflow that would be rejected as code (hardcoded
secret, private-network egress, SQL concatenation, broken expressions) must
not sail through the gates unchallenged.

Deterministic, no network, no audit.db writes.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from security_gate import SecurityGate
from quality_gate import QualityGate
from scripts.build_gates_pipeline import (
    N8nPrecisionGate, RagVectorGate, DryRunGate, run_pipeline,
)


class _SilentReporter:
    def __init__(self):
        self.json_out = False

    def stage(self, name, status, violations, score=None, warnings=None):
        pass


def _run(artifact, hitl=False, enable_autofix=False):
    full_text = json.dumps(artifact, default=str)
    return run_pipeline(artifact, full_text, hitl=hitl,
                        reporter=_SilentReporter(),
                        enable_autofix=enable_autofix)


def _node(name, ntype, **params):
    return {"id": name, "name": name, "type": ntype, "typeVersion": 1,
            "position": [0, 0], "parameters": params}


# ---------------------------------------------------------------------------
# SecurityGate — native n8n scans (no promoted rules needed)
# ---------------------------------------------------------------------------

class TestSecurityNativeN8n:
    def test_private_egress_rejected_without_promoted_rules(self):
        gate = SecurityGate(rules_dir=None)
        wf = {"nodes": [_node("H", "n8n-nodes-base.httpRequest",
                              url="http://192.168.1.5/x")]}
        r = gate.evaluate_to_dict(wf)
        assert r["status"] == "REJECTED_SECURITY_RISK"
        assert any("SSRF_INTERNAL_EGRESS" in v for v in r["violations"])

    def test_localhost_egress_rejected(self):
        gate = SecurityGate(rules_dir=None)
        wf = {"nodes": [_node("H", "n8n-nodes-base.httpRequest",
                              url="http://localhost:5678/rest/config")]}
        r = gate.evaluate_to_dict(wf)
        assert r["status"] == "REJECTED_SECURITY_RISK"

    def test_inline_secret_field_fatal(self):
        gate = SecurityGate(rules_dir=None)
        wf = {"nodes": [_node("H", "n8n-nodes-base.httpRequest",
                              url="https://api.example.com/x",
                              headerParameters={"parameters": [
                                  {"name": "X-Api-Key",
                                   "value": "abcdefghijklmnop123456"}]})]}
        # 'value' leaf is not secret-named, but a 20+ char key-named Code
        # assignment is the Code-shape canary:
        wf2 = {"nodes": [_node("C", "n8n-nodes-base.code",
                               jsCode="const apiKey = 'abcdefghijklmnop123456';")]}
        r = gate.evaluate_to_dict(wf2)
        assert r["status"] == "REJECTED_SECURITY_RISK"
        assert any("INLINE_SECRET" in v for v in r["violations"])

    def test_url_query_token_fatal(self):
        gate = SecurityGate(rules_dir=None)
        wf = {"nodes": [_node("H", "n8n-nodes-base.httpRequest",
                              url="https://api.example.com/x?api_key=SECRET1234567890")]}
        r = gate.evaluate_to_dict(wf)
        assert r["status"] == "REJECTED_SECURITY_RISK"
        assert any("URL_TOKEN_LEAK" in v for v in r["violations"])

    def test_sql_concatenation_flagged(self):
        gate = SecurityGate(rules_dir=None)
        wf = {"nodes": [_node("Q", "n8n-nodes-base.postgres",
                              query="SELECT * FROM u WHERE id = {{ $json.id }}")]}
        r = gate.evaluate_to_dict(wf)
        assert any("SQL_INJECTION" in v for v in r["violations"])

    def test_metadata_leak_flagged(self):
        gate = SecurityGate(rules_dir=None)
        wf = {"nodes": [], "meta": {"instanceId": "abc-123"}}
        r = gate.evaluate_to_dict(wf)
        assert any("METADATA_LEAK" in v for v in r["violations"])

    def test_community_node_flagged(self):
        gate = SecurityGate(rules_dir=None)
        wf = {"nodes": [_node("X", "n8n-nodes-community.evil",
                              url="https://api.example.com")]}
        r = gate.evaluate_to_dict(wf)
        assert any("COMMUNITY_NODE" in v for v in r["violations"])

    def test_verbose_error_flagged(self):
        gate = SecurityGate(rules_dir=None)
        wf = {"nodes": [_node("R", "n8n-nodes-base.respondToWebhook",
                              responseBody="{{ $json }}")]}
        r = gate.evaluate_to_dict(wf)
        assert any("VERBOSE_ERROR" in v for v in r["violations"])

    def test_clean_public_workflow_approved(self):
        gate = SecurityGate(rules_dir=None)
        wf = {"nodes": [
            _node("W", "n8n-nodes-base.webhook",
                  path="h", authentication="headerAuth"),
            _node("H", "n8n-nodes-base.httpRequest",
                  url="https://api.example.com/x")]}
        assert gate.evaluate_to_dict(wf)["status"] == "APPROVED"


# ---------------------------------------------------------------------------
# QualityGate — n8n-native names not penalized; bare expressions scored
# ---------------------------------------------------------------------------

class TestQualityN8nNative:
    def test_idiomatic_names_not_deducted(self):
        wf = {"nodes": [
            _node("Webhook", "n8n-nodes-base.webhook",
                  path="x", pinnedData={"1": {}}),
            _node("HTTP Request", "n8n-nodes-base.httpRequest",
                  url="https://api.example.com")],
            "connections": {"Webhook": {"main": [{"node": "HTTP Request"}]}}}
        r = QualityGate().evaluate_to_dict(wf)
        assert r["status"] == "PASSED"
        assert not any("verb-prefixed" in v and "non-blocking" not in v
                       for v in r["violations"])

    def test_bare_expression_deducts(self):
        wf = {"nodes": [_node("Set Name", "n8n-nodes-base.set",
                              assignments={"assignments": [
                                  {"name": "n", "value": "$json.body.name",
                                   "type": "string"}]})],
              "connections": {}}
        r = QualityGate().evaluate_to_dict(wf)
        assert any("bare/malformed" in v for v in r["violations"])

    def test_missing_equals_prefix_deducts(self):
        wf = {"nodes": [_node("Set Name", "n8n-nodes-base.set",
                              assignments={"assignments": [
                                  {"name": "n", "value": "{{ $json.a }}",
                                   "type": "string"}]})],
              "connections": {}}
        r = QualityGate().evaluate_to_dict(wf)
        assert any("bare/malformed" in v for v in r["violations"])

    def test_deprecated_function_node_flagged(self):
        wf = {"nodes": [_node("Do Thing", "n8n-nodes-base.function")],
              "connections": {}}
        r = QualityGate().evaluate_to_dict(wf)
        assert any("deprecated Function" in v for v in r["violations"])


# ---------------------------------------------------------------------------
# PrecisionGate — Package I FAILs, Package J warnings
# ---------------------------------------------------------------------------

def _trigger():
    return _node("Start", "n8n-nodes-base.manualTrigger")


class TestPrecisionPackageIJ:
    def test_i2_internal_url_fails(self):
        wf = {"nodes": [_trigger(),
                        _node("H", "n8n-nodes-base.httpRequest",
                              url="http://10.0.0.5/x", authentication="none")],
              "connections": {"Start": {"main": [[{"node": "H"}]]}}}
        r = N8nPrecisionGate().run(wf, {})
        assert r["status"] == "FAIL"
        assert any(v.startswith("I2:") for v in r["violations"])

    def test_i3_fromai_outside_tool_fails(self):
        wf = {"nodes": [_trigger(),
                        _node("C", "n8n-nodes-base.code",
                              jsCode="return [{json:{v: $fromAI('x')}}];")],
              "connections": {"Start": {"main": [[{"node": "C"}]]}}}
        r = N8nPrecisionGate().run(wf, {})
        assert r["status"] == "FAIL"
        assert any(v.startswith("I3:") for v in r["violations"])

    def test_i3_fromai_inside_tool_ok(self):
        wf = {"nodes": [_trigger(),
                        _node("Agent", "@n8n/n8n-nodes-langchain.agent",
                              maxIterations=5,
                              options={"systemMessage": "do",
                                       "maxIterations": 5}),
                        _node("Tool", "@n8n/n8n-nodes-langchain.toolCode",
                              jsCode="return $fromAI('x');")],
              "connections": {
                  "Start": {"main": [[{"node": "Agent"}]]},
                  "Tool": {"ai_tool": [[{"node": "Agent"}]]}}}
        r = N8nPrecisionGate().run(wf, {})
        assert not any(v.startswith("I3:") for v in r["violations"])

    def test_j1_j2_warn_only(self):
        wf = {"nodes": [_trigger(),
                        _node("S", "n8n-nodes-base.set",
                              assignments={"assignments": [
                                  {"name": "a", "value": "$json.x",
                                   "type": "string"},
                                  {"name": "b", "value": "{{ $json.y }}",
                                   "type": "string"}]})],
              "connections": {"Start": {"main": [[{"node": "S"}]]}}}
        r = N8nPrecisionGate().run(wf, {})
        assert r["status"] == "PASS"
        assert any(w.startswith("J1:") for w in r["warnings"])
        assert any(w.startswith("J2:") for w in r["warnings"])

    def test_j3_merge_single_input_warns(self):
        wf = {"nodes": [_trigger(),
                        _node("A", "n8n-nodes-base.set", assignments={}),
                        _node("M", "n8n-nodes-base.merge", mode="append")],
              "connections": {"Start": {"main": [[{"node": "A"}]]},
                              "A": {"main": [[{"node": "M"}]]}}}
        r = N8nPrecisionGate().run(wf, {})
        assert any(w.startswith("J3:") for w in r["warnings"])

    def test_j4_schedule_without_timezone_warns(self):
        wf = {"nodes": [_node("Cron", "n8n-nodes-base.scheduleTrigger",
                              rule={"interval": [{"field": "hours"}]}),
                        _node("N", "n8n-nodes-base.noOp")],
              "connections": {"Cron": {"main": [[{"node": "N"}]]}}}
        r = N8nPrecisionGate().run(wf, {})
        assert any(w.startswith("J4:") for w in r["warnings"])


# ---------------------------------------------------------------------------
# RAG R4 is FAIL + auto-fixed POST -> PUT; DryRun accepts all pinned shapes
# ---------------------------------------------------------------------------

class TestRagR4AndDryRun:
    def test_r4_post_upsert_fails_and_autofixes(self):
        n = {"id": "Q", "name": "Q HTTP", "type": "n8n-nodes-base.httpRequest",
             "typeVersion": 1, "position": [0, 0],
             "parameters": {"method": "POST",
                            "url": "https://x.qdrant.io/collections/d/points"}}
        r = RagVectorGate().run({"nodes": [n], "connections": {}})
        assert r["status"] == "FAIL"
        assert any("R4" in v for v in r["violations"])

    def test_dryrun_accepts_node_level_pinned(self):
        wf = {"nodes": [
            {"id": "t", "name": "Start", "type": "n8n-nodes-base.manualTrigger",
             "typeVersion": 1, "position": [0, 0], "parameters": {},
             "pinnedData": [{"json": {"a": 1}}]}]}
        r = DryRunGate().run(wf, {})
        assert r["status"] == "PASS"

    def test_dryrun_accepts_root_pinned_map(self):
        wf = {"nodes": [
            {"id": "t", "name": "Start", "type": "n8n-nodes-base.manualTrigger",
             "typeVersion": 1, "position": [0, 0], "parameters": {}}],
            "pinnedData": {"Start": [{"json": {"a": 1}}]}}
        r = DryRunGate().run(wf, {})
        assert r["status"] == "PASS"

    def test_pipeline_blocks_secret_leaking_workflow(self):
        wf = {"nodes": [
            _node("Start", "n8n-nodes-base.manualTrigger"),
            _node("H", "n8n-nodes-base.httpRequest",
                  url="https://api.example.com/x?api_key=SECRET1234567890")],
            "connections": {"Start": {"main": [[{"node": "H"}]]}}}
        res = _run(wf, enable_autofix=False)
        assert res["verdict"] != "READY_FOR_DEPLOYMENT"
        sec = res["stages"]["security"]
        assert sec["status"] == "REJECTED_SECURITY_RISK"
