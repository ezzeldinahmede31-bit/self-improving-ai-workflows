"""Tests for secrets_vault.py (short-lived scoped leases)."""

import pytest

from secrets_vault import Vault


def test_issue_redeem_single_use():
    v = Vault()
    lid, raw = v.issue(scope=["calendar.read"], ttl_s=60, max_uses=1)
    ok, _ = v.redeem(raw, operation="calendar.read")
    assert ok
    ok, why = v.redeem(raw, operation="calendar.read")
    assert not ok and "spent" in why


def test_scope_enforced():
    v = Vault()
    _, raw = v.issue(scope=["calendar.read"], ttl_s=60)
    ok, why = v.redeem(raw, operation="mail.send")
    assert not ok and "scope" in why


def test_unknown_token_rejected():
    v = Vault()
    ok, _ = v.redeem("vlt_nope", operation="x")
    assert not ok


def test_revoke_and_rotate():
    v = Vault()
    lid, raw = v.issue(scope=["db.read"], ttl_s=60)
    assert v.revoke(lid) is True
    ok, _ = v.redeem(raw, operation="db.read")
    assert not ok
    lid2, raw2 = v.issue(scope=["db.read"], ttl_s=60)
    rep = v.rotate(lid2, ttl_s=60)
    assert rep is not None
    _, raw3 = rep
    ok, _ = v.redeem(raw3, operation="db.read")
    assert ok
    ok, _ = v.redeem(raw2, operation="db.read")
    assert not ok  # old raw token died with rotation
    assert v.revoke("ls_missing") is False


def test_expiry_and_sweep(tmp_path):
    v = Vault()
    lid, _ = v.issue(scope=["a"], ttl_s=1)
    import secrets_vault as svmod
    import time as _t
    real = _t.time
    svmod.time.time = lambda: real() + 5000
    try:
        ok, why = v.redeem("vlt_x", operation="a")
        assert not ok  # unknown token path first (deterministic)
        removed = v.sweep_expired()
    finally:
        svmod.time.time = real
    assert removed == 1
    assert lid not in v.active()


def test_raw_token_never_stored():
    v = Vault()
    _, raw = v.issue(scope=["a"], ttl_s=60)
    blob = repr(v._leases)
    assert raw not in blob


def test_bad_issue_rejected():
    v = Vault()
    with pytest.raises(ValueError):
        v.issue(scope=[], ttl_s=60)
    with pytest.raises(ValueError):
        v.issue(scope=["a"], ttl_s=0)


def test_access_log_records():
    v = Vault()
    lid, raw = v.issue(scope=["a"], ttl_s=60, max_uses=2)
    v.redeem(raw, operation="a")
    kinds = [e["kind"] for e in v.events()]
    assert "issue" in kinds and "redeem" in kinds
