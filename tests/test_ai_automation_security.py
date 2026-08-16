"""Tests for the 8 AI-automation security rules in security_gate.py."""
import pytest

from security_gate import SecurityGate, RISK_THRESHOLD


@pytest.fixture
def gate():
    return SecurityGate()


def _agent(name="Agent", **params):
    return {"name": name, "type": "n8n-nodes-langchain.agent",
            "parameters": params}


def _wf(nodes, connections=None):
    return {"nodes": nodes, "connections": connections or {}}


# --- R1: Tool Scope Lock -----------------------------------------------
class TestToolScopeLock:
    def test_wildcard_tools_rejected(self, gate):
        n = _agent(tools=["*"], options={"maxIterations": 10})
        r = gate.evaluate_to_dict(_wf([n]))
        assert r["status"] == "REJECTED_SECURITY_RISK"
        assert any("TOOL_SCOPE_LOCK" in v for v in r["violations"])

    def test_string_all_tools_rejected(self, gate):
        n = _agent(tools="all", options={"maxIterations": 10})
        r = gate.evaluate_to_dict(_wf([n]))
        assert r["status"] == "REJECTED_SECURITY_RISK"
        assert any("TOOL_SCOPE_LOCK" in v for v in r["violations"])

    def test_undefined_tools_rejected(self, gate):
        n = _agent(options={"maxIterations": 10})
        r = gate.evaluate_to_dict(_wf([n]))
        assert r["status"] == "REJECTED_SECURITY_RISK"
        assert any("TOOL_SCOPE_LOCK" in v for v in r["violations"])

    def test_explicit_limited_tools_ok(self, gate):
        n = _agent(tools=["read_file"], options={"maxIterations": 10})
        r = gate.evaluate_to_dict(_wf([n]))
        assert r["status"] == "APPROVED"
        assert not any("TOOL_SCOPE_LOCK" in v for v in r["violations"])


# --- R2: Prompt injection detection + auto-remediation ------------------
class TestPromptInjectionAutoFix:
    def test_raw_json_input_wrapped(self, gate):
        n = _agent(options={"systemMessage": "Do task with {{ $json.body }}.",
                            "maxIterations": 10})
        r = gate.evaluate_to_dict(_wf([n]))
        assert any("UNSANITIZED_EXTERNAL_INPUT_IN_PROMPT" in v
                   for v in r["violations"])
        assert any("wrapped" in f for f in r["auto_fixes"])
        # the fix persists onto the node's systemMessage
        sysmsg = n["parameters"]["options"]["systemMessage"]
        assert "<untrusted_external_data" in sysmsg
        assert "$json" in sysmsg

    def test_clean_prompt_no_fix(self, gate):
        n = _agent(options={"systemMessage": "You are a helpful assistant.",
                            "maxIterations": 10})
        r = gate.evaluate_to_dict(_wf([n]))
        assert not any("UNSANITIZED_EXTERNAL_INPUT_IN_PROMPT" in v
                       for v in r["violations"])
        assert r["auto_fixes"] == []

    def test_already_wrapped_not_double_fixed(self, gate):
        msg = ("task only. <untrusted_external_data source=\"$json\">"
               "{{ $json.x }}</untrusted_external_data>")
        n = _agent(options={"systemMessage": msg, "maxIterations": 10})
        r = gate.evaluate_to_dict(_wf([n]))
        assert not any("UNSANITIZED_EXTERNAL_INPUT_IN_PROMPT" in v
                       for v in r["violations"])


# --- R3: Credential-to-Tool Binding -------------------------------------
class TestCredentialToolBinding:
    def test_high_risk_tool_no_approval(self, gate):
        n = _agent(tools=["delete_user", "read_file"],
                   options={"maxIterations": 10})
        r = gate.evaluate_to_dict(_wf([n]))
        assert any("STATE_CHANGING_TOOL_NO_APPROVAL" in v
                   for v in r["violations"])

    def test_high_risk_tool_with_approval_ok(self, gate):
        n = _agent(tools=["delete_user"],
                   options={"maxIterations": 10},
                   requiresHumanApproval=True)
        r = gate.evaluate_to_dict(_wf([n]))
        assert not any("STATE_CHANGING_TOOL_NO_APPROVAL" in v
                       for v in r["violations"])

    def test_safe_tools_ok(self, gate):
        n = _agent(tools=["read_file", "search"], options={"maxIterations": 10})
        r = gate.evaluate_to_dict(_wf([n]))
        assert not any("STATE_CHANGING_TOOL_NO_APPROVAL" in v
                       for v in r["violations"])


# --- R4: Chained high-risk actions (two-tier) ---------------------------
class TestChainedHighRisk:
    def test_single_destructive_is_fatal(self, gate):
        n = {"name": "D", "type": "n8n-nodes-base.googleSheets",
             "parameters": {"operation": "delete", "resource": "row"}}
        r = gate.evaluate_to_dict(_wf([n]))
        assert r["status"] == "REJECTED_SECURITY_RISK"
        assert any("DESTRUCTIVE_ACTION_NO_APPROVAL" in v for v in r["violations"])

    def test_destructive_with_approval_ok(self, gate):
        n = {"name": "D", "type": "n8n-nodes-base.googleSheets",
             "parameters": {"operation": "delete", "resource": "row",
                            "requiresHumanApproval": True}}
        r = gate.evaluate_to_dict(_wf([n]))
        assert r["status"] == "APPROVED"

    def test_reversible_write_x3_warns_but_passes(self, gate):
        nodes = [{"name": f"s{i}", "type": "n8n-nodes-base.slack",
                  "parameters": {"operation": "send", "resource": "message"}}
                 for i in range(3)]
        r = gate.evaluate_to_dict(_wf(nodes))
        assert r["status"] == "APPROVED"  # MEDIUM only, not fatal
        assert any("REPEATED_SAME_WRITE_ACTION" in v for v in r["violations"])

    def test_different_writes_ok(self, gate):
        nodes = [
            {"name": "s1", "type": "n8n-nodes-base.slack",
             "parameters": {"operation": "send", "resource": "message"}},
            {"name": "s2", "type": "n8n-nodes-base.slack",
             "parameters": {"operation": "post", "resource": "message"}},
            {"name": "s3", "type": "n8n-nodes-base.httpRequest",
             "parameters": {"url": "https://api.example.com/x"}},
        ]
        r = gate.evaluate_to_dict(_wf(nodes))
        assert not any("REPEATED_SAME_WRITE_ACTION" in v for v in r["violations"])


# --- R5: Webhook auth enforcement ---------------------------------------
class TestWebhookAuth:
    def test_unauthed_webhook_rejected(self, gate):
        n = {"name": "W", "type": "n8n-nodes-base.webhook",
             "parameters": {"path": "x"}}
        r = gate.evaluate_to_dict(_wf([n]))
        assert r["status"] == "REJECTED_SECURITY_RISK"
        assert any("WEBHOOK_NO_AUTH" in v for v in r["violations"])

    def test_header_auth_webhook_ok(self, gate):
        n = {"name": "W", "type": "n8n-nodes-base.webhook",
             "parameters": {"path": "x", "authentication": "headerAuth"}}
        r = gate.evaluate_to_dict(_wf([n]))
        assert r["status"] == "APPROVED"
        assert not any("WEBHOOK_NO_AUTH" in v for v in r["violations"])

    def test_basic_auth_webhook_ok(self, gate):
        n = {"name": "W", "type": "n8n-nodes-base.webhook",
             "parameters": {"path": "x", "authentication": "basicAuth"}}
        r = gate.evaluate_to_dict(_wf([n]))
        assert r["status"] == "APPROVED"


# --- R6: No secrets in agent memory -------------------------------------
class TestSecretInAgentMemory:
    def test_secret_in_prompt_rejected(self, gate):
        n = _agent(options={"systemMessage": "key is sk-abcdefghijklmnopqrstuvwxyz1234567890",
                            "maxIterations": 10})
        r = gate.evaluate_to_dict(_wf([n]))
        assert any("SECRET_IN_AGENT_MEMORY" in v for v in r["violations"])
        assert r["status"] == "REJECTED_SECURITY_RISK"

    def test_clean_prompt_ok(self, gate):
        n = _agent(tools=["read_file"],
                   options={"systemMessage": "you are helpful.",
                            "maxIterations": 10})
        r = gate.evaluate_to_dict(_wf([n]))
        assert not any("SECRET_IN_AGENT_MEMORY" in v for v in r["violations"])


# --- R7: Rate/cost ceiling ----------------------------------------------
class TestIterationCeiling:
    def test_undefined_max_iterations_warns(self, gate):
        n = _agent(tools=["read_file"])
        r = gate.evaluate_to_dict(_wf([n]))
        assert any("NO_ITERATION_CEILING" in v for v in r["violations"])

    def test_too_high_max_iterations_warns(self, gate):
        n = _agent(tools=["read_file"], options={"maxIterations": 50})
        r = gate.evaluate_to_dict(_wf([n]))
        assert any("NO_ITERATION_CEILING" in v for v in r["violations"])

    def test_sane_max_iterations_ok(self, gate):
        n = _agent(tools=["read_file"], options={"maxIterations": 10})
        r = gate.evaluate_to_dict(_wf([n]))
        assert not any("NO_ITERATION_CEILING" in v for v in r["violations"])


# --- R8: Output destination validation ----------------------------------
class TestLLMControlledDestination:
    def test_agent_picked_url_rejected(self, gate):
        n1 = _agent(name="Orchestrator", tools=["read_file"],
                    options={"maxIterations": 10})
        n2 = {"name": "H", "type": "n8n-nodes-base.httpRequest",
              "parameters": {"url": "{{ $json.urlFromAgent }}"}}
        r = gate.evaluate_to_dict(_wf(
            [n1, n2],
            {"Orchestrator": {"main": [{"node": "H"}]}}))
        assert any("LLM_CONTROLLED_DESTINATION" in v for v in r["violations"])
        assert r["status"] == "REJECTED_SECURITY_RISK"

    def test_dynamic_url_without_agent_upstream_ok(self, gate):
        # dynamic URL but the HTTP node does NOT sit downstream of any agent
        n1 = _agent(name="Orchestrator", tools=["read_file"],
                    options={"maxIterations": 10})
        n2 = {"name": "H", "type": "n8n-nodes-base.httpRequest",
              "parameters": {"url": "{{ $json.urlFromTrigger }}"}}
        r = gate.evaluate_to_dict(_wf([n1, n2]))
        assert not any("LLM_CONTROLLED_DESTINATION" in v for v in r["violations"])

    def test_static_url_ok(self, gate):
        n = {"name": "H", "type": "n8n-nodes-base.httpRequest",
             "parameters": {"url": "https://api.example.com/v1"}}
        r = gate.evaluate_to_dict(_wf([n]))
        assert not any("LLM_CONTROLLED_DESTINATION" in v for v in r["violations"])
