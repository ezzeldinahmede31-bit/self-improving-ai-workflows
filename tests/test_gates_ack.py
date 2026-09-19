"""Tests for the `.gates-ack.json` sidecar mechanism (vendor-skill false-positive
acknowledgments): fail-closed loader + heuristic-only downgrade."""
import json

from scripts.build_gates_pipeline import (
    DeepReasoningGate,
    _load_gates_ack,
    _match_counting_ack,
)


def _ack(**over):
    base = {
        "finding": "counting/boundary heuristic flag",
        "verdict": "false-positive",
        "evidence": "trigger phrases are ordinary prose",
        "reviewer": "test",
        "date": "2026-09-19",
    }
    base.update(over)
    return base


def test_match_valid_ack_returns_evidence():
    note = _match_counting_ack([_ack()])
    assert "ordinary prose" in note and "test" in note


def test_match_ignores_malformed_entries():
    assert _match_counting_ack(None) == ""
    assert _match_counting_ack("not-a-list") == ""
    assert _match_counting_ack([{"finding": "x"}]) == ""
    assert _match_counting_ack([_ack(verdict="wontfix")]) == ""
    assert _match_counting_ack([_ack(evidence="")]) == ""
    assert _match_counting_ack([_ack(finding="unrelated topic")]) == ""


def test_reasoning_gate_ack_clears_heuristic_flag():
    text = "What data moves between systems and in which direction?"
    flagged = DeepReasoningGate().run({}, text, {}, "SKIP")
    assert flagged["status"] == "NEEDS_REVIEW"
    acked = DeepReasoningGate().run({}, text, {}, "SKIP", acks=[_ack()])
    assert acked["status"] == "HEURISTIC"
    assert any("ACK" in n for n in acked["notes"])


def test_ack_never_clears_math_fail_or_needs_review():
    text = "What data moves between systems and in which direction?"
    assert DeepReasoningGate().run({}, text, {}, "FAIL", acks=[_ack()])["status"] == "FAIL"
    assert DeepReasoningGate().run({}, "plain prose, no trigger", {}, "NEEDS_REVIEW",
                                   acks=[_ack()])["status"] == "NEEDS_REVIEW"


def test_loader_fail_closed(tmp_path):
    assert _load_gates_ack("/nonexistent/SKILL.md") == []
    outside = tmp_path / "wf.json"
    outside.write_text("{}")
    assert _load_gates_ack(str(outside)) == []
    skilldir = tmp_path / ".opencode" / "skills" / "demo"
    skilldir.mkdir(parents=True)
    art = skilldir / "SKILL.md"
    art.write_text("x")
    assert _load_gates_ack(str(art)) == []
    (skilldir / ".gates-ack.json").write_text("{bad json")
    assert _load_gates_ack(str(art)) == []
    entries = [_ack()]
    (skilldir / ".gates-ack.json").write_text(json.dumps(entries))
    assert _load_gates_ack(str(art)) == entries
