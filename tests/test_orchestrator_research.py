"""Tests for the Pre-Build Research capability.

Every acceptance bullet maps to a test below. Findings here are
representative fixtures (not live claims); the one LIVE pass is the
operator-executed demo documented in the final report, whose outputs are
re-verified by test_live_demo_report_shape against the saved file.
"""
import json
import os

from orchestrator import research as R
from orchestrator.state import StateStore

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _store(tmp_path):
    return StateStore(str(tmp_path / "s.db"))


def _oss(name="shlink", license="MIT"):
    return {"name": name, "url": f"https://github.com/x/{name}",
            "arch": "php+mysql", "license": license, "activity": "active",
            "maintained": True, "tests": True,
            "sources": [f"https://github.com/x/{name}"]}


# -- depth policy -------------------------------------------------------
def test_depth_light_for_small(tmp_path):
    assert R.decide_depth({"complexity": "small"}) == "light"


def test_depth_deep_for_large_and_security():
    assert R.decide_depth({"complexity": "large", "importance": "high"}) == "deep"
    assert R.decide_depth({"security_sensitivity": "high"}) == "deep-security"


def test_plan_topics_match_depth():
    assert [t["topic"] for t in R.plan_research("g", "light")] == [
        "oss-candidates", "closed-candidates", "community-feedback"]
    assert "security-review" in [
        t["topic"] for t in R.plan_research("g", "deep-security")]


# -- findings validation --------------------------------------------------
def test_oss_finding_needs_sources_and_fields():
    assert R.validate_finding("oss-candidate", {"name": "x"})
    assert R.validate_finding("oss-candidate", _oss()) == []


def test_closed_finding_forbids_code():
    bad = {"name": "bitly", "sources": ["https://bitly.com"],
           "strengths_observed": ["fast"], "code": "print(1)"}
    assert any("must not contain code" in e
               for e in R.validate_finding("closed-candidate", bad))
    good = dict(bad)
    del good["code"]
    assert R.validate_finding("closed-candidate", good) == []


def test_feedback_kind_classification_required():
    bad = {"claim": "slow", "source": "u1"}
    assert R.validate_finding("community-feedback", bad)
    good = dict(bad, source_kind="documented-issue")
    assert R.validate_finding("community-feedback", good) == []


# -- complaint mining ------------------------------------------------------
def test_repeated_needs_two_sources_and_ignores_single_opinion():
    fb = [
        {"claim": "Slow UI", "source": "issue-1",
         "source_kind": "documented-issue"},
        {"claim": "slow ui", "source": "reddit-2",
         "source_kind": "repeated-pattern"},
        {"claim": "Slow UI", "source": "blog-3",
         "source_kind": "individual-opinion"},
        {"claim": "I dislike blue", "source": "u-9",
         "source_kind": "individual-opinion"},
    ]
    out = R.repeated_complaints(fb)
    assert len(out) == 1 and out[0]["claim"] == "Slow UI"
    assert len(out[0]["sources"]) == 2  # opinion source excluded


# -- license gate ------------------------------------------------------------
def test_license_verdicts():
    assert R.license_verdict("MIT")[0] == "ALLOW"
    assert R.license_verdict("Apache-2.0")[0] == "ALLOW"
    assert R.license_verdict("GPL-3.0")[0] == "REVIEW"
    assert R.license_verdict(None)[0] == "DENY"
    assert R.license_verdict("NOASSERTION")[0] == "DENY"


def test_reuse_gate(tmp_path):
    store = _store(tmp_path)
    pid = store.create_project("r")
    store.add_finding(pid, "oss-candidate", "oss-candidates", _oss())
    store.add_finding(pid, "oss-candidate", "oss-candidates",
                      _oss("gpltool", "GPL-3.0"))
    ok, _ = R.reuse_verdict(store, pid, "shlink")
    assert ok is True
    ok2, why2 = R.reuse_verdict(store, pid, "gpltool")
    assert ok2 is False and "REVIEW" in why2
    ok3, _ = R.reuse_verdict(store, pid, "ghost")
    assert ok3 is False
    store.close()


# -- evidence rule --------------------------------------------------------------
def test_decision_needs_evidence(tmp_path):
    store = _store(tmp_path)
    pid = store.create_project("r")
    ok, _ = R.propose_decision(store, pid, "use X", "because", [])
    assert ok is False
    ok2, did = R.propose_decision(store, pid, "use X", "because",
                                  ["https://s"], {"add_constraints": ["c1"]})
    assert ok2 is True and did.startswith("d_")
    store.close()


def test_replace_needs_theirs_better(tmp_path):
    store = _store(tmp_path)
    pid = store.create_project("r")
    ok, _ = R.propose_decision(store, pid, "replace store", "why",
                               ["https://s"],
                               {"replace_ours": "state.py"}, None)
    assert ok is False
    ok2, _ = R.propose_decision(
        store, pid, "replace store", "why", ["https://s"],
        {"replace_ours": "state.py"}, {"verdict": "theirs-better"})
    assert ok2 is True
    store.close()


# -- apply + report + kb ----------------------------------------------------------
def test_apply_decisions_and_report(tmp_path):
    store = _store(tmp_path)
    pid = store.create_project("r")
    store.add_finding(pid, "oss-candidate", "oss-candidates", _oss())
    store.add_finding(pid, "closed-candidate", "closed",
                      {"name": "bitly", "sources": ["https://bitly.com"],
                       "strengths_observed": ["custom domains"]})
    store.add_finding(pid, "community-feedback", "community-feedback",
                      {"claim": "Slow UI", "source": "i1",
                       "source_kind": "documented-issue"})
    ok, did = R.propose_decision(
        store, pid, "Adopt short-id algorithm", "proven pattern",
        ["https://github.com/x/shlink"],
        {"add_constraints": ["ids must be non-sequential"],
         "reuse": ["shlink"], "avoid": ["sequential ids"]})
    assert ok
    store.set_decision_status(pid, did, "approved")
    applied = R.apply_decisions(store, pid)
    assert applied["constraints"] == ["ids must be non-sequential"]
    assert applied["reuses"][0]["component"] == "shlink"
    assert applied["avoided"][0]["pattern"] == "sequential ids"
    rep = str(tmp_path / "R.md")
    R.generate_report(store, pid, "demo shortener", rep)
    text = open(rep, encoding="utf-8").read()
    for section in R.REPORT_SECTIONS:
        assert section in text, section
    assert "bitly" in text and "shlink" in text
    store.close()


def test_kb_save_lookup_stale(tmp_path):
    store = _store(tmp_path)
    R.kb_save(store, "url shortener", {"a": 1}, ["https://s"], "p1")
    row = R.kb_lookup(store, "URL Shortener")
    assert row and row["stale"] is False
    assert R.kb_lookup(store, "nope") is None
    store.close()


def test_research_prompt_has_no_code_leak_vector():
    p = R.build_research_prompt("oss-candidates", "shortener", "light")
    assert "never code" in p and "shortener" in p


def test_report_creates_missing_dirs(tmp_path):
    from orchestrator.state import StateStore as SS
    store = SS(str(tmp_path / "s.db"))
    pid = store.create_project("r")
    out = str(tmp_path / "newdir" / "sub" / "R.md")
    R.generate_report(store, pid, "g", out)
    assert open(out, encoding="utf-8").read().startswith("# Research Report")
    store.close()


def test_live_demo_report_shape():
    path = os.path.join(ROOT, "research", "demo_url_shortener_RESEARCH.md")
    assert os.path.exists(path), "operator live demo must be run first"
    text = open(path, encoding="utf-8").read()
    for section in R.REPORT_SECTIONS:
        assert section in text, section
    assert "shlink" in text and "AGPL" in text and "bitly" in text
