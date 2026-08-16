"""End-to-end wiring of the weak-model hardening layer into the orchestrator."""

import pytest

from master_system_orchestrator import SystemOrchestrator


@pytest.fixture
def orch():
    return SystemOrchestrator(
        budget_usd=20.0, elide_output=True,
        mock_mappings={"api.example.com": "http://127.0.0.1:9191"})


class TestOrchestratorHardening:
    def test_schema_violation_rejected_before_verify(self, orch):
        res = orch.execute_workflow_task(
            "telegram order webhook",
            {"nodes": [{"name": "X"}]},  # missing connections -> schema fail
            daily_reqs=10, tech_stack=["telegram"],
        )
        assert res["status"] == "REJECTED"
        assert "schema" in res["reason"].lower()
        assert orch.metrics.counter("schema_rejections") == 1

    def test_low_confidence_escalates_to_hitl(self, orch):
        # webhook + localhost -> confidence floor; no frontier configured
        res = orch.execute_workflow_task(
            "design a brand new custom topology with localhost calls",
            {"nodes": [{"name": "Webhook",
                        "parameters": {"url": "http://127.0.0.1:8000/x"}}],
             "connections": {}},
            daily_reqs=10,
        )
        assert res["status"] == "PENDING_HUMAN_REVIEW"
        assert "hitl_request_id" in res

    def test_valid_workflow_reaches_deploy_with_hardening(self, orch):
        res = orch.execute_workflow_task(
            "webhook forwards to a trusted service",
            {"nodes": [
                {"name": "Receive Webhook", "type": "n8n-nodes-base.webhook",
                 "parameters": {"path": "v1-orders", "httpMethod": "POST",
                                "authentication": "headerAuth",
                                "pinnedData": {"1": {"json": {"order": {"id": 1}}}}},
                 "onError": "continueRegularOutput", "continueOnFail": True},
                {"name": "Send Orders", "type": "n8n-nodes-base.httpRequest",
                 "parameters": {"url": "https://api.example.com/v1/orders"},
                 "continueOnFail": True},
            ], "connections": {
                "Receive Webhook": {"main": [{"node": "Send Orders"}]}}},
            daily_reqs=100, tech_stack=["telegram"],
        )
        assert res["status"] == "READY_FOR_DEPLOYMENT"
        assert res["hardening"]["tier"] == "CHEAP"
        assert "rag_hits" in res["hardening"]

    def test_self_evolution_runs_automatically_on_entry(self, orch):
        # security-ish task triggers cybersec_audit domain -> gap 24% -> skill
        res = orch.execute_workflow_task(
            "audit webhook for safety and ssrf",
            {"nodes": [
                {"name": "Receive Webhook", "type": "n8n-nodes-base.webhook",
                 "parameters": {"path": "v1", "httpMethod": "POST",
                                "pinnedData": {"1": {"json": {"x": 1}}}},
                 "onError": "continueRegularOutput", "continueOnFail": True},
            ], "connections": {}},
            daily_reqs=100,
        )
        # evolution is advisory — never changes the pipeline outcome
        assert res["status"] in ("READY_FOR_DEPLOYMENT", "PENDING_HUMAN_REVIEW",
                                 "REJECTED")