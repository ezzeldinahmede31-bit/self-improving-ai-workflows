"""Capability security matrix: TTL bypass vectors + escalation matrix.

Every row must hold: bounded TTL, scoped actions/resources/tenants,
attenuation-only descent, expiry, anti-forgery, anti-replay-after-revoke.
"""
import time

import pytest

from capability import CapabilityIssuer, CapabilityError, MAX_TTL_S

SECRET = b"0" * 32


def _iss():
    return CapabilityIssuer(secret=SECRET)


# ---- TTL bypass vectors ----

def test_ttl_default_bounded():
    iss = _iss()
    tok = iss.issue(actions=["a"])
    body = iss._decode(tok)
    assert body["exp"] - body["iat"] == 3600


@pytest.mark.parametrize("bad", [0, -1, -3600, MAX_TTL_S + 1, 10 ** 12,
                                 10 ** 30, float("inf"), float("-inf"),
                                 "huge", "", None, [600], {"t": 1}])
def test_ttl_bypass_vectors_rejected(bad):
    with pytest.raises(ValueError):
        _iss().issue(actions=["a"], ttl_s=bad)


def test_ttl_nan_rejected():
    with pytest.raises(ValueError):
        _iss().issue(actions=["a"], ttl_s=float("nan"))


def test_ttl_max_boundary_accepted():
    tok = _iss().issue(actions=["a"], ttl_s=MAX_TTL_S)
    body = _iss()._decode(tok)
    assert body["exp"] - body["iat"] == MAX_TTL_S


def test_ttl_string_integer_accepted_and_bounded():
    tok = _iss().issue(actions=["a"], ttl_s="600")
    assert _iss()._decode(tok)["exp"] - _iss()._decode(tok)["iat"] == 600


# ---- expiry / replay ----

def test_expired_token_denied():
    iss = _iss()
    tok = iss.issue(actions=["read"], resource="task:1", ttl_s=1)
    ok, _ = iss.verify(tok, action="read", resource="task:1")
    assert ok is True
    time.sleep(1.15)
    # 60s skew keeps it valid briefly; forge an actually-expired body instead
    import base64, hashlib, hmac as _hmac, json as _json
    body = iss._decode(tok)
    body["exp"] = int(time.time()) - 3600
    raw = _json.dumps(body, sort_keys=True,
                      separators=(",", ":")).encode()
    sig = base64.urlsafe_b64encode(
        _hmac.new(SECRET, raw, hashlib.sha256).digest()).decode().rstrip("=")
    old = base64.urlsafe_b64encode(raw).decode().rstrip("=") + "." + sig
    ok2, reason = iss.verify(old, action="read", resource="task:1")
    assert ok2 is False and "expired" in reason


def test_revoked_token_denied_replay_blocked():
    iss = _iss()
    tok = iss.issue(actions=["read"], resource="task:1", ttl_s=600)
    tid = iss._decode(tok)["id"]
    assert iss.revoke(tid) is True
    ok, reason = iss.verify(tok, action="read", resource="task:1")
    assert ok is False and "revoked" in reason


# ---- forgery ----

def test_forged_signature_rejected():
    iss = _iss()
    tok = iss.issue(actions=["read"], ttl_s=600)
    part, sig = tok.split(".")
    bad = part + "." + ("A" * len(sig))
    ok, _ = iss.verify(bad, action="read", resource="*")
    assert ok is False


def test_wrong_issuer_secret_rejected():
    tok = _iss().issue(actions=["read"], ttl_s=600)
    other = CapabilityIssuer(b"different-secret-16b!!")
    ok, _ = other.verify(tok, action="read", resource="*")
    assert ok is False


def test_tampered_payload_rejected():
    import base64
    iss = _iss()
    tok = iss.issue(actions=["read"], resource="task:1", ttl_s=600)
    part, sig = tok.split(".")
    raw = base64.urlsafe_b64decode(part + "=" * (-len(part) % 4))
    import json as _json
    body = _json.loads(raw.decode())
    body["act"] = ["*"]  # attacker widens scope, keeps signature
    new_part = base64.urlsafe_b64encode(
        _json.dumps(body, sort_keys=True,
                    separators=(",", ":")).encode()).decode().rstrip("=")
    ok, _ = iss.verify(new_part + "." + sig, action="nuke", resource="*")
    assert ok is False


# ---- substitution matrix ----

def test_tenant_substitution_denied():
    iss = _iss()
    tok = iss.issue(actions=["read"], resource="tenant:A", ttl_s=600)
    ok, _ = iss.verify(tok, action="read", resource="tenant:B")
    assert ok is False


def test_action_substitution_denied():
    iss = _iss()
    tok = iss.issue(actions=["read"], resource="task:1", ttl_s=600)
    ok, _ = iss.verify(tok, action="write", resource="task:1")
    assert ok is False


def test_resource_substitution_denied():
    iss = _iss()
    tok = iss.issue(actions=["read"], resource="task:1", ttl_s=600)
    ok, _ = iss.verify(tok, action="read", resource="task:2")
    assert ok is False


def test_glob_scope_still_bounded():
    iss = _iss()
    tok = iss.issue(actions=["net.fetch"], resource="task:*", ttl_s=600)
    ok, _ = iss.verify(tok, action="net.fetch", resource="task:9")
    assert ok is True
    ok2, _ = iss.verify(tok, action="net.fetch", resource="other:9")
    assert ok2 is False


# ---- attenuation ----

def test_attenuate_narrows_only():
    iss = _iss()
    parent = iss.issue(actions=["read", "write"], resource="task:*", ttl_s=600)
    child = iss.attenuate(parent, actions=["read"], resource="task:1")
    ok, _ = iss.verify(child, action="read", resource="task:1")
    assert ok is True
    ok2, _ = iss.verify(child, action="write", resource="task:1")
    assert ok2 is False
    with pytest.raises(CapabilityError):
        iss.attenuate(parent, actions=["read", "delete"])
    with pytest.raises(CapabilityError):
        iss.attenuate(parent, actions=["read"], resource="other:1")


def test_attenuate_cannot_extend_ttl_past_parent():
    iss = _iss()
    parent = iss.issue(actions=["read"], resource="*", ttl_s=100)
    child = iss.attenuate(parent, ttl_s=MAX_TTL_S)
    cbody = iss._decode(child)
    pbody = iss._decode(parent)
    assert cbody["exp"] <= pbody["exp"]


def test_attenuate_revoked_or_expired_parent_refused():
    iss = _iss()
    parent = iss.issue(actions=["read"], ttl_s=600)
    iss.revoke(iss._decode(parent)["id"])
    with pytest.raises(CapabilityError):
        iss.attenuate(parent, actions=["read"])
