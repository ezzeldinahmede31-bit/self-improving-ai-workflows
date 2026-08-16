"""Tests for the 4 Cognitive & Cybersecurity modules:

1. Extended Thinking & Dual-Process Planner   (dual_process_planner.py)
2. Adversarial Red-Team Agent                 (cybersec_sandbox_engine.py)
3. Execution-Guided Coding Sandbox            (cybersec_sandbox_engine.py)
4. Zero-Trust Secret Redactor & Vault         (secret_redactor.py)
Plus integration tests proving the orchestrator now runs them in order.
"""

import json

import pytest

from dual_process_planner import ExtendedThinkingPlanner
from cybersec_sandbox_engine import CyberSecRedTeamAgent, ExecutionSandbox
from secret_redactor import SecretRedactor, SecretVault
from master_system_orchestrator import SystemOrchestrator


# ---------------------------------------------------------------------------
# Module 1 — Dual-Process Planner
# ---------------------------------------------------------------------------

class TestExtendedThinkingPlanner:
    def test_dag_structure(self):
        plan = ExtendedThinkingPlanner().plan_dag("x", ["telegram", "supabase"])
        assert plan[0].id == "trigger"
        assert plan[-1].id == "join"
        assert plan[-1].deps  # join depends on the calls

    def test_tree_of_thought_tracks_cost(self):
        p = ExtendedThinkingPlanner()
        dag = p.plan_dag("task", ["a", "b"])
        paths = p.tree_of_thought(dag)
        assert len(paths) == 3  # 3 distinct architectures
        selected = p.score_and_select(paths, budget_usd=20)
        assert selected is not None
        # A: Streamlined must win for a small task
        assert selected.name.startswith("A")

    def test_path_self_evaluation_rejects_over_budget(self):
        p = ExtendedThinkingPlanner(budget_usd=0.5)
        dag = p.plan_dag("huge", ["w", "x", "y", "z"])
        paths = p.tree_of_thought(dag)
        # C: Multi-Agent (est tokens ~12000+) exceeds half of $0.5 -> REJECTED
        selected = p.score_and_select(paths, budget_usd=0.5)
        assert selected is not None

    def test_tactical_build_steps_are_grounded(self):
        p = ExtendedThinkingPlanner()
        dag = p.plan_dag("t", ["openai"])
        sel = p.score_and_select(p.tree_of_thought(dag), budget_usd=20)
        steps = p.tactical_build_steps(sel, services=["openai"])
        joined = "\n".join(steps)
        assert "SecurityGate" in joined
        assert "http" in joined.lower()

    def test_plan_task_returns_rationale(self):
        plan = ExtendedThinkingPlanner().plan_task("telegram → db", ["telegram"])
        assert plan.selected is not None
        assert plan.selected.name in plan.rationale
        assert len(plan.build_steps) >= 4


# ---------------------------------------------------------------------------
# Module 2 — Adversarial Red-Team Agent
# ---------------------------------------------------------------------------

class TestCyberSecRedTeamAgent:
    def test_injection_detection_in_js_code(self):
        rt = CyberSecRedTeamAgent()
        wf = {"nodes": [{"name": "Code", "type": "n8n-nodes-base.code",
                         "parameters": {"jsCode": "require('child_process').exec('rm -rf /')"}}]}
        rep = rt.audit_workflow(wf)
        assert not rep["red_team_passed"]
        assert "injection" in rep["vectors"]
        assert rep["max_severity"] >= 7

    def test_ssrf_detection_metadata_loopback(self):
        rt = CyberSecRedTeamAgent()
        wf = {"nodes": [{"name": "SSRF", "type": "n8n-nodes-base.httpRequest",
                         "parameters": {"url": "http://169.254.169.254/latest/meta-data"}}]}
        rep = rt.audit_workflow(wf)
        assert "ssrf" in rep["vectors"]
        assert not rep["red_team_passed"]

    def test_ssrf_localhost_n8n_canary(self):
        rt = CyberSecRedTeamAgent()
        wf = {"nodes": [{"name": "T", "type": "n8n-nodes-base.httpRequestTool",
                         "parameters": {"url": "http://127.0.0.1:5678/rest/config"}}]}
        rep = rt.audit_workflow(wf)
        assert "ssrf" in rep["vectors"]

    def test_secret_exfiltration_to_untrusted_hook(self):
        rt = CyberSecRedTeamAgent()
        wf = {"nodes": [{"name": "Hook", "type": "n8n-nodes-base.httpRequest",
                         "parameters": {"url": "https://webhook.site/0000",
                                        "headerParameters": {"parameters": [
                                            {"name": "Authorization",
                                             "value": "Bearer sk-proj-abcdefghijklmnopqrstuvwxyz1234567890"}]}}}]}
        rep = rt.audit_workflow(wf)
        assert "exfiltration" in rep["vectors"]
        assert not rep["red_team_passed"]

    def test_owasp_unauthed_mutating_webhook(self):
        rt = CyberSecRedTeamAgent()
        wf = {"nodes": [{"name": "W", "type": "n8n-nodes-base.webhook",
                         "parameters": {"httpMethod": "DELETE", "path": "drop"}}]}
        rep = rt.audit_workflow(wf)
        assert "api_auth" in rep["vectors"]
        # DELETE unauthenticated = severity 7
        assert rep["max_severity"] >= 7

    def test_clean_workflow_passes(self):
        rt = CyberSecRedTeamAgent()
        wf = {"nodes": [{"name": "G", "type": "n8n-nodes-base.httpRequest",
                         "parameters": {"url": "https://api.example.com/v1/x",
                                        "authentication": "genericCredentialType"}}]}
        rep = rt.audit_workflow(wf)
        assert rep["red_team_passed"]
        assert rep["vulnerabilities"] == []

    def test_audit_text_finds_secret(self):
        rt = CyberSecRedTeamAgent()
        rep = rt.audit_text("token=ghp_abcdefghijklmnopqrstuvwxyz123456789")
        assert not rep["red_team_passed"]
        assert "exfiltration" in rep["vectors"]


# ---------------------------------------------------------------------------
# Module 3 — Execution-Guided Coding Sandbox
# ---------------------------------------------------------------------------

class TestExecutionSandbox:
    def test_local_fallback_success(self, monkeypatch):
        s = ExecutionSandbox(use_docker=False)
        res = s.run_python("print(6 * 7)")
        assert res.get("success") is True
        assert res["output"] == "42"
        assert res["sandbox"] == "local_fallback"

    def test_local_fallback_traceback(self, monkeypatch):
        s = ExecutionSandbox(use_docker=False)
        res = s.run_python("x = 1/0")
        assert res.get("success") is False
        assert "ZeroDivisionError" in res.get("error", "")

    def test_local_fallback_timeout_killed(self, monkeypatch):
        s = ExecutionSandbox(use_docker=False, timeout_sec=1)
        res = s.run_python("while True: pass")
        assert res.get("success") is False
        assert "Timeout" in res.get("error", "")

    def test_self_heal_retries_on_traceback(self, monkeypatch):
        s = ExecutionSandbox(use_docker=False, max_retries=1)
        retry = {  # first attempt bad, retry fixes it
            "retry_0": "print('fixed')",
        }
        res = s.self_heal("raise ValueError('boom')", retry_code=retry)
        assert res.get("success") is True
        assert res["output"] == "fixed"

    def test_self_heal_exhausts_retries(self, monkeypatch):
        s = ExecutionSandbox(use_docker=False, max_retries=1)
        res = s.self_heal("raise RuntimeError('stubborn')")
        assert res.get("success") is False
        assert res["attempts"] == 2


# ---------------------------------------------------------------------------
# Module 4 — Zero-Trust Secret Redactor & Vault
# ---------------------------------------------------------------------------

class TestSecretRedactor:
    def test_masks_openai_key(self):
        r = SecretRedactor()
        res = r.scan_and_redact({"api_key": "sk-proj-aBcDeFgHiJkLmNoPqRsTuVwXyZ123456"})
        assert res["found"]
        assert "sk-proj" not in res["redacted"]
        assert "$env.REDACTED_" in res["redacted"]

    def test_masks_jwt_and_bearer(self):
        r = SecretRedactor()
        jwt = "eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJzdWIiOiCJkabCx.eyJhIjoiQiJ9.abc"
        res = r.scan_and_redact({"auth": f"Bearer {jwt}"})
        assert res["found"]

    def test_entropy_catch_base64_blob(self):
        r = SecretRedactor()
        blob = "K9uMp2xQwErTyUiOpAsDfGhJkLzXcVbN" * 2
        res = r.scan_and_redact({"blob": blob})
        assert res["found"], "high-entropy token should be caught"

    def test_clean_text_untouched(self):
        r = SecretRedactor()
        res = r.scan_and_redact("plain status message here")
        assert res["found"] == []
        assert res["redacted"] == "plain status message here"

    def test_vault_inject_roundtrip(self):
        v = SecretVault()
        secret = "sk-123456789012345678901234567890"
        payload = {"auth": secret}
        red, found = v.register_payload(payload)
        assert found
        assert secret not in red
        restored = v.inject(red)
        assert secret in restored

    def test_vault_sweep_clears(self):
        v = SecretVault()
        v.register_payload({"k": "ghp_abcdefghijklmnopqrstuvwxyz1234567890"})
        v.sweep()
        assert len(v._store) == 0


# ---------------------------------------------------------------------------
# Integration — orchestrator runs the 4 engines in order
# ---------------------------------------------------------------------------

class TestOrchestratorIntegration:
    def setup_method(self):
        self.orch = SystemOrchestrator(
            budget_usd=20.0,
            elide_output=True,
            mock_mappings={"api.example.com": "http://127.0.0.1:9191"},
        )

    @staticmethod
    def _valid_flow(extra_http_nodes=None):
        """A workflow that passes QualityGate (verb names + pinnedData +
        continueOnFail) so only security/cognitive checks decide the route."""
        nodes = [
            {"name": "Receive Webhook", "type": "n8n-nodes-base.webhook",
             "parameters": {"path": "v1-orders", "httpMethod": "POST",
                            "authentication": "headerAuth",
                            "pinnedData": {"1": {"json": {"order": {"id": 1}}}}},
             "onError": "continueRegularOutput", "continueOnFail": True},
            {"name": "Send Supabase", "type": "n8n-nodes-base.httpRequest",
             "parameters": {"url": "https://api.example.com/v1/orders"},
             "continueOnFail": True},
        ]
        if extra_http_nodes:
            nodes += extra_http_nodes
        return {"nodes": nodes, "connections": {
            "Receive Webhook": {"main": [{"node": "Send Supabase"}]}}}

    def test_planner_run_inside_orchestrator(self):
        res = self.orch.execute_workflow_task(
            "telegram webhook → supabase insert", self._valid_flow(),
            daily_reqs=500, tech_stack=["telegram", "supabase", "deepseek"])
        # clean + safe -> READY_FOR_DEPLOYMENT (mock mapping routable, no secrets)
        assert res["status"] == "READY_FOR_DEPLOYMENT"

    def test_red_team_overrides_decision_to_hitl(self):
        bad = {"nodes": [
            {"name": "Sync Internal", "type": "n8n-nodes-base.httpRequest",
             "parameters": {"url": "http://127.0.0.1:5678/rest/config"},
             "continueOnFail": True},
        ], "connections": {}}
        res = self.orch.execute_workflow_task(
            "sync internal n8n config", bad,
            daily_reqs=10, tech_stack=["deepseek"])
        assert res["status"] == "PENDING_HUMAN_REVIEW"
        assert res.get("hitl_request_id")
        assert "Red-Team" in res.get("reason", "")

    def test_secret_redaction_before_processing(self):
        flow = {"nodes": [
            {"name": "Call API", "type": "n8n-nodes-base.httpRequest",
             "parameters": {"url": "https://api.example.com/v1/c",
                            "headerParameters": {"parameters": [
                                {"name": "Authorization",
                                 "value": "Bearer sk-proj-abcdefghijklmnopqrstuvwxyz1234567890"}]}},
             "continueOnFail": True},
        ], "connections": {}}
        res = self.orch.execute_workflow_task(
            "post to external api", flow,
            daily_reqs=10, tech_stack=["deepseek"])
        # hardcoded bearer token -> red-team exfiltration -> HITL
        assert res["status"] == "PENDING_HUMAN_REVIEW"
        # the storage copy must NOT contain the secret
        assert "sk-proj" not in self.orch._redacted_storage_copy

    def test_runtime_sandbox_gates_destroying_code(self):
        # Python Code node with harmful import cannot silently pass: sandbox sees
        # ValueError-like runtime during self-heal (attempted fix fails -> REJECTED)
        # We craft one whose python raises despite any retry.
        flow = {"nodes": [
            {"name": "Scheduled Cleanup", "type": "n8n-nodes-base.code",
             "parameters": {"pythonCode": "raise ValueError('unsafe op')"}},
        ], "connections": {}}
        res = self.orch.execute_workflow_task(
            "scheduled cleanup script", flow,
            daily_reqs=10, tech_stack=["deepseek"])
        assert res["status"] == "REJECTED"
        assert res.get("reason") == "Execution sandbox runtime failure"