"""Tests for the 9 weak-model-hardening additions:

#1 CascadeRouter (confidence tiering)     cascade_routing.py
#2 SelfConsistencyPool (best-of-N vote)   cascade_routing.py
#3 GeneratorCriticSplit                   cascade_routing.py
#4 RagMemory (real RAG)                   rag_engine.py
#5 micro_decompose (finer DAG)            dual_process_planner.py
#6 JsonSchemaGuard + FunctionCallContract schema_guard.py
#7 FewShotAssembler                       prompt_assembler.py
#8 LoRADatasetExporter                    lora_dataset.py
#9 DraftRuns (test-time compute)          cascade_routing.py
"""

import json
import tempfile
from pathlib import Path

import pytest

from cascade_routing import (CascadeRouter, SelfConsistencyPool,
                             GeneratorCriticSplit, DraftRuns,
                             extract_confidence, ChecklistItem)
from rag_engine import RagMemory
from dual_process_planner import ExtendedThinkingPlanner
from schema_guard import JsonSchemaGuard, FunctionCallContract
from prompt_assembler import FewShotAssembler, build_generator_prompt
from lora_dataset import LoRADatasetExporter
from feedback_loop import FeedbackLoop


# ---------------------------------------------------------------------------
# #1 Cascade routing
# ---------------------------------------------------------------------------

class TestCascadeRouter:
    def setup_method(self):
        self.calls = {"cheap": 0, "frontier": 0}

        def cheap(task):
            self.calls["cheap"] += 1
            return {"ok": True, "answer": "cheap"}

        def frontier(task):
            self.calls["frontier"] += 1
            return {"ok": True, "answer": "frontier"}

        self.router = CascadeRouter(cheap_fn=cheap, frontier_fn=frontier)

    def test_routine_uses_cheap(self):
        r = self.router.route("parse webhook payload", {"ok": True, "confidence": 0.9})
        assert r["tier"] == "CHEAP"
        assert self.calls["frontier"] == 0

    def test_high_risk_always_frontier(self):
        r = self.router.route("edit production workflow with customer data")
        assert r["tier"] == "FRONTIER"
        assert r["escalated"] is True
        assert self.calls["frontier"] == 1

    def test_low_confidence_escalates(self):
        r = self.router.route("design a new topology",
                              {"ok": True, "confidence": 0.1})
        assert r["tier"] == "FRONTIER"
        assert "confidence" in r["reason"]

    def test_high_risk_no_frontier_goes_hitl(self):
        r = CascadeRouter(cheap_fn=lambda t: {"ok": True},
                          frontier_fn=None).route("deploy to live")
        assert r["tier"] == "HITL"

    def test_explicit_confidence_marker(self):
        est = extract_confidence("confidence: 0.42")
        assert est.declared is True
        assert est.score == 0.42


# ---------------------------------------------------------------------------
# #2 Self-consistency
# ---------------------------------------------------------------------------

class TestSelfConsistencyPool:
    def test_picks_best_scored_candidate(self):
        def draw(i):
            if i == 0:
                return {"nodes": [], "connections": {}}
            return {"nodes": [{"name": f"n{i}"}], "connections": {}}

        pool = SelfConsistencyPool(draw_fn=draw, n=3)
        res = pool.run()
        assert res["n_drawn"] == 3
        assert len(res["winner"]["nodes"]) == 1  # richer candidate won

    def test_schema_valid_gets_priority(self):
        def draw(i):
            return {"nodes": []} if i == 0 else {"nodes": [], "connections": {}}

        pool = SelfConsistencyPool(
            draw_fn=draw, n=2,
            schema_validator=lambda o: "connections" in o)
        res = pool.run()
        assert "connections" in res["winner"]


# ---------------------------------------------------------------------------
# #3 Generator / Critic split
# ---------------------------------------------------------------------------

class TestGeneratorCriticSplit:
    def test_critical_violation_blocks(self):
        checklist = [
            ChecklistItem("no_localhost", "URLs must not target localhost", critical=True),
            ChecklistItem("named_nodes", "Every node needs a name", critical=False),
        ]

        def gen(task):
            return {"nodes": [{"type": "httpRequest",
                               "parameters": {"url": "http://127.0.0.1/x"}}]}

        def critic(output, rules):
            return ["no_localhost"]  # the critic (weak model) catches it

        gcs = GeneratorCriticSplit(critic_fn=critic, checklist=checklist)
        res = gcs.generate_and_critique(gen, "build")
        assert res["ok"] is False
        assert "no_localhost" in res["critical_breached"]

    def test_minor_violation_does_not_block(self):
        checklist = [ChecklistItem("named_nodes", "name required", critical=False)]
        gcs = GeneratorCriticSplit(critic_fn=lambda o, r: ["named_nodes"],
                                   checklist=checklist)
        res = gcs.generate_and_critique(lambda t: {}, "build")
        assert res["ok"] is True
        assert len(res["violations"]) == 1


# ---------------------------------------------------------------------------
# #4 Real RAG
# ---------------------------------------------------------------------------

class TestRagMemory:
    def test_ingest_and_query_relevant(self, tmp_path):
        rag = RagMemory(db_path=str(tmp_path / "r.db"))
        rag.ingest("n8n-docs", "webhook paths must be unique per workflow",
                   title="webhook", keywords=["webhook", "path"])
        rag.ingest("n8n-docs", "schedule cron every 5 minutes",
                   title="cron", keywords=["cron", "schedule"])
        hits = rag.query("unique webhook path", limit=5)
        assert hits[0]["title"] == "webhook"

    def test_approved_workflows_ranked_higher(self, tmp_path):
        rag = RagMemory(db_path=str(tmp_path / "r2.db"))
        rag.ingest("error-pattern", "missing pinnedData breaks testing", title="x",
                   keywords=["pinnedData"])
        rag.ingest_approved_workflow(
            {"nodes": [{"name": "Webhook", "type": "webhook",
                        "parameters": {"pinnedData": {}}}]},
            title="golden pinnedData pattern", scope="global")
        hits = rag.query("pinnedData")
        assert hits[0]["approved"] == 1

    def test_scope_isolation(self, tmp_path):
        rag = RagMemory(db_path=str(tmp_path / "r3.db"))
        rag.ingest("n8n-docs", "telegram auth", scope="telegram-task", keywords=["telegram"])
        rag.ingest("n8n-docs", "stripe webhook", scope="payments", keywords=["stripe"])
        assert rag.query("telegram auth", scope="telegram-task")[0]["scope"] == "telegram-task"
        assert rag.query("telegram auth", scope="payments") == []


# ---------------------------------------------------------------------------
# #5 Finer DAG
# ---------------------------------------------------------------------------

class TestMicroDecompose:
    def test_service_breaks_into_verifiable_units(self):
        planner = ExtendedThinkingPlanner()
        micro = planner.micro_decompose("stripe")
        ids = [n.id for n in micro]
        assert "stripe_auth" in ids
        assert "stripe_call" in ids
        assert "stripe_error" in ids
        # every unit has a dependency chain (no orphan in the middle)
        assert micro[1].deps == ["stripe_auth"]

    def test_micro_units_are_small(self):
        planner = ExtendedThinkingPlanner()
        micro = planner.micro_decompose("telegram")
        assert 4 <= len(micro) <= 7  # deliberately small chunks


# ---------------------------------------------------------------------------
# #6 Schema guard
# ---------------------------------------------------------------------------

WORKFLOW_SCHEMA = {
    "type": "object",
    "required": ["nodes", "connections"],
    "properties": {
        "nodes": {"type": "array", "items": {"type": "object"}},
        "connections": {"type": "object"},
    },
}


class TestJsonSchemaGuard:
    def test_valid_json_passes(self):
        guard = JsonSchemaGuard(WORKFLOW_SCHEMA)
        r = guard.ensure('{"nodes": [], "connections": {}}')
        assert r.ok is True
        assert r.attempts == 1

    def test_invalid_json_self_heals_with_schema_feedback(self):
        # draw_fn "fixes" on second attempt
        calls = {"n": 0}

        def draw(msg):
            calls["n"] += 1
            return '{"nodes": [], "connections": {}}'

        guard = JsonSchemaGuard(WORKFLOW_SCHEMA, max_attempts=3, validator=None)
        r = guard.ensure("garbage not json", draw_fn=draw)
        assert r.ok is True
        assert calls["n"] == 1

    def test_exhausts_attempts_on_stubborn_failure(self):
        guard = JsonSchemaGuard(WORKFLOW_SCHEMA, max_attempts=2)
        r = guard.ensure("not json at all", draw_fn=lambda m: "still not json")
        assert r.ok is False
        assert r.attempts == 2

    def test_missing_required_key_detected(self):
        guard = JsonSchemaGuard(WORKFLOW_SCHEMA)
        r = guard.ensure('{"nodes": []}')
        assert r.ok is False
        assert any("connections" in e for e in r.errors)

    def test_function_call_contract(self):
        fc = FunctionCallContract(allowed_names={"create_workflow"}, max_attempts=2)
        r = fc.call('{"name": "create_workflow", "arguments": {"path": "x"}}')
        assert r.ok is True
        assert r.arguments["path"] == "x"

    def test_function_call_rejects_unknown(self):
        fc = FunctionCallContract(allowed_names={"create_workflow"}, max_attempts=1)
        r = fc.call('{"name": "rm_rf", "arguments": {}}')
        assert r.ok is False


# ---------------------------------------------------------------------------
# #7 Few-shot assembler
# ---------------------------------------------------------------------------

class TestFewShotAssembler:
    def test_rejections_become_negative_fewshot(self, tmp_path):
        fb = FeedbackLoop(db_path=str(tmp_path / "fb.db"))
        for _ in range(3):
            fb.record_rejection("ssrf_internal_egress", reason="no localhost")
        asm = FewShotAssembler(feedback=fb)
        block = asm.render_prompt_block(rule_keywords=["ssrf"])
        assert "ssrf_internal_egress" in block
        assert "AVOID" in block

    def test_build_prompt_composes_all_scaffolding(self):
        p = build_generator_prompt(
            task="build a webhook",
            rag_context="# Context\nwebhook path unique",
            few_shot="# negatives\nAVOID localhost",
            schema_hint='{"nodes": [...]}')
        assert "## Task" in p
        assert "Reference context" in p
        assert "Do not repeat" in p
        assert "Output format" in p


# ---------------------------------------------------------------------------
# #8 LoRA dataset
# ---------------------------------------------------------------------------

class TestLoRADatasetExporter:
    def test_exports_approved_and_rejected_jsonl(self, tmp_path):
        rag = RagMemory(db_path=str(tmp_path / "rag.db"))
        rag.ingest_approved_workflow({"nodes": []}, title="golden")
        fb = FeedbackLoop(db_path=str(tmp_path / "fb.db"))
        fb.record_rejection("bad_domain", "brand misuse")

        exp = LoRADatasetExporter(rag=rag, feedback_db=str(tmp_path / "fb.db"))
        out = tmp_path / "lora.jsonl"
        stats = exp.export_jsonl(out)
        assert stats.total == 2
        assert stats.positive == 1
        assert stats.negative == 1
        lines = out.read_text().splitlines()
        assert json.loads(lines[0])["rejected"] in (True, False)

    def test_few_shot_reuses_corpus(self, tmp_path):
        rag = RagMemory(db_path=str(tmp_path / "r.db"))
        rag.ingest_approved_workflow({"nodes": []}, title="good flow")
        exp = LoRADatasetExporter(rag=rag)
        assert "good flow" in exp.few_shot_from_corpus(limit=1)


# ---------------------------------------------------------------------------
# #9 Draft runs
# ---------------------------------------------------------------------------

class TestDraftRuns:
    def test_returns_best_scored_draft(self):
        drafts = {"0": "short", "1": "a longer well-formed draft answer", "2": "mid"}

        def draw(i):
            return drafts[str(i)]

        dr = DraftRuns(draw_fn=draw, drafts=3)
        res = dr.best(score_fn=len)
        assert res["best_draft"] == "a longer well-formed draft answer"
        assert len(res["all_drafts_scored"]) == 3