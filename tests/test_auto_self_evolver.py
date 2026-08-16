"""Tests for the Autonomous Self-Evolution Engine (v2 — honest measurement).

Covers the no-theater contract:
  - benchmark_vs only claims gaps it MEASURED with live model calls
  - weaknesses come from the REAL audit trail (FeedbackLoop), never static prose
  - every candidate maps to a deterministic canonical probe (no placebo)
  - promotion happens only when a real model passes the probe
  - promoted rules land in rules.json and the SecurityGate ENFORCES them
"""

import json

import pytest

from auto_self_evolver import (AutonomousSelfEvolver, BenchmarkReport,
                               CANONICAL_PROBES, SkillRegistry, WeaknessSource,
                               run_probe, benchmark_vs)
from feedback_loop import FeedbackLoop
from security_gate import SecurityGate


# ---------------------------------------------------------------------------
# Deterministic fake models: one that violates a probe, one that complies.
# These let us assert MEASURED gap/promotion behavior without a real LLM.
# ---------------------------------------------------------------------------

def fake_current_violates(prompt: str) -> str:
    """Pretends to be a weak current model: emits an SSRF-y internal URL."""
    return json.dumps({"nodes": [{"name": "n",
                                  "parameters": {"url": "http://127.0.0.1:8000/x"}}]})


def fake_leader_complies(prompt: str) -> str:
    return json.dumps({"nodes": [{"name": "n",
                                  "parameters": {"url": "https://api.example.com/x"}}]})


def fake_current_complies(prompt: str) -> str:
    return fake_leader_complies(prompt)


@pytest.fixture
def evolver(tmp_path):
    return AutonomousSelfEvolver(skills_dir=tmp_path / "skills",
                                 key_path=tmp_path / "rules.key")


@pytest.fixture
def feedback(tmp_path):
    return FeedbackLoop(db_path=tmp_path / "fb.db")


def make_evolver(feedback, tmp_path):
    """Evolver wired to a REAL FeedbackLoop audit trail."""
    return AutonomousSelfEvolver(
        skills_dir=tmp_path / "skills",
        weakness_source=WeaknessSource(feedback=feedback),
        key_path=tmp_path / "rules.key",
        audit=feedback)


# ---------------------------------------------------------------------------
# Benchmark: live measurement only, no fabricated numbers
# ---------------------------------------------------------------------------

class TestBenchmark:
    def test_missing_leader_means_unmeasured(self, evolver):
        r = evolver.benchmark_and_analyze_gap("cybersec_audit",
                                              current_model_fn=fake_current_violates,
                                              leader_fn=None)
        assert isinstance(r, BenchmarkReport)
        assert r.measured is False
        assert r.current_score is None
        assert r.gap_pct is None
        assert r.needs_evolution is False   # never escalate on unknown
        assert "no live leader" in r.note

    def test_measured_gap_reported_from_real_outputs(self, evolver):
        r = evolver.benchmark_and_analyze_gap(
            "cybersec_audit", current_model_fn=fake_current_violates,
            leader_fn=fake_leader_complies, leader_name="gpt-5")
        assert r.measured is True
        assert r.leader == "gpt-5"
        assert r.current_score == pytest.approx(0.667, abs=0.01)  # 2/3 probes
        assert r.leader_score == 1.0
        assert r.gap_pct == pytest.approx(33.33, abs=0.01)
        assert r.needs_evolution is True

    def test_no_gap_when_both_comply(self, evolver):
        r = benchmark_vs("cybersec_audit", fake_current_complies,
                         fake_leader_complies)
        assert r.measured is True
        assert r.gap_pct == 0.0
        assert r.needs_evolution is False

    def test_broken_model_scores_zero_not_crash(self):
        def broken(prompt):
            raise RuntimeError("api down")
        r = benchmark_vs("cybersec_audit", broken, fake_leader_complies)
        assert r.current_score == 0.0
        assert r.gap_pct == pytest.approx(100.0, abs=0.01)


# ---------------------------------------------------------------------------
# Weakness extraction: real audit trail only, empty when nothing happened
# ---------------------------------------------------------------------------

class TestWeaknessSource:
    def test_empty_without_real_data(self, tmp_path):
        fb = FeedbackLoop(db_path=tmp_path / "empty.db")
        ws = WeaknessSource(feedback=fb)
        assert ws.extract() == []

    def test_rejections_surface_as_candidates(self, feedback):
        feedback.record_rejection("ssrf_internal_egress", "human vetoed egress")
        ws = WeaknessSource(feedback=feedback)
        got = ws.extract()
        assert got and got[0]["rule"] == "ssrf_internal_egress"
        assert got[0]["source"] == "feedback"
        assert got[0]["count"] >= 1

    def test_min_rejections_filters_weak_signals(self, feedback):
        feedback.record_rejection("unauthed_webhook", "once")
        ws = WeaknessSource(feedback=feedback)
        assert ws.extract(min_rejections=2) == []

    def test_quirks_callback_consumed(self):
        ws = WeaknessSource(quirks_list_cb=lambda: [
            {"service": "hitl_feedback", "trigger_term": "secret_hardcoded",
             "fix": "put secrets in vault"}])
        got = ws.extract()
        assert got and got[0]["rule"] == "secret_hardcoded"
        assert got[0]["source"] == "quirk"

    def test_non_hitl_quirks_ignored(self):
        ws = WeaknessSource(quirks_list_cb=lambda: [
            {"service": "other_service", "trigger_term": "x", "fix": "y"}])
        assert ws.extract() == []


# ---------------------------------------------------------------------------
# Probes: deterministic, connected to the exact failure mode
# ---------------------------------------------------------------------------

class TestProbes:
    def test_ssrf_probe_rejects_internal_egress(self):
        ok, _ = run_probe(CANONICAL_PROBES["ssrf_internal_egress"],
                          '{"url": "http://192.168.1.5/x"}')
        assert ok is False

    def test_ssrf_probe_passes_public_egress(self):
        ok, _ = run_probe(CANONICAL_PROBES["ssrf_internal_egress"],
                          '{"url": "https://api.example.com/x"}')
        assert ok is True

    def test_secret_probe_rejects_token_literal(self):
        ok, _ = run_probe(CANONICAL_PROBES["secret_hardcoded"],
                          'x = "sk-abcdefghijklmnopqrstuvwxyz123456"')
        assert ok is False

    def test_ast_probe_rejects_syntax_error(self):
        ok, detail = run_probe(CANONICAL_PROBES["async_syntax"],
                               "async def main(:\n  pass")
        assert ok is False
        assert "SyntaxError" in detail

    def test_ast_probe_passes_valid_code(self):
        ok, _ = run_probe(CANONICAL_PROBES["async_syntax"],
                          "async def main():\n    await f()")
        assert ok is True

    def test_unknown_probe_kind_raises(self):
        from auto_self_evolver import ProbeError
        with pytest.raises(ProbeError):
            run_probe({"kind": "nope"}, "x")


# ---------------------------------------------------------------------------
# Registry: machine-readable artifacts actually consumed by the gate
# ---------------------------------------------------------------------------

class TestSkillRegistry:
    def _reg(self, tmp_path, **kw):
        return SkillRegistry(tmp_path / "skills",
                             key_path=tmp_path / "rules.key", **kw)

    def test_promote_writes_rules_json(self, tmp_path):
        reg = self._reg(tmp_path)
        path = reg.promote("secret_hardcoded", CANONICAL_PROBES["secret_hardcoded"],
                           evidence={"rejection_count": 3, "verified_by": "m"})
        assert path.exists()
        rules = json.loads(path.read_text(encoding="utf-8"))
        assert isinstance(rules, list)
        payload = rules[0]
        assert payload["rule"] == "secret_hardcoded"
        assert payload["probe"]["kind"] == "guard"
        assert "promoted_at" in payload
        assert reg.sig_path.exists()

    def test_promote_writes_skill_doc(self, tmp_path):
        reg = self._reg(tmp_path)
        reg.promote("secret_hardcoded", CANONICAL_PROBES["secret_hardcoded"])
        doc = reg.write_skill_doc("secret_hardcoded",
                                  CANONICAL_PROBES["secret_hardcoded"],
                                  "verified by real model")
        assert doc.exists()
        content = doc.read_text(encoding="utf-8")
        assert content.startswith("---\nname: auto-fix-secret-hardcoded")

    def test_load_rules_returns_promoted_only(self, tmp_path):
        reg = self._reg(tmp_path)
        assert reg.load_rules() == []
        reg.promote("secret_hardcoded", CANONICAL_PROBES["secret_hardcoded"])
        reg.promote("ssrf_internal_egress", CANONICAL_PROBES["ssrf_internal_egress"])
        rules = reg.load_rules()
        assert {r["rule"] for r in rules} == {"secret_hardcoded",
                                              "ssrf_internal_egress"}

    def test_gate_enforces_promoted_rule(self, tmp_path):
        """The whole point of critique #4: a promoted rule becomes a REAL
        rejection in the deterministic gate, not an inert .md."""
        reg = self._reg(tmp_path)
        reg.promote("ssrf_internal_egress", CANONICAL_PROBES["ssrf_internal_egress"],
                    evidence={"rejection_count": 3, "verified_by": "test-model"})
        gate = SecurityGate(rules_dir=tmp_path / "skills",
                            key_path=str(tmp_path / "rules.key"))

        clean = {"nodes": [{"type": "n8n-nodes-base.httpRequest",
                            "parameters": {"url": "https://api.example.com/x"}}]}
        assert gate.evaluate_to_dict(clean)["status"] == "APPROVED"

        bad = {"nodes": [{"type": "n8n-nodes-base.httpRequest",
                          "parameters": {"url": "http://192.168.1.5/x"}}]}
        res = gate.evaluate_to_dict(bad)
        assert res["status"] == "REJECTED_SECURITY_RISK"
        assert any("Auto-rule 'ssrf_internal_egress'" in v for v in res["violations"])

    def test_clean_gate_with_no_rules_unaffected(self):
        gate = SecurityGate(rules_dir=None)
        wf = {"nodes": [{"type": "n8n-nodes-base.httpRequest",
                         "parameters": {"url": "https://api.example.com/x"}}]}
        assert gate.evaluate_to_dict(wf)["status"] == "APPROVED"


# ---------------------------------------------------------------------------
# Evolution cycle: promotion ONLY after a real model passes the probe
# ---------------------------------------------------------------------------

class TestEvolutionCycle:
    def test_no_weaknesses_means_nothing_promoted(self, tmp_path, feedback):
        evolver = make_evolver(feedback, tmp_path)
        res = evolver.run_evolution_cycle("cybersec_audit",
                                          current_model_fn=fake_current_complies,
                                          leader_fn=fake_leader_complies)
        assert res.promoted_count == 0
        assert res.measured is True
        assert "no real rejection evidence" in res.round_note

    def test_no_model_means_nothing_promoted(self, tmp_path, feedback):
        evolver = make_evolver(feedback, tmp_path)
        feedback.record_rejection("ssrf_internal_egress", "veto")
        res = evolver.run_evolution_cycle("cybersec_audit",
                                          current_model_fn=None, leader_fn=None)
        assert res.promoted_count == 0
        assert res.measured is False
        assert "NOTHING promoted" in res.round_note
        assert "ssrf_internal_egress" in res.candidates

    def test_current_model_still_violates_is_not_promoted(self, tmp_path, feedback):
        evolver = make_evolver(feedback, tmp_path)
        feedback.record_rejection("ssrf_internal_egress", "still doing it")
        res = evolver.run_evolution_cycle("cybersec_audit",
                                          current_model_fn=fake_current_violates,
                                          leader_fn=fake_leader_complies)
        assert res.promoted_count == 0
        assert any("probe failed" in f for f in res.failures)

    def test_compliant_model_promotes_rule(self, tmp_path, feedback):
        evolver = make_evolver(feedback, tmp_path)
        feedback.record_rejection("ssrf_internal_egress", "was doing it, fixed now")
        res = evolver.run_evolution_cycle("cybersec_audit",
                                          current_model_fn=fake_current_complies,
                                          leader_fn=fake_leader_complies)
        assert res.promoted_count == 1
        assert res.candidates == ["ssrf_internal_egress"]
        assert evolver.registry.load_rules()[0]["rule"] == "ssrf_internal_egress"

    def test_unknown_rule_skipped_cleanly(self, tmp_path, feedback):
        evolver = make_evolver(feedback, tmp_path)
        feedback.record_rejection("some_future_rule_no_probe_yet", "new vector")
        res = evolver.run_evolution_cycle("cybersec_audit",
                                          current_model_fn=fake_current_complies,
                                          leader_fn=fake_leader_complies)
        assert res.promoted_count == 0
        assert any("no canonical probe" in f for f in res.failures)

    def test_result_serializable(self, tmp_path, feedback):
        evolver = make_evolver(feedback, tmp_path)
        feedback.record_rejection("ssrf_internal_egress", "x")
        res = evolver.run_evolution_cycle("cybersec_audit",
                                          current_model_fn=fake_current_complies,
                                          leader_fn=fake_leader_complies)
        json.dumps(res.to_dict())


# ---------------------------------------------------------------------------
# Research-pattern ports: Voyager, DSPy, Cline/Roo, EvoAgent (deterministic)
# ---------------------------------------------------------------------------

class TestVoyagerSkillRetrieval:
    def test_find_rules_for_task_returns_scored_match(self, tmp_path):
        reg = SkillRegistry(tmp_path / "skills", key_path=tmp_path / "k.key")
        reg.promote("ssrf_internal_egress", CANONICAL_PROBES["ssrf_internal_egress"])
        hits = reg.find_rules_for_task("check http egress to internal hosts")
        assert any(r["rule"] == "ssrf_internal_egress" for r in hits)

    def test_find_rules_for_task_no_match_empty(self, tmp_path):
        reg = SkillRegistry(tmp_path / "skills", key_path=tmp_path / "k.key")
        reg.promote("ssrf_internal_egress", CANONICAL_PROBES["ssrf_internal_egress"])
        assert reg.find_rules_for_task("color palette css") == []


class TestDSPyDemonstrations:
    def test_demonstration_captured_on_promote(self, tmp_path, feedback):
        evolver = make_evolver(feedback, tmp_path)
        feedback.record_rejection("ssrf_internal_egress", "was doing it")
        evolver.run_evolution_cycle("cybersec_audit",
                                    current_model_fn=fake_current_complies,
                                    leader_fn=fake_leader_complies)
        rule = evolver.registry.load_rules()[0]
        assert rule["evidence"]["demonstration"] == fake_leader_complies("")
        demos = evolver.registry.demonstrations_for_task("ssrf_internal_egress")
        assert demos and demos[0]["rule"] == "ssrf_internal_egress"

    def test_demo_injection_reaches_model(self, tmp_path, feedback):
        seen = []

        def spy(prompt: str) -> str:
            seen.append(prompt)
            return fake_leader_complies(prompt)

        evolver = make_evolver(feedback, tmp_path)
        feedback.record_rejection("ssrf_internal_egress", "round one")
        evolver.run_evolution_cycle("cybersec_audit",
                                    current_model_fn=spy, leader_fn=spy)
        # second round: the demo from round one is injected into the prompt
        feedback.record_rejection("ssrf_internal_egress", "round two")
        evolver.run_evolution_cycle("cybersec_audit",
                                    current_model_fn=spy, leader_fn=spy)
        assert any("Known-good example" in p for p in seen)


class TestClineDirectRule:
    def test_promote_direct_rule_records_developer_source(self, tmp_path):
        reg = SkillRegistry(tmp_path / "skills", key_path=tmp_path / "k.key")
        reg.promote_direct_rule("async_db_conn_guard",
                                {"kind": "guard",
                                 "deny_patterns": [r"create_pool\(.*close\)"],
                                 "description": "async db connection must use the close pattern"})
        rule = reg.load_rules()[0]
        assert rule["rule"] == "async_db_conn_guard"
        assert rule["source"] == "developer"


class TestEvoAgentDirective:
    def test_directive_derived_from_probe(self):
        from auto_self_evolver import build_system_directive
        d = build_system_directive("ssrf_internal_egress",
                                   CANONICAL_PROBES["ssrf_internal_egress"])
        assert "System Directive (ssrf_internal_egress)" in d
        assert "pre-deploy gate" in d

    def test_fatal_probe_directive_strengthens_language(self):
        from auto_self_evolver import build_system_directive
        d = build_system_directive("ssrf_internal_egress",
                                   {**CANONICAL_PROBES["ssrf_internal_egress"],
                                    "fatal": True})
        assert "MUST be rejected" in d


def test_demo_main_runs():
    import subprocess, sys
    r = subprocess.run([sys.executable, "auto_self_evolver.py"],
                       capture_output=True, text=True, timeout=30)
    assert r.returncode == 0
    assert '"measured": true' in r.stdout
