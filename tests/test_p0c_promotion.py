"""Tests for promotion_pipeline.py."""

from promotion_pipeline import STAGES, PromotionPipeline


def _pass(_c):
    return True, "ok"


def _stages(**over):
    d = {s: _pass for s in STAGES if s != "promote"}
    d["promote"] = lambda c: (True, "promoted")
    d.update(over)
    return d


def test_full_pass_promotes(tmp_path):
    p = PromotionPipeline(str(tmp_path / "runs.jsonl"))
    out = p.run("cand-1", {"x": 1}, _stages())
    assert out["promoted"] is True and out["halted_at"] is None
    assert len(p.history()) == 1


def test_first_failure_halts(tmp_path):
    p = PromotionPipeline(str(tmp_path / "runs.jsonl"))

    def bad(_c):
        return False, "regression red"

    out = p.run("cand-2", {}, _stages(regression=bad))
    assert out["promoted"] is False and out["halted_at"] == "regression"
    assert "sandbox" not in out["stages"]


def test_promote_refused_without_approval(tmp_path):
    p = PromotionPipeline(str(tmp_path / "runs.jsonl"))
    stages = _stages()
    stages["approval"] = lambda c: (False, "human said no")
    out = p.run("cand-3", {}, stages)
    assert out["promoted"] is False


def test_missing_stage_halts(tmp_path):
    p = PromotionPipeline(str(tmp_path / "runs.jsonl"))
    stages = _stages()
    del stages["eval"]
    out = p.run("cand-4", {}, stages)
    assert out["halted_at"] == "eval"


def test_crashing_stage_halts(tmp_path):
    p = PromotionPipeline(str(tmp_path / "runs.jsonl"))

    def boom(_c):
        raise RuntimeError("stage bug")

    out = p.run("cand-5", {}, _stages(unit=boom))
    assert out["promoted"] is False and out["halted_at"] == "unit"


def test_stage_order_fixed():
    assert STAGES == ("scan", "unit", "regression", "sandbox", "eval",
                      "approval", "promote")
