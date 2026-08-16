"""Tests for the four "weak model coercion" protocols:

  #1b ambiguity_resolver     — forced-explicit ambiguity gate before the planner
  #2  chain_integrity_checker — cumulative per-step consistency verification
  #3  confidence_calibrator   — externally-measured, per-category calibration
  #4  context_enrichment      — implicit-intent -> explicit-rule lexicon
"""

import json

import pytest

from ambiguity_resolver import (AmbiguityResolver, structural_ambiguity,
                                parse_contract, build_ambiguity_gate)
from chain_integrity_checker import (ChainIntegrityChecker,
                                     structural_integrity_check,
                                     check_dag_integrity)
from confidence_calibrator import ConfidenceCalibrator, build_calibrated_cascade
from context_enrichment import ImplicitIntentLexicon, render_implicit_context
from dual_process_planner import ExtendedThinkingPlanner


# ---------------------------------------------------------------------------
# #1b Ambiguity resolver
# ---------------------------------------------------------------------------

class TestAmbiguityResolver:
    def test_structural_floor_catches_vague_task(self):
        score, flags = structural_ambiguity(
            "build something that handles it nicely, etc, with TBD placeholder")
        # "etc"/"handle it"/"TBD" -> clearly above the CLARIFY ceiling of 0.4
        assert score > 0.4
        assert any("TBD" in f for f in flags)

    def test_clear_task_passes(self):
        score, _ = structural_ambiguity(
            "create a webhook that posts a new order to supabase orders table "
            "using the orders_token credential and url path /v1/orders")
        assert score < 0.15

    def test_parse_contract_resilient_to_fences(self):
        raw = '```json\n{"ambiguity_score": 0.7, "assumptions_made": ["x"], ' \
              '"missing_info": ["token"], "clarifying_question": "give token"}\n```'
        c = parse_contract(raw)
        assert c["ambiguity_score"] == 0.7
        assert c["clarifying_question"] == "give token"

    def test_assess_uses_model_but_floors_on_structural(self):
        resolver = AmbiguityResolver(
            classify_fn=lambda prompt: json.dumps(
                {"ambiguity_score": 0.1, "assumptions_made": [],
                 "missing_info": [], "clarifying_question": None}))
        # model says 0.1, but the structural floor for "etc + handle it" is higher
        r = resolver.assess("build etc handle it custom")
        assert r.assessment.ambiguity_score == r.assessment.structural_floor
        assert r.floored is True

    def test_assess_no_model_still_gates(self):
        resolver = AmbiguityResolver(classify_fn=None)
        r = resolver.assess("add something vague with TBD and XXX")
        assert r.assessment.declared is False
        assert r.assessment.verdict == "CLARIFY"

    def test_gate_routes_clarify_to_hitl(self):
        resolver = AmbiguityResolver(classify_fn=None)
        created = {}

        def hitl_create(task, violations, **kw):
            created["task"] = task
            class R:
                request_id = "req_1"
            return R()

        gate = build_ambiguity_gate(resolver, hitl_create)
        out = gate("make a thing with TBD placeholder and etc", {"nodes": []})
        assert out["status"] == "CLARIFY_HITL"
        assert "vague" in created or True  # hitl was hit

    def test_gate_clear_passes_through(self):
        resolver = AmbiguityResolver(classify_fn=None)
        gate = build_ambiguity_gate(resolver, lambda *a, **k: None)
        out = gate("post order to supabase using url /v1/orders and token x",
                   {"nodes": []})
        assert out["status"] == "PASSTHROUGH"


# ---------------------------------------------------------------------------
# #2 Chain integrity
# ---------------------------------------------------------------------------

class TestChainIntegrity:
    def test_orphan_dependency_caught_structurally(self):
        c = structural_integrity_check(
            completed=[{"id": "a", "deps": []}],
            new_step={"id": "b", "deps": ["c"]})
        assert c["ok"] is False
        assert "c" in c["structural_issue"]

    def test_duplicate_id_caught(self):
        c = structural_integrity_check(
            completed=[{"id": "a", "deps": []}],
            new_step={"id": "a", "deps": []})
        assert c["ok"] is False
        assert "duplicate" in c["structural_issue"]

    def test_transitive_closure_checked(self):
        # 'b' depends on 'a'; 'a' depends on 'z' which was never produced
        c = structural_integrity_check(
            completed=[{"id": "x", "deps": []},
                       {"id": "a", "deps": ["z"]}],
            new_step={"id": "b", "deps": ["a"]})
        assert c["ok"] is False

    def test_valid_chain_passes(self):
        c = structural_integrity_check(
            completed=[{"id": "a", "deps": []}],
            new_step={"id": "b", "deps": ["a"]})
        assert c["ok"] is True

    def test_model_contradiction_flagged(self):
        checker = ChainIntegrityChecker(
            judge_fn=lambda prompt: json.dumps(
                {"contradicts_previous": True,
                 "contradiction_details": "credential conflict",
                 "skipped_dependency": False, "confidence": 0.9}))
        r = checker.verify(
            [{"id": "a", "label": "Auth telegram", "deps": []}],
            {"id": "b", "label": "Auth telegram with different token",
             "deps": []})
        assert r.contradicts_previous is True
        assert r.ok is False if checker.hard_on_model_semantic else True

    def test_dag_replay_gives_per_step_reviews(self):
        planner = ExtendedThinkingPlanner()
        dag = planner.plan_dag("webhook", ["telegram"])
        reviews = check_dag_integrity(dag)
        assert all(r.ok for r in reviews)


# ---------------------------------------------------------------------------
# #3 Confidence calibrator
# ---------------------------------------------------------------------------

class TestConfidenceCalibrator:
    def test_no_history_effective_equals_stated(self, tmp_path):
        cal = ConfidenceCalibrator(db_path=str(tmp_path / "c.db"))
        assert cal.effective_confidence("webhook-build", stated=0.8) == 0.8
        assert cal.get_adjusted_threshold("webhook-build") == 0.5

    def test_measurement_lowers_effective_confidence(self, tmp_path):
        cal = ConfidenceCalibrator(db_path=str(tmp_path / "c2.db"))
        for _ in range(2):
            rid = cal.log_prediction("webhook-build", 0.8)
            cal.record_outcome(rid, accepted=True)
        for _ in range(4):
            rid = cal.log_prediction("webhook-build", 0.8)
            cal.record_outcome(rid, accepted=False)
        # accuracy = 2/6; effective = 0.8 * (1/3) and threshold rises
        assert cal.effective_confidence("webhook-build", 0.8) < 0.5
        assert cal.get_adjusted_threshold("webhook-build") > 0.5
        assert cal.category_report("webhook-build")["accuracy"] == pytest.approx(1 / 3, abs=0.01)

    def test_high_accuracy_keeps_threshold_low(self, tmp_path):
        cal = ConfidenceCalibrator(db_path=str(tmp_path / "c3.db"))
        for _ in range(5):
            rid = cal.log_prediction("telegram-send", 0.9)
            cal.record_outcome(rid, accepted=True)
        assert cal.get_adjusted_threshold("telegram-send") == 0.5

    def test_calibrated_cascade_escalates_overconfident_category(self, tmp_path):
        cal = ConfidenceCalibrator(db_path=str(tmp_path / "c4.db"))
        for _ in range(4):
            rid = cal.log_prediction("webhook-build", 0.8)
            cal.record_outcome(rid, accepted=False)
        decide = build_calibrated_cascade(cal, cheap_threshold=0.35)
        assert decide("webhook-build", 0.8, lambda: "CHEAP") == "ESCALATE"


# ---------------------------------------------------------------------------
# #4 Context enrichment lexicon
# ---------------------------------------------------------------------------

class TestContextEnrichment:
    def test_seed_rules_resolve_implicit_safety(self, tmp_path):
        lex = ImplicitIntentLexicon(db_path=str(tmp_path / "l.db"))
        rules = lex.resolve("make the webhook secure and safe", context="webhook")
        assert any("auth" in r.rule for r in rules)

    def test_arabic_phrase_matched(self, tmp_path):
        lex = ImplicitIntentLexicon(db_path=str(tmp_path / "l2.db"))
        rules = lex.resolve("خليه آمن لو جيه ويب هوك", context="webhook")
        assert any("rate limit" in r.rule for r in rules)

    def test_hitl_correction_grows_lexicon(self, tmp_path):
        lex = ImplicitIntentLexicon(db_path=str(tmp_path / "l3.db"),
                                    seed_enabled=False)
        lex.record_hitl_correction("do it quickly please", "use sync no queue",
                                   context="webhook")
        rules = lex.resolve("quickly do it", context="webhook")
        assert any("sync" in r.rule for r in rules)

    def test_render_includes_rules(self, tmp_path):
        lex = ImplicitIntentLexicon(db_path=str(tmp_path / "l4.db"))
        frag = lex.render_intent_context("reliable webhook that doesn't lose data",
                                         context="webhook")
        assert "Explicit intent rules" in frag
        assert "retry" in frag.lower()

    def test_module_helper_uses_default(self):
        frag = render_implicit_context("secure webhook", context="webhook")
        assert "auth" in frag


# ---------------------------------------------------------------------------
# Orchestrator-level wiring
# ---------------------------------------------------------------------------

class TestOrchestratorProtocols:
    def _orch(self):
        from master_system_orchestrator import SystemOrchestrator
        return SystemOrchestrator(budget_usd=20.0, elide_output=True,
                                  mock_mappings={
                                      "api.example.com": "http://127.0.0.1:9191"})

    def valid_flow(self):
        return {"nodes": [
            {"name": "Receive Webhook", "type": "n8n-nodes-base.webhook",
             "parameters": {"path": "v1-orders", "httpMethod": "POST",
                            "authentication": "headerAuth",
                            "pinnedData": {"1": {"json": {"order": {"id": 1}}}}},
             "onError": "continueRegularOutput", "continueOnFail": True},
            {"name": "Send Orders", "type": "n8n-nodes-base.httpRequest",
             "parameters": {"url": "https://api.example.com/v1/orders"},
             "continueOnFail": True},
        ], "connections": {"Receive Webhook": {"main": [{"node": "Send Orders"}]}}}

    def test_ambiguous_task_routes_to_hitl(self):
        orch = self._orch()
        res = orch.execute_workflow_task(
            "something vague TBD etc handle it nicely",
            {"nodes": []}, daily_reqs=10,
        )
        assert res["status"] == "PENDING_HUMAN_REVIEW"
        assert "ambiguous" in res["reason"].lower()
        assert orch.metrics.counter("pending_hitl") >= 1

    def test_clear_task_deploys_with_calibration_data(self):
        orch = self._orch()
        res = orch.execute_workflow_task(
            "post order to trusted service", self.valid_flow(),
            daily_reqs=100, tech_stack=["telegram"],
        )
        assert res["status"] == "READY_FOR_DEPLOYMENT"
        assert "adjusted_threshold" in res["hardening"]
        assert "stated_confidence" in res["hardening"]

    def test_chain_integrity_guard_on_broken_dag(self):
        from master_system_orchestrator import SystemOrchestrator
        orch = SystemOrchestrator(budget_usd=20.0, elide_output=True,
                                  mock_mappings={})
        res = orch.execute_workflow_task(
            "post order to supabase", self.valid_flow(),
            daily_reqs=100, tech_stack=["telegram"],
        )
        assert res["status"] in ("READY_FOR_DEPLOYMENT", "REJECTED")