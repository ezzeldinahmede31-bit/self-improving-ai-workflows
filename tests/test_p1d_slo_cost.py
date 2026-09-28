"""Tests for slo.py and cost_governor.py."""


def test_slo_rate_breach_and_recovery():
    from slo import SLOEngine
    e = SLOEngine(window=50)
    e.add_target("agent", "tool_ok", op=">=", threshold=0.99, kind="rate")
    for _ in range(30):
        e.observe("agent", "tool_ok", 0.0, good=True)
    assert e.evaluate("agent", "tool_ok")["state"] == "ok"
    for _ in range(30):
        e.observe("agent", "tool_ok", 0.0, good=False)
    out = e.evaluate("agent", "tool_ok")
    assert out["state"] == "breached" and out["observed"] < 0.99


def test_slo_latency_at_risk_and_warming():
    from slo import SLOEngine
    e = SLOEngine(window=50)
    e.add_target("agent", "p95", op="<=", threshold=5.0, kind="p95")
    assert e.evaluate("agent", "p95")["state"] == "warming"
    for v in [4.6] * 25:
        e.observe("agent", "p95", v)
    assert e.evaluate("agent", "p95")["state"] == "at-risk"
    for v in [9.0] * 25:
        e.observe("agent", "p95", v)
    assert e.evaluate("agent", "p95")["state"] == "breached"
    assert e.evaluate("ghost", "x")["state"] == "unknown"


def test_cost_governor_escalation_ladder():
    from cost_governor import CostGovernor
    g = CostGovernor(warn_at=10.0, tight_at=50.0, critical_at=80.0,
                     freeze_at=100.0, cheap_model="tiny")
    assert g.record(cost=5.0)["level"] == "normal"
    assert g.record(cost=6.0)["level"] == "watch"
    out = g.record(cost=40.0, model="big", expensive_path=True)
    assert out["level"] == "tight" and "reroute_to_cheap" in out["actions"]
    out = g.record(cost=30.0)
    assert out["level"] == "critical" and "escalate_human" in out["actions"]
    out = g.record(cost=25.0)
    assert out["level"] == "frozen" and "block_spend" in out["actions"]
    assert len(g.history()) == 5


def test_cost_governor_bad_config():
    from cost_governor import CostGovernor
    import pytest
    with pytest.raises(ValueError):
        CostGovernor(warn_at=50.0, tight_at=10.0, critical_at=80.0,
                     freeze_at=100.0)
    g = CostGovernor(warn_at=1.0, tight_at=2.0, critical_at=3.0,
                     freeze_at=4.0)
    with pytest.raises(ValueError):
        g.record(cost=-1.0)
    assert g.status()["level"] == "normal"
