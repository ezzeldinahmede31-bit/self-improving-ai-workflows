"""Tests for dep_drift.py and api_monitor.py."""


def test_dep_drift_classify_and_verdict():
    from dep_drift import DependencyDrift
    d = DependencyDrift()
    d.pin({"a": "1.0.0", "b": "2.1.0", "c": "3.0.0"}, {"img": "sha:1"})
    diff = d.check({"a": "1.0.0", "b": "2.2.0", "d": "1.0.0"},
                   {"img": "sha:1"})
    assert diff["added"] == ["d"] and diff["same"] == 1
    assert diff["upgraded"][0]["major_change"] is False
    v = d.verdict(diff)
    assert v["drifted"] and v["security_relevant"] and \
        "retest" in v["actions"]
    diff2 = d.check({"a": "1.0.0", "b": "2.1.0", "c": "3.0.0"},
                    {"img": "sha:1"})
    v2 = d.verdict(diff2)
    assert not v2["drifted"] and v2["actions"] == ["log"]


def test_dep_major_bump_and_removal():
    from dep_drift import DependencyDrift
    d = DependencyDrift()
    d.pin({"a": "1.0.0"})
    diff = d.check({"a": "9.0.0"})
    assert diff["upgraded"][0]["major_change"] is True
    diff = d.check({})
    assert diff["removed"] == ["a"]
    assert d.verdict(diff)["security_relevant"] is True


def test_api_monitor_green_and_change():
    from api_monitor import ApiMonitor
    m = ApiMonitor()
    m.watch("tg", lambda: ("ok", {"ok": True}, 0.1, "v1"),
            expected_keys=["ok"], max_latency_s=2.0,
            known_errors=["busy"], version="v1")
    m.attach("tg", lambda: ("ok", {"ok": True}, 0.1, "v1"))
    assert m.check("tg")["ok"] is True
    m.attach("tg", lambda: ("ok", {}, 0.1, "v1"))
    out = m.check("tg")
    assert not out["ok"] and len(m.findings) == 1
    m.attach("tg", lambda: ("weird", {"ok": True}, 0.1, "v1"))
    assert not m.check("tg")["ok"]
    assert m.check("ghost")["ok"] is False
    import pytest
    with pytest.raises(KeyError):
        m.attach("ghost", lambda: None)
