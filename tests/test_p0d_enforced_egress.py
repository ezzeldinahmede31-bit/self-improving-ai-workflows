"""Regression: network sensitive actions must declare egress URLs (strict)."""

import pytest

from enforced_execution import EnforcedExecutor, EnforcementError
from platform_wiring import EnforcementProfile


def _profile():
    return EnforcementProfile(
        policy={"default": "allow", "rules": []},
        egress=None,  # egress config irrelevant here; urls missing => deny
    )


def _executor():
    from capability import CapabilityIssuer
    prof = _profile()
    prof.capability_secret = b"0123456789abcdef"
    iss = CapabilityIssuer(prof.capability_secret)
    tok = iss.issue(actions=["http.fetch"], resource="*")
    return EnforcedExecutor(prof, strict=True), iss, tok


def test_network_action_without_urls_denied_strict():
    ex, iss, tok = _executor()
    with pytest.raises(EnforcementError, match="without declared urls"):
        ex.execute(action="http.fetch", actor="a", resource="r",
                   capability_token=tok, capability_issuer=iss,
                   run=lambda: "should-not-run")


def test_network_action_with_blocked_url_denied():
    import platform_wiring
    from egress_firewall import EgressPolicy
    prof = EnforcementProfile(
        policy={"default": "allow", "rules": []},
        egress=EgressPolicy(),
    )
    prof.capability_secret = b"0123456789abcdef"
    from capability import CapabilityIssuer
    iss = CapabilityIssuer(prof.capability_secret)
    tok = iss.issue(actions=["http.fetch"], resource="*")
    ex = EnforcedExecutor(prof, strict=True)
    with pytest.raises(EnforcementError, match="egress blocked"):
        ex.execute(action="http.fetch", actor="a", resource="r",
                   urls=["http://127.0.0.1/"],
                   capability_token=tok, capability_issuer=iss,
                   run=lambda: "should-not-run")


def test_non_network_action_without_urls_allowed():
    ex, iss, tok2 = _executor()
    from capability import CapabilityIssuer
    iss2 = CapabilityIssuer(b"0123456789abcdef")
    tok = iss2.issue(actions=["memory.write"], resource="*")
    ex2 = EnforcedExecutor(
        EnforcementProfile(policy={"default": "allow", "rules": []}),
        strict=True)
    verdict, result = ex2.execute(
        action="memory.write", actor="a", resource="r",
        capability_token=tok, capability_issuer=iss2,
        run=lambda: "ok")
    assert verdict.allowed and result == "ok"
