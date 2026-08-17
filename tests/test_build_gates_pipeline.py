"""Tests for the Build Gates Pipeline (scripts/build_gates_pipeline.py).

Covers all seven stages: SECURITY, QUALITY, INTEGRITY, MATH, REASONING, HITL,
AUDIT — deterministic, no network, no real audit.db writes (--no-hitl paths
and tmp_db for HITL).
"""

import json
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.build_gates_pipeline import (
    run_pipeline, MathLogicGate, DeepReasoningGate, COUNTING_KEYWORDS,
    _extract_gates_section, _dag_checks,
    SchemaPreflightGate, DryRunGate, ErrorPatternDB, AttemptGuard,
)
from scripts.gate_skill_invoker import (
    run_all_mandatory_skills, run_mandatory_skills_for_gate,
    verify_skill_readiness, find_skill, GATE_MANDATORY_SKILLS,
)
from hitl_gate import HITLGate, DEFAULT_TIMEOUT_MINUTES


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


# ---------------------------------------------------------------------------
# Stage 1: SECURITY
# ---------------------------------------------------------------------------

def test_clean_workflow_approved():
    wf = _wf([_node("Receive Webhook", "n8n-nodes-base.webhook",
                    path="h", authentication="headerAuth",
                    pinnedData={"1": {"json": {"id": 1}}}),
              _node("Send HTTP Response")],
             {"Receive Webhook": {"main": [{"node": "Send HTTP Response"}]}})
    res = _run(wf)
    assert res["verdict"] == "READY_FOR_DEPLOYMENT"
    assert res["stages"]["security"]["status"] == "APPROVED"


def test_child_process_is_fatal():
    wf = _wf([_node("Execute Code", "n8n-nodes-base.code",
                    jsCode="require('child_process').exec('rm -rf /');")])
    res = _run(wf, hitl=False)
    assert res["verdict"] == "REJECTED_SECURITY_RISK"
    assert any("child_process" in v for v in res["stages"]["security"]["violations"])


def test_ssrf_metadata_is_fatal():
    wf = _wf([_node("Steal Metadata", parameters={"url": "http://169.254.169.254/latest/meta-data/"})])
    res = _run(wf, hitl=False)
    assert res["verdict"] == "REJECTED_SECURITY_RISK"


def test_hardcoded_secret_is_fatal():
    wf = _wf([_node("Call OpenAI", parameters={"url": "https://api.openai.com"})],
             extra={"_gates": {"math": {}}})
    # inject a secret into a node parameter
    wf["nodes"][0]["parameters"]["options"] = {"headers": {"Authorization": "Bearer sk-1234567890abcdefghijklmn"}}
    res = _run(wf, hitl=False)
    assert res["verdict"] == "REJECTED_SECURITY_RISK"
    assert any("secret" in v.lower() for v in res["stages"]["security"]["violations"])


# ---------------------------------------------------------------------------
# Stage 2: QUALITY
# ---------------------------------------------------------------------------

def test_bare_json_quality_reject():
    wf = _wf([_node("Receive Webhook", "n8n-nodes-base.webhook",
                    path="h", authentication="headerAuth"),
              _node("Transform Data", "n8n-nodes-base.code",
                    jsCode="return [{ json: { v: $json, x: 1 } }];")],
             {"Receive Webhook": {"main": [{"node": "Transform Data"}]}})
    res = _run(wf)
    assert res["verdict"] == "QUALITY_VIOLATION"
    assert res["stages"]["quality"]["quality_score"] < 80


def test_oversized_workflow_quality_reject():
    nodes = [_node("Receive Webhook", "n8n-nodes-base.webhook",
                   path="h", authentication="headerAuth")] + \
            [_node(f"Step {i}", "n8n-nodes-base.code", jsCode="return [];") for i in range(12)]
    res = _run(_wf(nodes))
    assert res["verdict"] == "QUALITY_VIOLATION"
    assert any("nodes" in v for v in res["stages"]["quality"]["violations"])


# ---------------------------------------------------------------------------
# Stage 3: INTEGRITY (DAG)
# ---------------------------------------------------------------------------

def test_orphan_dependency_fails_integrity():
    wf = _wf([_node("A"), _node("B"), _node("C")],
             {"A": {"main": [{"node": "B"}]}, "B": {"main": [{"node": "Ghost"}]}})
    assert _dag_checks(wf)


def test_cycle_detected():
    wf = _wf([_node("A"), _node("B")],
             {"A": {"main": [{"node": "B"}]}, "B": {"main": [{"node": "A"}]}})
    assert any("cycle" in v for v in _dag_checks(wf))


def test_linear_dag_clean():
    wf = _wf([_node("A"), _node("B")],
             {"A": {"main": [{"node": "B"}]}})
    assert _dag_checks(wf) == []


def test_loop_back_edge_not_cycle():
    # Canonical splitInBatches v3: body loops back into the loop node to
    # trigger the next iteration. That edge must NOT be flagged as a DAG cycle
    # (the A2 check already blesses this pattern); genuine cycles still fail.
    wf = _wf([_node("Loop", ntype="n8n-nodes-base.splitInBatches"),
              _node("Work")],
             {"Loop": {"main": [[], [{"node": "Work"}]]},
              "Work": {"main": [{"node": "Loop"}]}})
    assert _dag_checks(wf) == []


# ---------------------------------------------------------------------------
# Stage 4: MATH (math-verify + z3 + voting)
# ---------------------------------------------------------------------------

def test_math_verify_equivalence_pass():
    gates = {"math": {"answer": "1/3", "expected": "0.3333333333333333"}}
    res = MathLogicGate().run(gates, "")
    assert res["status"] == "PASS"


def test_math_verify_mismatch_fail():
    gates = {"math": {"answer": "150", "expected": "149"}}
    res = MathLogicGate().run(gates, "")
    assert res["status"] == "FAIL"
    assert res["violations"]


def test_z3_unsat_fails():
    gates = {"z3": {"vars": {"x": 1, "y": 1},
                    "assertions": ["x + y == 10", "x - y == 4", "x * y == 25"]}}
    res = MathLogicGate().run(gates, "")
    assert res["status"] == "FAIL"


def test_z3_sat_pass():
    gates = {"z3": {"vars": {"x": 1, "y": 1},
                    "assertions": ["x + y == 10", "x - y == 4"]}}
    res = MathLogicGate().run(gates, "")
    assert res["status"] == "PASS"


def test_vote_majority_wins():
    gates = {"vote": {"candidates": [{"answer": "149"}, {"answer": "149"}, {"answer": "150"}]}}
    res = MathLogicGate().run(gates, "")
    assert res["status"] == "PASS"


def test_vote_tie_escalates():
    gates = {"vote": {"candidates": [{"answer": "149"}, {"answer": "150"}]}}
    res = MathLogicGate().run(gates, "")
    assert res["status"] == "NEEDS_REVIEW"


# ---------------------------------------------------------------------------
# Stage 5: REASONING (boundary/counting escalation)
# ---------------------------------------------------------------------------

def test_counting_keyword_boundaries():
    assert COUNTING_KEYWORDS.search("how many roots in (0, 2pi)?")
    assert COUNTING_KEYWORDS.search("count the solutions")
    # 'country' / 'countryLabel' must NOT trigger
    assert not COUNTING_KEYWORDS.search("SELECT ?countryLabel WHERE { ?country wdt:P30 wd:Q46 }")


def test_counting_without_expected_escalates():
    gates = {"counting": {"answer": 149}}
    math = MathLogicGate().run(gates, "")
    reason = DeepReasoningGate().run({}, "how many solutions in the interval", gates, math["status"])
    assert reason["status"] == "NEEDS_REVIEW"


def test_counting_with_expected_pass():
    gates = {"counting": {"answer": 149, "expected": 149},
             "math": {"answer": "149", "expected": "149"}}
    math = MathLogicGate().run(gates, "")
    reason = DeepReasoningGate().run({}, "how many solutions", gates, math["status"])
    assert reason["status"] != "NEEDS_REVIEW"


def test_no_counting_clean_pass():
    math = MathLogicGate().run({}, "")
    reason = DeepReasoningGate().run({}, "fetch homepages and extract emails", {}, math["status"])
    assert reason["status"] == "PASS"


# ---------------------------------------------------------------------------
# Stage 6: HITL
# ---------------------------------------------------------------------------

def test_security_reject_routes_to_hitl_pending(tmp_path):
    wf = _wf([_node("Evil", "n8n-nodes-base.code", jsCode="require('child_process');")])
    res = _run(wf, hitl=True)
    assert res["verdict"] == "PENDING_HUMAN_REVIEW"
    assert res["hitl_request"]["request_id"]


def test_hitl_approve_requires_token(tmp_path):
    db = tmp_path / "audit.db"
    gate = HITLGate(db_path=str(db), timeout_minutes=DEFAULT_TIMEOUT_MINUTES,
                    security_token="secret-token")
    req = gate.create_pending(raw_input="x", risk_score=45, violations=["v"])
    assert gate.approve(req.request_id, "wrong")["status"] == "INVALID_TOKEN"
    assert gate.approve(req.request_id, "secret-token")["status"] == "OVERRIDE_APPROVED"
    assert gate.reject(req.request_id, "late")["status"] == "OVERRIDE_APPROVED"


def test_hitl_default_deny_on_expiry(tmp_path):
    db = tmp_path / "audit.db"
    gate = HITLGate(db_path=str(db), timeout_minutes=0)
    req = gate.create_pending(raw_input="x", risk_score=50, violations=["v"])
    expired = gate.sweep_expired()
    assert req.request_id in expired
    assert gate.get(req.request_id).state == "EXPIRED_REJECTED"


def test_hitl_reject_hard_reject(tmp_path):
    db = tmp_path / "audit.db"
    gate = HITLGate(db_path=str(db))
    req = gate.create_pending(raw_input="x", risk_score=30, violations=[])
    assert gate.reject(req.request_id, "user said no")["status"] == "HARD_REJECT"


# ---------------------------------------------------------------------------
# Feature 1: SCHEMA PREFLIGHT (zero gate before generation)
# ---------------------------------------------------------------------------

def test_schema_preflight_needs_review_without_cache():
    wf = _wf([_node("A")])
    res = SchemaPreflightGate().run(wf, schema_cache=None)
    assert res["status"] == "NEEDS_REVIEW"
    assert any("no schema cache" in v for v in res["violations"])


def test_schema_preflight_unknown_node_type_fails():
    wf = _wf([_node("A", "n8n-nodes-base.ghostNode")])
    cache = {"n8n-nodes-base.httpRequest": {"required": []}}
    res = SchemaPreflightGate().run(wf, schema_cache=cache)
    assert res["status"] == "FAIL"
    assert any("ghostNode" in v for v in res["violations"])


def test_schema_preflight_missing_required_param_fails():
    wf = _wf([_node("A", "n8n-nodes-base.httpRequest")])
    cache = {"n8n-nodes-base.httpRequest": {"required": ["url"]}}
    res = SchemaPreflightGate().run(wf, schema_cache=cache)
    assert res["status"] == "FAIL"
    assert any("missing required" in v for v in res["violations"])


def test_schema_preflight_pass():
    wf = _wf([_node("A", "n8n-nodes-base.httpRequest", url="https://example.com")])
    cache = {"n8n-nodes-base.httpRequest": {"required": ["url"]}}
    res = SchemaPreflightGate().run(wf, schema_cache=cache)
    assert res["status"] == "PASS"
    assert res["checked"] == 1


def test_preflight_fail_blocks_deployment():
    wf = _wf([_node("A", "n8n-nodes-base.ghostNode")])
    cache = {"n8n-nodes-base.httpRequest": {"required": []}}
    full_text = json.dumps(wf)
    res = run_pipeline(wf, full_text, hitl=False, reporter=_SilentReporter(),
                       schema_cache=cache)
    assert res["verdict"] == "SCHEMA_PREFLIGHT_FAILED"


# ---------------------------------------------------------------------------
# Feature 3: DRY-RUN (real trial evidence before delivery)
# ---------------------------------------------------------------------------

def test_dry_run_fails_without_evidence():
    wf = _wf([_node("A", "n8n-nodes-base.httpRequest", url="https://example.com")])
    res = DryRunGate().run(wf, {})
    assert res["status"] == "FAIL"
    assert any("dry-run" in v for v in res["violations"])


def test_dry_run_pass_with_pinned_data():
    wf = _wf([_node("A", "n8n-nodes-base.httpRequest", url="https://example.com",
                    pinnedData={"1": {"json": {"ok": True}}})])
    res = DryRunGate().run(wf, {})
    assert res["status"] == "PASS"


def test_dry_run_pass_with_expected_result():
    wf = _wf([_node("A", "n8n-nodes-base.httpRequest", url="https://example.com")],
             extra={"_gates": {"dry_run": {"expected_result": "https://example.com"}}})
    gates = _extract_gates_section(wf)
    res = DryRunGate().run(wf, gates)
    assert res["status"] == "PASS"


def test_dry_run_skip_without_nodes():
    res = DryRunGate().run({"nodes": []}, {})
    assert res["status"] == "SKIP"


def test_clean_workflow_without_evidence_rejected():
    # even a perfect workflow must carry trial evidence before it ships
    wf = _wf([_node("Receive Webhook", "n8n-nodes-base.webhook",
                    path="h", authentication="headerAuth"),
              _node("Fetch Homepage", "n8n-nodes-base.httpRequest", url="https://example.com",
                    continueOnFail=True),
              _node("Send Telegram Message", "n8n-nodes-base.httpRequest", url="https://example.com")],
             {"Receive Webhook": {"main": [{"node": "Fetch Homepage"}]},
              "Fetch Homepage": {"main": [{"node": "Send Telegram Message"}]}})
    res = _run(wf)
    assert res["verdict"] == "DRY_RUN_EVIDENCE_MISSING"
    assert res["reason_code"] == "RUN_TRIAL_EXECUTION_FIRST"


def test_dry_run_does_not_mask_security():
    # security violations stay the primary verdict (dry-run is last resort)
    wf = _wf([_node("Steal Metadata", parameters={"url": "http://169.254.169.254/latest/meta-data/"})])
    res = _run(wf, hitl=False)
    assert res["verdict"] == "REJECTED_SECURITY_RISK"


def test_dry_run_does_not_mask_quality():
    # oversized workflow -> QUALITY_VIOLATION, not DRY_RUN_EVIDENCE_MISSING
    nodes = [_node("Receive Webhook", "n8n-nodes-base.webhook",
                   path="h", authentication="headerAuth")] + \
            [_node(f"Step {i}", "n8n-nodes-base.code", jsCode="return [];") for i in range(12)]
    res = _run(_wf(nodes))
    assert res["verdict"] == "QUALITY_VIOLATION"


# ---------------------------------------------------------------------------
# Feature 5: ERROR PATTERN DB (accumulated failure memory)
# ---------------------------------------------------------------------------

def test_error_pattern_db_records_and_dedups(tmp_path):
    db = ErrorPatternDB(tmp_path / "patterns.json")
    db.record("quality", "bare $json in code node")
    db.record("quality", "bare $json in code node")
    db.record("quality", "12 nodes exceed limit")
    lst = db.avoid_list(limit=10)
    assert "bare $json in code node" in lst
    assert "12 nodes exceed limit" in lst
    data = json.loads((tmp_path / "patterns.json").read_text())
    counts = {p["pattern"]: p["count"] for p in data}
    assert counts["bare $json in code node"] == 2
    assert counts["12 nodes exceed limit"] == 1


def test_error_patterns_injected_into_reasoning(tmp_path):
    db = ErrorPatternDB(tmp_path / "patterns.json")
    db.record("quality", "legacy $json syntax")
    gates = {}
    math = MathLogicGate().run(gates, "")
    reason = DeepReasoningGate().run({}, "fetch homepages", gates, math["status"],
                                     known_patterns=db.avoid_list())
    assert any("legacy $json syntax" in n for n in reason["notes"])


# ---------------------------------------------------------------------------
# Feature 6: ATTEMPT GUARD (loop/attempt budget)
# ---------------------------------------------------------------------------

def test_attempt_guard_continues_within_budget(tmp_path):
    g = AttemptGuard(tmp_path / "attempts.json")
    assert g.register("wf1", "QUALITY_VIOLATION", "bare $json", 1.0) == "CONTINUE"
    assert g.register("wf1", "QUALITY_VIOLATION", "bare $json", 1.0) == "CONTINUE"


def test_attempt_guard_stops_after_repeats(tmp_path):
    g = AttemptGuard(tmp_path / "attempts.json")
    assert g.register("wf1", "QUALITY_VIOLATION", "bare $json", 1.0) == "CONTINUE"
    assert g.register("wf1", "QUALITY_VIOLATION", "bare $json", 1.0) == "CONTINUE"
    assert g.register("wf1", "QUALITY_VIOLATION", "bare $json", 1.0) == "STOP"


def test_attempt_guard_stops_on_timeout(tmp_path):
    g = AttemptGuard(tmp_path / "attempts.json")
    assert g.register("wf2", "QUALITY_VIOLATION", "slow gate", 9999.0) == "STOP"


def test_attempt_guard_stops_pipeline(tmp_path, monkeypatch):
    from scripts import build_gates_pipeline as bgp
    monkeypatch.setattr(bgp, "MAX_SAME_REASON_REJECTIONS", 0)
    g = AttemptGuard(tmp_path / "attempts.json")
    wf = _wf([_node("Receive Webhook", "n8n-nodes-base.webhook",
                    path="h", authentication="headerAuth"),
              _node("Fetch Homepage", "n8n-nodes-base.httpRequest", url="https://example.com",
                    continueOnFail=True),
              _node("Send Telegram Message", "n8n-nodes-base.httpRequest", url="https://example.com")],
             {"Receive Webhook": {"main": [{"node": "Fetch Homepage"}]},
              "Fetch Homepage": {"main": [{"node": "Send Telegram Message"}]}})
    full_text = json.dumps(wf)
    res = run_pipeline(wf, full_text, hitl=False, reporter=_SilentReporter(),
                       attempt_guard=g, artifact_id="wf3")
    assert res["verdict"] == "LOOP_STOP_REQUIRES_USER"
    assert res["reason_code"] == "REPEATED_SAME_REASON_OR_TIMEOUT"


# ---------------------------------------------------------------------------
# Stage 7: AUDIT + full-pipeline integration
# ---------------------------------------------------------------------------

def test_audit_report_persisted(tmp_path, monkeypatch):
    from scripts import build_gates_pipeline as bgp
    monkeypatch.setattr(bgp, "AUDITS_DIR", tmp_path)
    wf = _wf([_node("Receive Webhook", "n8n-nodes-base.webhook",
                    path="h", authentication="headerAuth",
                    pinnedData={"1": {"json": {"id": 1}}}),
              _node("Send HTTP Response")],
             {"Receive Webhook": {"main": [{"node": "Send HTTP Response"}]}})
    full_text = json.dumps(wf)
    res = run_pipeline(wf, full_text, hitl=False, reporter=_SilentReporter())
    bgp._persist_audit(res, full_text)
    files = list(tmp_path.glob("*.json"))
    assert len(files) == 1
    saved = json.loads(files[0].read_text())
    assert saved["verdict"] == "READY_FOR_DEPLOYMENT"


def test_full_pipeline_math_annotated_pass():
    wf = _wf([], extra={"_gates": {
        "math": {"answer": "149", "expected": "149"},
        "counting": {"answer": 149, "expected": 149},
        "vote": {"candidates": [{"answer": "149"}, {"answer": "149"}, {"answer": "150"}]},
    }})
    res = _run(wf)
    assert res["verdict"] == "READY_FOR_DEPLOYMENT"
    assert res["stages"]["math"]["status"] == "PASS"


def test_gates_section_extraction():
    artifact = {"nodes": [], "_gates": {"math": {"answer": "1"}}}
    assert _extract_gates_section(artifact) == {"math": {"answer": "1"}}
    assert _extract_gates_section("plain text") == {}


# ---------------------------------------------------------------------------
# Stage 3.5: SKILLS (GateSkillInvoker — mandatory-skill invocation, fail-closed)
# ---------------------------------------------------------------------------

def test_skills_stage_pass_all_installed():
    # Every mandatory gate skill is installed (project or global) with valid
    # frontmatter and routable — the clean baseline for this machine.
    res = run_all_mandatory_skills()
    assert res["status"] == "PASS"
    assert len(res["invoked"]) == len({
        s for skills in GATE_MANDATORY_SKILLS.values() for s in skills})
    assert all(i["status"] == "SUCCESS" for i in res["invoked"])


def test_skills_stage_reports_no_manifest():
    res = run_all_mandatory_skills()
    assert res["manifest_provided"] is False
    assert any("manifest" in v for v in res["violations"])


def test_manifest_missing_skill_blocks_pipeline():
    wf = _wf([_node("Receive Webhook", "n8n-nodes-base.webhook",
                    path="h", authentication="headerAuth",
                    pinnedData={"1": {"json": {"id": 1}}}),
              _node("Send HTTP Response")],
             {"Receive Webhook": {"main": [{"node": "Send HTTP Response"}]}})
    full_text = json.dumps(wf)
    # agent claims it loaded only ONE of the 11 mandatory skills
    res = run_pipeline(wf, full_text, hitl=False, reporter=_SilentReporter(),
                       skills_loaded={"security-review"})
    assert res["verdict"] == "MANDATORY_SKILL_VIOLATION"
    assert res["reason_code"] == "SKILL_INVOCATION_UNVERIFIED"
    assert res["stages"]["skills"]["status"] == "FAIL"
    assert res["skill_invocation_status"] == "FAIL"


def test_manifest_full_skills_allows_pass():
    wf = _wf([_node("Receive Webhook", "n8n-nodes-base.webhook",
                    path="h", authentication="headerAuth",
                    pinnedData={"1": {"json": {"id": 1}}}),
              _node("Send HTTP Response")],
             {"Receive Webhook": {"main": [{"node": "Send HTTP Response"}]}})
    loaded = {s for skills in GATE_MANDATORY_SKILLS.values() for s in skills}
    full_text = json.dumps(wf)
    res = run_pipeline(wf, full_text, hitl=False, reporter=_SilentReporter(),
                       skills_loaded=loaded)
    assert res["verdict"] == "READY_FOR_DEPLOYMENT"
    assert res["skill_invocation_status"] == "PASS"
    assert res["skill_manifest_provided"] is True


def test_missing_skill_dir_blocks(tmp_path, monkeypatch):
    import scripts.gate_skill_invoker as gsi
    # force the search roots to an empty dir -> every mandatory skill missing
    monkeypatch.setattr(gsi, "PROJECT_SKILLS", tmp_path / "empty")
    monkeypatch.setattr(gsi, "GLOBAL_SKILLS", tmp_path / "empty2")
    res = gsi.run_all_mandatory_skills()
    assert res["status"] == "FAIL"
    assert res["failed_gates"] == ["SECURITY", "QUALITY", "INTEGRITY", "PRECISION", "REASONING"]
    assert all(i["status"] == "FAILED" for i in res["invoked"])


def test_verify_skill_readiness_global_lookup():
    # n8n-validation-expert lives in global ~/.claude/skills, not the project
    ev = verify_skill_readiness("n8n-validation-expert")
    assert ev["exists"] is True
    assert ev["frontmatter_ok"] is True
    assert ev["name_matches"] is True


def test_unknown_gate_has_no_mandatory_skills():
    res = run_mandatory_skills_for_gate("NOPE_GATE", {})
    assert res["status"] == "NO_MANDATORY_SKILLS"


def test_security_gate_has_expected_mandatory_set():
    assert "security-review" in GATE_MANDATORY_SKILLS["SECURITY"]
    assert "frontier-red-team-auditor" in GATE_MANDATORY_SKILLS["SECURITY"]
    assert "off-by-one-boundary-guard" in GATE_MANDATORY_SKILLS["REASONING"]


def test_skills_failure_routes_to_hitl_when_enabled(tmp_path):
    import scripts.gate_skill_invoker as gsi
    monkeypatch_tmp = tmp_path
    # block by empty search roots so the SKILLS stage fails
    original_project, original_global = gsi.PROJECT_SKILLS, gsi.GLOBAL_SKILLS
    gsi.PROJECT_SKILLS = monkeypatch_tmp / "empty"
    gsi.GLOBAL_SKILLS = monkeypatch_tmp / "empty2"
    try:
        wf = _wf([_node("Receive Webhook", "n8n-nodes-base.webhook",
                        path="h", authentication="headerAuth"),
                  _node("A", "n8n-nodes-base.httpRequest", url="https://example.com",
                        continueOnFail=True),
                  _node("B", "n8n-nodes-base.httpRequest", url="https://example.com")],
                 {"Receive Webhook": {"main": [{"node": "A"}]},
                  "A": {"main": [{"node": "B"}]}})
        full_text = json.dumps(wf)
        res = run_pipeline(wf, full_text, hitl=True, reporter=_SilentReporter())
        assert res["verdict"] == "PENDING_HUMAN_REVIEW"
        assert res["hitl_request"]["request_id"]
    finally:
        gsi.PROJECT_SKILLS = original_project
        gsi.GLOBAL_SKILLS = original_global
