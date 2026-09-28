"""Tests for model_bench.py and model_drift.py."""


def _good(prompt):
    return {"output": '{"ok": true}', "tokens": 10, "cost": 0.01}


def _bad(prompt):
    return {"output": "nope", "tokens": 50, "cost": 0.05}


def _checker(_inp, out):
    return ('"ok": true' in out, "missing marker")


def test_bench_ranking_and_pick():
    from model_bench import ModelBench
    b = ModelBench()
    b.add_task("t1", "do it", _checker, dimension="reasoning")
    b.add_task("t2", "do it json", _checker, dimension="structured")
    out = b.compare({"good": _good, "bad": _bad})
    assert out["ranking"][0] == "good" and out["pick"] == "good"
    assert out["results"]["good"]["pass_rate"] == 1.0
    assert out["results"]["bad"]["pass_rate"] == 0.0
    assert b.tasks() == ["t1", "t2"]


def test_bench_model_crash_recorded():
    from model_bench import ModelBench, parses_json

    def boom(_p):
        raise RuntimeError("down")

    b = ModelBench()
    b.add_task("t1", "x", parses_json)
    res = b.run_suite(boom, model_name="m")
    assert res["pass_rate"] == 0.0 and "down" in res["rows"][0]["note"]


def test_drift_trip_and_action():
    from model_drift import DriftMonitor
    m = DriftMonitor(window=20)
    m.pin_baseline("tool_ok", 0.98, abs_tol=0.03, rel_tol=0.05,
                   direction="drop")
    for _ in range(12):
        m.observe("tool_ok", 0.98)
    assert m.check("tool_ok")["state"] == "ok"
    for _ in range(12):
        m.observe("tool_ok", 0.89)
    out = m.check("tool_ok")
    assert out["state"] == "drifted" and out["action"] in (
        "fallback", "rollback")


def test_drift_warming_and_unknown():
    from model_drift import DriftMonitor
    m = DriftMonitor(window=20)
    assert m.check("ghost")["state"] == "unknown"
    m.pin_baseline("x", 1.0)
    m.observe("x", 1.0)
    assert m.check("x")["state"] == "warming"
    assert m.mean("ghost") is None


def test_drift_direction_filter():
    from model_drift import DriftMonitor
    m = DriftMonitor(window=10)
    m.pin_baseline("cost", 1.0, abs_tol=0.01, rel_tol=0.01,
                   direction="rise")
    for _ in range(10):
        m.observe("cost", 0.5)  # improvement, wrong direction
    assert m.check("cost", min_samples=5)["state"] == "ok"
