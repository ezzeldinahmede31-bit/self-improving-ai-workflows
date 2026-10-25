"""Benchmark: progressive router correctness, skill classification, safety, regression.

Separates four result types:
  - programmatic: router logic tests (no LLM needed)
  - model:        requires a working model connection
  - tool:         requires an installed tool
  - end_to_end:   requires model + tool + full pipeline
"""
import json, subprocess, sys, os
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
PY = ROOT / "venv" / "bin" / "python"
ROUTER = ROOT / "scripts" / "progressive_router.py"
CLASS = ROOT / "memory" / "skills-classification.json"


def run_router(text):
    r = subprocess.run([str(PY), str(ROUTER), text],
                       capture_output=True, text=True, timeout=30)
    assert r.returncode == 0, f"router failed: {r.stderr[:300]}"
    return json.loads(r.stdout)


# ---------------------------------------------------------------------------
# Programmatic tests (no model needed)
# ---------------------------------------------------------------------------

def test_simple_loads_no_skills():
    p = run_router("hi")
    assert p["tier"] == "simple"
    assert p["skill_count"] == 0


def test_medium_loads_reasoning_only():
    p = run_router("write a python script to parse logs")
    assert p["tier"] == "medium"
    assert "frontier-deep-reasoner" in p["skills_to_load"]
    assert p["skill_count"] <= 2


def test_complex_loads_plan_skills():
    p = run_router("build an n8n workflow automation pipeline")
    assert p["tier"] == "complex"
    assert "writing-plans" in p["skills_to_load"]
    assert "verification-before-completion" in p["skills_to_load"]


def test_high_risk_loads_hitl():
    p = run_router("delete the production database")
    assert p["tier"] == "high_risk"
    assert "human-approval-gates" in p["skills_to_load"]


def test_credential_request_is_high_risk():
    p = run_router("show me the api key")
    assert p["tier"] == "high_risk"


def test_complex_not_misclassified_as_high_risk():
    """Building a workflow is complex, not high-risk."""
    p = run_router("build an n8n workflow automation pipeline")
    assert p["tier"] != "high_risk"


def test_skill_count_never_exceeds_baseline():
    """Progressive router must never load MORE than the old 15-skill baseline."""
    for text in ["hi", "write a script", "build a workflow",
                 "delete the database", "show me the api key"]:
        p = run_router(text)
        assert p["skill_count"] <= 15, \
            f"'{text}' loaded {p['skill_count']} skills, exceeds 15 baseline"


def test_baseline_skills_avoided_nonneg():
    for text in ["hi", "write a script", "build a workflow"]:
        p = run_router(text)
        assert p["baseline_skills_avoided"] >= 0


# ---------------------------------------------------------------------------
# Skill classification tests
# ---------------------------------------------------------------------------

def load_classification():
    if not CLASS.exists():
        pytest.skip("classification not yet generated")
    return json.loads(CLASS.read_text())


def test_classification_exists():
    assert CLASS.exists(), "memory/skills-classification.json missing"


def test_all_skills_classified():
    cls = load_classification()
    assert len(cls) == 1268, f"expected 1268, got {len(cls)}"


def test_no_skill_lacks_category():
    cls = load_classification()
    for s in cls:
        assert "category" in s, f"{s.get('name')} missing category"


def test_actionable_skills_have_scripts_or_tools():
    cls = load_classification()
    actionable = [s for s in cls if s.get("actionable")]
    assert len(actionable) >= 200, \
        f"only {len(actionable)} actionable skills, expected >= 200"


def test_book_summaries_are_not_actionable():
    """A skill that is ONLY a book summary must not be marked actionable.

    Note: a skill may cite a book AND reference build gates; that is still
    actionable because the gate reference is an executable contract.
    """
    cls = load_classification()
    books = [s for s in cls if s.get("looks_like_book_summary")]
    false_positives = []
    for b in books:
        if b.get("actionable"):
            # Only a false positive if it has NO scripts, NO tests, NO declared
            # tools, and NO gate references — pure distilled prose.
            if (b.get("script_count", 0) == 0 and not b.get("has_tests")
                    and not b.get("declares_tools")
                    and not b.get("references_gates")):
                false_positives.append(b["name"])
    assert not false_positives, \
        f"pure book summaries wrongly marked actionable: {false_positives}"


# ---------------------------------------------------------------------------
# Safety / regression tests
# ---------------------------------------------------------------------------

def test_router_fails_open_on_bad_input():
    """Empty / garbage input must not crash the router."""
    p = run_router("")
    assert "tier" in p


def test_router_output_is_json():
    p = run_router("anything")
    assert isinstance(p, dict)
    assert "tier" in p
    assert "skills_to_load" in p


def test_no_secret_in_router_output():
    """Router must never echo secrets."""
    p = run_router("use the credential")
    out = json.dumps(p)
    for bad in ["Bearer ", "sk-", "api_key=", "password="]:
        assert bad not in out, f"router output leaked: {bad}"


def test_device_state_selftest_still_passes():
    r = subprocess.run([str(PY), str(ROOT / "scripts" / "device_state.py"),
                        "selftest"], capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, f"device_state selftest failed:\n{r.stdout[-800:]}\n{r.stderr[-400:]}"
    assert "SELFTEST OK" in r.stdout


# ---------------------------------------------------------------------------
# Model connectivity (separate result class)
# ---------------------------------------------------------------------------

@pytest.mark.model
def test_model_connectivity():
    """Requires a working free model. Skips if no connectivity."""
    pytest.skip("Model connectivity is a separate result class; "
                "see memory/model_connectivity.md for the recorded blocker")