"""Tests for capacity.py and health_probes.py."""


def test_capacity_headroom_and_forecast():
    from capacity import CapacityPlanner
    c = CapacityPlanner()
    s = c.snapshot(workers=4, in_flight=6, queue=10, cpu=0.5, ram=0.4,
                   api_used=100.0, api_limit=1000.0)
    assert c.headroom(s)["state"] == "green"
    out = c.forecast(10.0)
    assert out["first_breaker"] in ("cpu", "ram", "queue", "api")
    assert out["latency_multiplier_approx"] > 1.0
    import pytest
    with pytest.raises(ValueError):
        c.snapshot(workers=1, in_flight=0, queue=0, cpu=1.5, ram=0.1,
                   api_used=0.0, api_limit=1.0)
    assert CapacityPlanner().headroom()["state"] == "unknown"


def test_credential_health_windows():
    from health_probes import CredentialHealth
    h = CredentialHealth(warn_days=7.0)
    assert h.check("ghost")["state"] == "unknown"
    h.track("dated", 100 * 86400.0)
    assert h.check("dated", now=0.0)["state"] == "ok"
    assert h.check("dated", now=95 * 86400.0)["state"] == "renew-soon"
    assert h.check("dated", now=101 * 86400.0)["state"] == "expired"
    h.track("undated", None)
    assert h.check("undated")["state"] == "unknown"


def test_dependency_gate():
    from health_probes import DependencyHealth
    d = DependencyHealth(timeout_s=0.2)
    assert d.probe("ghost")["up"] is False
    d.add("closed", "127.0.0.1", 1)  # discard port: refused locally
    assert d.probe("closed")["up"] is False
    assert d.gate(["closed"]) == {"ok": False, "down": ["closed"]}


def test_synthetic_probe_cleans_up():
    from health_probes import SyntheticProbes
    p = SyntheticProbes()
    assert p.run("ghost")["healthy"] is False
    cleaned = []
    p.add("book", lambda: {"id": "fake-1"},
          lambda produced: (produced["id"] == "fake-1", ""),
          lambda produced: cleaned.append(produced["id"]))
    out = p.run("book")
    assert out["healthy"] and out["cleaned"] and cleaned == ["fake-1"]
    p.add("dirty", lambda: {"id": "x"}, lambda pr: (True, ""),
          lambda pr: (_ for _ in ()).throw(RuntimeError("stuck")))
    out2 = p.run("dirty")
    assert out2["healthy"] is False and out2["cleaned"] is False
