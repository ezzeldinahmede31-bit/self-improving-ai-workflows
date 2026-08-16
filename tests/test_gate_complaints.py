"""Tests for the per-gate ComplaintsRegistry (scripts/gate_complaints.py).

Covers: SKILL_GAP recording (when no local skill covers the violation topic),
SLOW recording (gate beyond the timeout budget), local-skill coverage
suppression, resolution via find-skills (auto-install a good hit / create a
skill in the gate's complaints folder / NO_SOLUTION), dedupe, and the ledger
file shape. Deterministic — finder/installer/skill_creator are injected fakes;
no network, no real memory writes (tmp dirs only).
"""

import json
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.gate_complaints import (
    ComplaintsRegistry, extract_keywords, default_find_skills, _skill_corpus,
    GATE_TIMEOUT_SECONDS,
)


def _make_registry(tmp_path, finder=None, installer=None, skill_creator=None):
    return ComplaintsRegistry(root=tmp_path, gate="TEST",
                              finder=finder, installer=installer,
                              skill_creator=skill_creator)


def _fake_finder(results):
    def finder(keywords):
        return list(results)
    return finder


def _read_ledger(tmp_path, gate="TEST"):
    p = tmp_path / "memory" / "gate_complaints" / f"{gate.upper()}.json"
    if not p.is_file():
        return []
    return json.loads(p.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Keyword extraction
# ---------------------------------------------------------------------------

def test_extract_keywords_filters_stopwords():
    kws = extract_keywords("the workflow node must not contain a secret token")
    assert "token" in kws
    assert "workflow" not in kws   # stopword
    assert "the" not in kws        # stopword


def test_extract_keywords_respects_limit():
    kws = extract_keywords("alpha beta gamma delta epsilon zeta eta theta iota", limit=4)
    assert len(kws) == 4


# ---------------------------------------------------------------------------
# Recording
# ---------------------------------------------------------------------------

def test_record_skill_gap_writes_complaint(tmp_path):
    reg = _make_registry(tmp_path)
    # a topic that no installed skill covers
    c = reg.record_skill_gap("TEST", "extremely obscure quantum-dot fabrication failure")
    assert c is not None
    assert c["kind"] == "SKILL_GAP"
    assert c["status"] == "OPEN"
    assert c["gate"] == "TEST"
    ledger = _read_ledger(tmp_path)
    assert len(ledger) == 1
    assert ledger[0]["id"] == c["id"]


def test_record_skill_gap_suppressed_when_local_skill_covers(tmp_path):
    reg = _make_registry(tmp_path)
    # "security" is covered by many installed skills (security-review etc.)
    c = reg.record_skill_gap("TEST", "security vulnerability in the workflow")
    assert c is None
    assert _read_ledger(tmp_path) == []


def test_record_skill_gap_dedupes_open_complaints(tmp_path):
    reg = _make_registry(tmp_path)
    msg = "quantum-dot fabrication failure xyz"
    c1 = reg.record_skill_gap("TEST", msg)
    c2 = reg.record_skill_gap("TEST", msg)
    assert c1 is not None
    assert c2 is None  # same gate+kind+keywords already OPEN
    assert len(_read_ledger(tmp_path)) == 1


def test_record_slow_under_budget_no_complaint(tmp_path):
    reg = _make_registry(tmp_path)
    c = reg.record_slow("TEST", 5.0, "SECURITY")
    assert c is None


def test_record_slow_over_budget_writes_complaint(tmp_path):
    reg = _make_registry(tmp_path)
    c = reg.record_slow("TEST", GATE_TIMEOUT_SECONDS + 30, "QUALITY")
    assert c is not None
    assert c["kind"] == "SLOW"
    assert c["elapsed_seconds"] > GATE_TIMEOUT_SECONDS


def test_empty_violation_is_ignored(tmp_path):
    reg = _make_registry(tmp_path)
    assert reg.record_skill_gap("TEST", "") is None
    assert _read_ledger(tmp_path) == []


# ---------------------------------------------------------------------------
# Resolution
# ---------------------------------------------------------------------------

def test_resolve_installs_good_hit(tmp_path):
    hits = [{"spec": "trusted/mega@fixer", "installs": 5000, "owner": "trusted",
             "installable": True}]
    installed = []
    reg = _make_registry(tmp_path, finder=_fake_finder(hits),
                         installer=lambda spec: (installed.append(spec) or True))
    reg.record_skill_gap("TEST", "quantum-dot fabrication failure xyz")
    res = reg.resolve_open()
    assert res["status"] == "COMPLAINTS_RESOLVED"
    assert len(res["installed"]) == 1
    assert installed == ["trusted/mega@fixer"]
    ledger = _read_ledger(tmp_path)
    assert ledger[0]["status"] == "SKILL_INSTALLED"
    assert ledger[0]["resolution"] == "trusted/mega@fixer"
    assert ledger[0]["resolved_at"] is not None


def test_resolve_creates_skill_when_not_installable(tmp_path):
    hits = [{"spec": "low/repo@weak", "installs": 5, "owner": "low",
             "installable": False}]
    created = []
    reg = _make_registry(tmp_path, finder=_fake_finder(hits),
                         installer=lambda spec: False,
                         skill_creator=lambda gate, c: (created.append(gate) or "/tmp/fake/SKILL.md"))
    reg.record_skill_gap("TEST", "quantum-dot fabrication failure xyz")
    res = reg.resolve_open()
    assert res["status"] == "COMPLAINTS_RESOLVED"
    assert len(res["created"]) == 1
    assert created == ["TEST"]
    assert _read_ledger(tmp_path)[0]["status"] == "SKILL_CREATED"


def test_resolve_no_hits_marks_no_solution(tmp_path):
    reg = _make_registry(tmp_path, finder=_fake_finder([]))
    reg.record_skill_gap("TEST", "quantum-dot fabrication failure xyz")
    res = reg.resolve_open()
    assert res["status"] == "COMPLAINTS_RESOLVED"
    assert res["no_solution"] == [_read_ledger(tmp_path)[0]["id"]]
    assert _read_ledger(tmp_path)[0]["status"] == "NO_SOLUTION"


def test_resolve_install_failure_falls_back_to_create(tmp_path):
    hits = [{"spec": "trusted/mega@fixer", "installs": 5000, "owner": "trusted",
             "installable": True}]
    created = []
    reg = _make_registry(tmp_path, finder=_fake_finder(hits),
                         installer=lambda spec: False,  # install fails
                         skill_creator=lambda gate, c: (created.append(gate) or "/tmp/fake/SKILL.md"))
    reg.record_skill_gap("TEST", "quantum-dot fabrication failure xyz")
    res = reg.resolve_open()
    assert len(res["created"]) == 1
    assert res["installed"] == []
    assert _read_ledger(tmp_path)[0]["status"] == "SKILL_CREATED"


def test_resolve_none_open_is_no_complaints(tmp_path):
    reg = _make_registry(tmp_path)
    res = reg.resolve_open()
    assert res["status"] == "NO_COMPLAINTS"
    assert res["processed"] == 0


def test_resolve_only_processes_open(tmp_path):
    reg = _make_registry(tmp_path)
    reg.record_skill_gap("TEST", "quantum-dot fabrication failure xyz")
    reg._set_status("TEST", _read_ledger(tmp_path)[0]["id"], "SKILL_INSTALLED", resolution="x")
    res = reg.resolve_open()
    assert res["status"] == "NO_COMPLAINTS"  # the only complaint is already resolved


# ---------------------------------------------------------------------------
# Default skill creator writes a real file
# ---------------------------------------------------------------------------

def test_default_create_skill_writes_skill_md(tmp_path):
    reg = _make_registry(tmp_path)
    complaint = {
        "id": "test-123", "gate": "TEST", "kind": "SKILL_GAP",
        "violation": "quantum-dot fabrication failure xyz",
        "keywords": ["quantum", "dot", "fabrication", "failure"],
        "created_at": "2026-08-15T00:00:00Z",
    }
    path = reg._skill_creator("TEST", complaint)
    assert path is not None
    p = Path(path)
    assert p.is_file()
    # the skill MUST be created under the registry's own root (tmp dir in
    # tests), never under the real project skill pack
    assert str(tmp_path) in str(p.resolve())
    text = p.read_text(encoding="utf-8")
    assert "quantum-dot fabrication failure xyz" in text
    assert text.startswith("---")


def test_summary_shape(tmp_path):
    reg = _make_registry(tmp_path)
    reg.record_skill_gap("TEST", "quantum-dot fabrication failure xyz")
    s = reg.summary("TEST")
    assert s["gate"] == "TEST"
    assert s["total"] == 1
    assert s["open"] == 1
    assert s["statuses"]["OPEN"] == 1


# ---------------------------------------------------------------------------
# Real npx finder parsing (offline — fake npx via PATH injection)
# ---------------------------------------------------------------------------

def test_default_find_skills_parses_rows_with_fake_npx(tmp_path):
    # simulate `npx skills find` output with a fake npx on PATH
    fake_npx = tmp_path / "bin" / "npx"
    fake_npx.parent.mkdir(parents=True)
    fake_npx.write_text(
        "#!/bin/sh\nprintf 'owner/repo@good 2000 installs\\nlow/weak@bad 5 installs\\n'\n")
    fake_npx.chmod(0o755)
    import subprocess
    import scripts.gate_complaints as gc
    orig = subprocess.run
    try:
        calls = {}
        def fake_run(cmd, **kw):
            calls["cmd"] = cmd
            return orig([str(fake_npx)] + cmd[2:], **kw)
        gc.subprocess.run = fake_run
        hits = gc.default_find_skills(["quantum", "dot"])
        assert any(h["spec"] == "owner/repo@good" and h["installable"] for h in hits)
        bad = next(h for h in hits if h["spec"] == "low/weak@bad")
        assert bad["installable"] is False
        assert calls.get("cmd") == ["npx", "-y", "skills", "find", "quantum dot"]
    finally:
        gc.subprocess.run = orig
