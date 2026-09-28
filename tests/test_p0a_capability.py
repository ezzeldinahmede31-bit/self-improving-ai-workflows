"""Tests for capability.py (scoped expiring revocable tokens)."""

import time

import pytest

from capability import CapabilityError, CapabilityIssuer


def _issuer():
    return CapabilityIssuer(secret=b"0" * 32)


def test_issue_and_verify_roundtrip():
    iss = _issuer()
    tok = iss.issue(actions=["calendar.read"], resource="cal:*")
    ok, why = iss.verify(tok, action="calendar.read", resource="cal:1")
    assert ok, why


def test_action_outside_scope_denied():
    iss = _issuer()
    tok = iss.issue(actions=["calendar.read"], resource="*")
    ok, why = iss.verify(tok, action="calendar.delete")
    assert not ok and "scope" in why


def test_resource_outside_scope_denied():
    iss = _issuer()
    tok = iss.issue(actions=["db.*"], resource="db:reports")
    ok, _ = iss.verify(tok, action="db.read", resource="db:prod")
    assert not ok


def test_tampered_token_rejected():
    iss = _issuer()
    tok = iss.issue(actions=["a"], resource="*")
    head, sig = tok.split(".")
    bad = head + "." + ("A" if sig[-1] != "A" else "B") + sig[1:]
    ok, _ = iss.verify(bad, action="a")
    assert not ok


def test_expiry_enforced():
    iss = _issuer()
    tok = iss.issue(actions=["a"], resource="*", ttl_s=1)
    # Fast-forward the clock instead of sleeping through the TTL.
    import capability as capmod
    real_time = capmod.time.time
    capmod.time.time = lambda: real_time() + 5000
    try:
        ok, why = iss.verify(tok, action="a")
    finally:
        capmod.time.time = real_time
    assert not ok and "expired" in why


def test_revoke_blocks_use():
    iss = _issuer()
    tok = iss.issue(actions=["a"], resource="*")
    body = iss._decode(tok)
    assert iss.revoke(body["id"]) is True
    ok, why = iss.verify(tok, action="a")
    assert not ok and "revoked" in why
    assert iss.revoke("no-such-id") is False


def test_attenuate_narrows_only():
    iss = _issuer()
    tok = iss.issue(actions=["calendar.*"], resource="*")
    child = iss.attenuate(tok, actions=["calendar.read"])
    ok, _ = iss.verify(child, action="calendar.read")
    assert ok
    ok, _ = iss.verify(child, action="calendar.delete")
    assert not ok
    with pytest.raises(CapabilityError):
        iss.attenuate(tok, actions=["admin.*"])


def test_empty_actions_rejected():
    iss = _issuer()
    with pytest.raises(ValueError):
        iss.issue(actions=[], resource="*")
