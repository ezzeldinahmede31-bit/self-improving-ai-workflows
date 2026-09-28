"""Tests for tenancy.py and privacy.py."""


def test_tenant_state_machine():
    from tenancy import Tenancy
    t = Tenancy()
    t.add_tenant("clinic-a", 100.0)
    assert t.record_spend("clinic-a", 10.0)["state"] == "ok"
    assert t.record_spend("clinic-a", 70.0)["state"] == "warning"
    out = t.record_spend("clinic-a", 25.0)
    assert out["state"] == "degraded" and "degrade_model" in out["actions"]
    out = t.record_spend("clinic-a", 10.0)
    assert out["state"] == "critical"
    out = t.record_spend("clinic-a", 20.0)
    assert out["state"] == "exceeded" and "block_new_spend" in out["actions"]
    st = t.status("clinic-a")
    assert st["spent"] == 135.0 and st["events"] == 5


def test_tenant_isolation_and_errors(tmp_path):
    import pytest
    from tenancy import Tenancy
    t = Tenancy(str(tmp_path / "ten.json"))
    t.add_tenant("a", 10.0)
    t.add_tenant("b", 10.0)
    assert t.namespaced("a", "cal") != t.namespaced("b", "cal")
    with pytest.raises(KeyError):
        t.namespaced("ghost", "x")
    with pytest.raises(KeyError):
        t.record_spend("ghost", 1.0)
    with pytest.raises(ValueError):
        t.record_spend("a", -1.0)
    with pytest.raises(ValueError):
        t.add_tenant("a", 5.0)
    t.save()
    t2 = Tenancy(str(tmp_path / "ten.json"))
    assert t2.status("a")["cap"] == 10.0


def test_privacy_dlp_and_minimize():
    from privacy import PrivacyGovernor
    g = PrivacyGovernor()
    g.classify("phone", "sensitive", ttl_s=3600)
    g.classify("name", "internal")
    assert g.check_text("call +20 100 234 5678 now") == ["phone"]
    assert g.check_text("plain status update") == []
    assert g.redact("mail me at a@b.com") == "mail me at [EMAIL]"
    assert g.minimize({"a": 1, "b": 2}, ["a"]) == {"a": 1}
    assert g.retention_due("phone", 0.0, now=99999.0) is True
    assert g.retention_due("name", 0.0, now=99999.0) is False
    rec = g.record_request("delete", "patient-7")
    assert rec["status"] == "open" and g.requests("open") == [rec]
    import pytest
    with pytest.raises(ValueError):
        g.classify("x", "cosmic")
    with pytest.raises(ValueError):
        g.record_request("migrate", "x")
