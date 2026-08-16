import pytest
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from master_system_orchestrator import (
    BrutallyHonestBudgetAnalyzer,
    TaskScopedJITRAG,
    SystemOrchestrator,
)
from hitl_gate import HITLState


class TestBudgetAnalyzer:
    def test_viable_small_scale(self):
        a = BrutallyHonestBudgetAnalyzer.audit_task(
            monthly_budget_usd=20.0, daily_requests=100, avg_tokens=800,
            proposed_tech_stack=["deepseek"],
        )
        assert a["viable"] is True
        assert a["est_cost_deepseek_chat"] < 20.0

    def test_low_budget_viable_deepseek(self):
        a = BrutallyHonestBudgetAnalyzer.audit_task(
            monthly_budget_usd=5.0, daily_requests=100, avg_tokens=800,
            proposed_tech_stack=["deepseek"],
        )
        assert a["viable"] is True

    def test_budget_violation_when_requests_skyrocket(self):
        a = BrutallyHonestBudgetAnalyzer.audit_task(
            monthly_budget_usd=1.0, daily_requests=100000, avg_tokens=800,
            proposed_tech_stack=["claude-3-5-sonnet"],
        )
        # sonnet is way too expensive at 3M req/mo
        assert a["viable"] is False

    def test_vector_db_overengineering_flagged_low_volume(self):
        a = BrutallyHonestBudgetAnalyzer.audit_task(
            monthly_budget_usd=20.0, daily_requests=100, avg_tokens=800,
            proposed_tech_stack=["vector_db"],
        )
        assert a["viable"] is True
        assert any("OVER-ENGINEERING" in n for n in a["critique_notes"])

    def test_no_overengineering_at_scale(self):
        a = BrutallyHonestBudgetAnalyzer.audit_task(
            monthly_budget_usd=20.0, daily_requests=1000, avg_tokens=800,
            proposed_tech_stack=["vector_db"],
        )
        # 30k requests — vector DB may be justified
        assert not any("OVER-ENGINEERING" in n for n in a["critique_notes"])

    def test_postgres_flagged_at_low_scale(self):
        a = BrutallyHonestBudgetAnalyzer.audit_task(
            monthly_budget_usd=20.0, daily_requests=100, avg_tokens=800,
            proposed_tech_stack=["postgres"],
        )
        assert any("Postgres" in n for n in a["critique_notes"])

    def test_budget_matrix_model_pricing(self):
        # local qwen should be free
        a = BrutallyHonestBudgetAnalyzer.audit_task(
            monthly_budget_usd=50.0, daily_requests=10000, avg_tokens=800,
            proposed_tech_stack=["qwen2.5-coder:7b"],
        )
        assert a["est_cost_local_qwen"] == 0.0


class TestTaskScopedJITRAG:
    def test_isolated_purge(self):
        rag = TaskScopedJITRAG("test task")
        rag.ingest_jit_docs([
            {"source": "Telegram", "doc_type": "rate_limits",
             "content": "max 4096 bytes", "keywords": ["telegram", "limit"]},
        ])
        results = rag.query_context("4096")
        assert results and "4096" in results[0]["content"]
        # purge removes the file
        assert rag.purge_context() is True
        assert not os.path.exists(rag.db_path)

    def test_query_scoped_to_keyword(self):
        rag = TaskScopedJITRAG("task")
        rag.ingest_jit_docs([
            {"source": "A", "content": "telegram webhook needs HTTPS", "keywords": []},
            {"source": "B", "content": "stripe idempotency-key required", "keywords": []},
        ])
        hits = rag.query_context("stripe")
        assert all("stripe" in h["content"] for h in hits)

    def test_purge_idempotent(self):
        rag = TaskScopedJITRAG("t")
        assert rag.purge_context() is True
        assert rag.purge_context() is False  # already gone


class TestOrchestrator:
    def _mock_token(self):
        return "orchestrator-test-token"

    def test_read_deploy_path(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        orch = SystemOrchestrator(budget_usd=20.0, elide_output=True)
        flow = {
            "nodes": [
                {"name": "Telegram Webhook",
                 "type": "n8n-nodes-base.webhook",
                 "parameters": {"path": "x", "pinnedData": {"1": {"json": {}}},
                                "authentication": "headerAuth"}},
                {"name": "Send Supabase", "type": "n8n-nodes-base.httpRequest",
                 "parameters": {"url": "https://supabase.co/rest/v1/orders"}},
            ],
            "connections": {
                "Telegram Webhook": {"main": [{"node": "Send Supabase"}]},
            },
        }
        result = orch.execute_workflow_task(
            task_prompt="telegram webhook to supabase",
            workflow_json=flow,
            daily_reqs=100,
            tech_stack=["deepseek", "supabase_free"],
        )
        assert result["status"] == "READY_FOR_DEPLOYMENT"

    def test_security_goes_to_hitl(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        orch = SystemOrchestrator(budget_usd=20.0, elide_output=True,
                                  security_token=self._mock_token())
        bad = {
            "nodes": [{"type": "n8n-nodes-base.code",
                       "parameters": {"jsCode": "require('child_process').exec('id')"}}],
            "connections": {},
        }
        result = orch.execute_workflow_task(
            task_prompt="run server cleanup",
            workflow_json=bad,
            daily_reqs=10,
            tech_stack=["deepseek"],
        )
        assert result["status"] == "PENDING_HUMAN_REVIEW"
        rid = result["hitl_request_id"]
        # approve resolves it
        from hitl_gate import HITLGate
        approval = orch.hitl.approve(rid, self._mock_token())
        assert approval["status"] == HITLState.APPROVED

    def test_budget_rejection_aborts(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        orch = SystemOrchestrator(budget_usd=0.5, elide_output=True)
        flow = {"nodes": [], "connections": {}}
        result = orch.execute_workflow_task(
            task_prompt="heavy pipeline",
            workflow_json=flow,
            daily_reqs=100000,
            tech_stack=["claude-3-5-sonnet"],
        )
        assert result["status"] == "BUDGET_REJECTED"

    def test_ephemeral_rag_always_purged(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        orch = SystemOrchestrator(budget_usd=20.0, elide_output=True)
        flow = {"nodes": [], "connections": {}}
        result = orch.execute_workflow_task(
            task_prompt="trivial", workflow_json=flow, daily_reqs=1,
            tech_stack=["deepseek"],
        )
        assert result["status"] == "READY_FOR_DEPLOYMENT"
        # tmp files shouldn't linger
        left = [f for f in tmp_path.iterdir() if f.suffix == "_ephemeral.sqlite"]
        assert not left


if __name__ == "__main__":
    pytest.main([__file__, "-v"])