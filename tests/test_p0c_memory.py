"""Tests for memory_governance.py."""

from memory_governance import MemoryGovernor


def _gov():
    return MemoryGovernor(
        trusted_sources=("ops-manual", "owner"),
        authority={"ops-manual": 10, "owner": 9, "user": 1})


def test_trusted_write_reads_back():
    g = _gov()
    g.write("price", 800, source="ops-manual", author="owner",
            confidence=0.9)
    assert g.read("price") == 800


def test_untrusted_quarantined_by_default():
    g = _gov()
    out = g.write("role", "admin", source="user", author="user")
    assert out["quarantined"] is True
    assert g.read("role") is None
    assert g.quarantine() == ["role"]


def test_admin_self_promote_attack_fails():
    g = _gov()
    g.write("role", "admin", source="user", author="user")
    # Promotion requires a TRUSTED author; the attacker is not one.
    assert g.promote("role", "user", by="user") is False
    assert g.read("role") is None
    assert g.promote("role", "user", by="owner") is True
    assert g.read("role") == "admin"


def test_conflict_resolves_by_authority_then_time():
    g = _gov()
    g.write("price", 1000, source="owner", author="owner")
    g.write("price", 800, source="ops-manual", author="owner")
    assert g.read("price") == 800
    assert len(g.archive()) == 1


def test_ttl_expiry_and_sweep():
    g = MemoryGovernor(trusted_sources=("s",))
    g.write("k", "v", source="s", ttl_s=1)
    import memory_governance as mg
    import time as _t
    real = _t.time
    mg.time.time = lambda: real() + 5000
    try:
        assert g.read("k") is None
        assert g.sweep() == 1
    finally:
        mg.time.time = real


def test_confidence_clamped():
    g = _gov()
    g.write("k", 1, source="owner", confidence=9.0)
    assert g.read("k") == 1
