"""Tests for deployment.py and tracing.py."""


def test_flag_buckets_stable():
    from deployment import FeatureFlags
    f = FeatureFlags()
    f.set("ui2", 50)
    a = f.enabled("ui2", "user-1")
    assert f.enabled("ui2", "user-1") == a  # stable per identity
    assert f.enabled("ui2") in (True, False)
    f.set("off", 0)
    assert f.enabled("off", "any") is False
    f.set("on", 100)
    assert f.enabled("on", "any") is True
    import pytest
    with pytest.raises(ValueError):
        f.set("x", 101)


def test_rollout_advances_then_rolls_back():
    from deployment import DeploymentController
    dc = DeploymentController()
    calls = []
    probes = {1: lambda: (True, {"err": 0.0}),
              10: lambda: (True, {"err": 0.01}),
              50: lambda: (False, {"err": 0.4}),
              100: lambda: (True, {})}
    out = dc.rollout("v2", "v1", probes, promote_fn=calls.append)
    assert out["rolled_back"] and out["live"] == "v1"
    assert [t["stage"] for t in out["trail"]] == [1, 10, 50]
    assert calls == [1, 10]
    assert dc.flags.enabled("release:v2", "u") is False


def test_rollout_full_green():
    from deployment import DeploymentController
    dc = DeploymentController()
    probes = {s: (lambda s=s: (True, {"err": 0.0})) for s in (1, 10, 50, 100)}
    out = dc.rollout("v3", "v2", probes)
    assert not out["rolled_back"] and out["live"] == "v3"


def test_rollout_missing_probe_halts():
    from deployment import DeploymentController
    dc = DeploymentController()
    out = dc.rollout("v4", "v3", {1: lambda: (True, {})})
    assert out["rolled_back"] and "probe" in out["reason"]


def test_trace_spans_and_report(tmp_path):
    from tracing import Tracer
    tr = Tracer(str(tmp_path / "t.jsonl"))
    ids = tr.start_trace(name="booking")
    with tr.span("n8n"):
        with tr.span("ai"):
            pass
    rep = tr.report(ids["trace_id"])
    assert len(rep["spans"]) == 2
    assert rep["total_s"] >= 0.0
    assert tr.current_ids()["trace_id"] == ids["trace_id"]


def test_trace_adopt_continues(tmp_path):
    from tracing import Tracer
    tr = Tracer(str(tmp_path / "t.jsonl"))
    ids = tr.start_trace(name="root")
    with tr.span("hop1"):
        child = tr.adopt(ids["trace_id"], tr.current_ids()["span_id"])
    assert child["trace_id"] == ids["trace_id"]
