"""DNS TTL policy + connection-boundary pinning (GAP-02 / GAP-03 closure).

Deterministic: fake resolvers + fake transports, no network.
Covers: TTL boundaries, cache expiry/negative/invalidate, pinned fetch,
DNS-change-to-hostile (rebind) races, redirect + multi-hop redirect,
IP-literal smuggling forms, IPv4/IPv6.
"""
import math

import pytest

from egress_firewall import (
    DnsCache,
    EgressPolicy,
    PinnedFetchBlocked,
    clamp_dns_ttl,
    fetch_pinned,
)

PUB = "93.184.216.34"       # TEST-NET-1 style public stand-in
PUB2 = "203.0.113.7"        # TEST-NET-3 stand-in (global? no -> use real public)
PUB2 = "8.8.8.8"
PRIV = "10.0.0.5"
LOOP = "127.0.0.1"
META = "169.254.169.254"


def _policy(**kw):
    base = dict(allow_public_internet=True)
    base.update(kw)
    return EgressPolicy(**base)


# ---- TTL clamp boundaries ----

def test_ttl_missing_uses_default():
    p = _policy()
    assert clamp_dns_ttl(None, p) == 60.0


def test_ttl_zero_and_one_round_up_to_min():
    p = _policy()
    assert clamp_dns_ttl(0, p) == p.min_dns_ttl_s
    assert clamp_dns_ttl(1, p) == p.min_dns_ttl_s


def test_ttl_max_and_max_plus_one():
    p = _policy()
    assert clamp_dns_ttl(p.max_dns_ttl_s, p) == p.max_dns_ttl_s
    assert clamp_dns_ttl(p.max_dns_ttl_s + 1, p) == p.max_dns_ttl_s


def test_ttl_huge_clamped():
    assert clamp_dns_ttl(10 ** 12, _policy()) == 300.0


def test_ttl_negative_clamped_to_min():
    p = _policy()
    assert clamp_dns_ttl(-30, p) == p.min_dns_ttl_s
    assert clamp_dns_ttl(float("-inf"), p) == p.min_dns_ttl_s


def test_ttl_nan_and_garbage_clamped_to_min():
    p = _policy()
    assert clamp_dns_ttl(float("nan"), p) == p.min_dns_ttl_s
    assert clamp_dns_ttl("soon", p) == p.min_dns_ttl_s


# ---- DnsCache behavior ----

def test_cache_serves_within_ttl_then_refreshes():
    p = _policy()
    cache = DnsCache(p)
    calls = {"n": 0}

    def resolve(h):
        calls["n"] += 1
        return [PUB]

    assert cache.lookup("a.example", resolve, ttl_s=100, now=0.0) == [PUB]
    assert cache.lookup("a.example", resolve, ttl_s=100, now=50.0) == [PUB]
    assert calls["n"] == 1
    # past clamped TTL (100 < 300 so expiry at 100): re-resolves
    assert cache.lookup("a.example", resolve, ttl_s=100, now=101.0) == [PUB]
    assert calls["n"] == 2


def test_cache_never_outlives_max_ttl():
    p = _policy()
    cache = DnsCache(p)
    calls = {"n": 0}

    def resolve(h):
        calls["n"] += 1
        return [PUB]

    cache.lookup("b.example", resolve, ttl_s=3600, now=0.0)
    assert cache.lookup("b.example", resolve, ttl_s=3600, now=299.0) == [PUB]
    assert calls["n"] == 1
    assert cache.lookup("b.example", resolve, ttl_s=3600, now=301.0) == [PUB]
    assert calls["n"] == 2, "hostile 3600s claim must not outlive max 300s"


def test_negative_cache_and_expiry():
    p = _policy()
    cache = DnsCache(p)
    assert cache.lookup("nx.example", lambda h: [], now=0.0) == []
    calls = {"n": 0}

    def resolve(h):
        calls["n"] += 1
        return [PUB]

    assert cache.lookup("nx.example", resolve, now=10.0) == []
    assert calls["n"] == 0, "negative entry must suppress re-resolution"
    assert cache.lookup("nx.example", resolve, now=31.0) == [PUB]
    assert calls["n"] == 1


def test_invalidate_and_clear():
    p = _policy()
    cache = DnsCache(p)
    cache.lookup("c.example", lambda h: [PUB], now=0.0)
    cache.invalidate("c.example")
    assert cache.lookup("c.example", lambda h: [PUB2], now=1.0) == [PUB2]
    cache.clear()
    assert cache._positive == {} and cache._negative == {}


# ---- fetch_pinned ----

def _ok_transport(seen):
    def transport(host, port, ip, use_tls, path, method, data,
                  headers, timeout):
        seen.append({"host": host, "ip": ip, "use_tls": use_tls,
                     "path": path})
        return 200, b"hello", {}
    return transport


def test_pinned_fetch_connects_to_authorized_ip_not_name():
    seen = []
    out = fetch_pinned("http://svc.example/x", _policy(),
                       resolve=lambda h: [PUB],
                       connect=_ok_transport(seen))
    assert out["status"] == 200 and out["body"] == b"hello"
    assert seen[0]["ip"] == PUB and seen[0]["host"] == "svc.example"


def test_pinned_fetch_blocks_private_loopback_metadata():
    for bad in (PRIV, LOOP, META):
        with pytest.raises(PinnedFetchBlocked):
            fetch_pinned("http://svc.example/x", _policy(),
                         resolve=lambda h, _b=bad: [_b],
                         connect=_ok_transport([]))


def test_rebind_private_after_authorize_blocked():
    """DNS clean at check, hostile at connect -> must abort (TOCTOU)."""
    answers = [[PUB], [PRIV]]

    def resolve(h):
        return answers.pop(0) if answers else [PRIV]

    with pytest.raises(PinnedFetchBlocked):
        fetch_pinned("http://svc.example/x", _policy(), resolve=resolve,
                     connect=_ok_transport([]))


def test_rebind_loopback_and_metadata_blocked():
    for hostile in ("127.0.0.1", "169.254.169.254", "192.168.1.1",
                    "10.9.9.9", "172.16.0.9", "::1", "fe80::1", "fc00::1"):
        answers = [[PUB], [hostile]]

        def resolve(h, _a=answers):
            return _a.pop(0) if _a else [hostile]

        with pytest.raises(PinnedFetchBlocked):
            fetch_pinned("http://svc.example/x", _policy(), resolve=resolve,
                         connect=_ok_transport([]))


def test_rebind_same_public_ip_allowed():
    seen = []
    out = fetch_pinned("http://svc.example/x", _policy(),
                       resolve=lambda h: [PUB],
                       connect=_ok_transport(seen))
    assert out["status"] == 200


def test_redirect_to_private_blocked():
    def transport(host, port, ip, use_tls, path, method, data,
                  headers, timeout):
        if path == "/start":
            return 302, b"", {"location": "http://evil.example/loot"}
        return 200, b"never", {}

    def resolve(h):
        return [PUB] if h == "svc.example" else [PRIV]

    with pytest.raises(PinnedFetchBlocked):
        fetch_pinned("http://svc.example/start", _policy(), resolve=resolve,
                     connect=transport)


def test_multi_hop_redirect_ceiling():
    hops = {"n": 0}

    def transport(host, port, ip, use_tls, path, method, data,
                  headers, timeout):
        hops["n"] += 1
        return 302, b"", {"location": f"http://svc.example/h{hops['n']}"}

    with pytest.raises(PinnedFetchBlocked):
        fetch_pinned("http://svc.example/h0", _policy(),
                     resolve=lambda h: [PUB], connect=transport,
                     max_redirects=3)
    assert hops["n"] == 4  # initial + 3 redirect follows, then ceiling


def test_ip_literal_forms_blocked_when_private():
    # decimal / hex / octal / short forms of 127.0.0.1 and 10.0.0.1
    for raw in ("2130706433", "0x7f000001", "0177.0.0.1", "127.1",
                "167772161", "0xa000001", "10.1", "012.0.0.1"):
        with pytest.raises(PinnedFetchBlocked):
            fetch_pinned(f"http://{raw}/", _policy(),
                         resolve=lambda h: (_ for _ in ()).throw(
                             AssertionError("DNS must not be consulted")),
                         connect=_ok_transport([]))


def test_public_ip_literal_allowed_and_pinned():
    seen = []
    out = fetch_pinned(f"http://{PUB}/doc", _policy(),
                       resolve=lambda h: (_ for _ in ()).throw(
                           AssertionError("DNS must not be consulted")),
                       connect=_ok_transport(seen))
    assert out["status"] == 200
    assert seen[0]["ip"] == PUB


def test_userinfo_and_port_policy_still_enforced():
    with pytest.raises(PinnedFetchBlocked):
        fetch_pinned("http://user:pass@svc.example/", _policy(),
                     resolve=lambda h: [PUB],
                     connect=_ok_transport([]))
    with pytest.raises(PinnedFetchBlocked):
        fetch_pinned("http://svc.example:22/", _policy(),
                     resolve=lambda h: [PUB],
                     connect=_ok_transport([]))


def test_https_downgrade_refused():
    def transport(host, port, ip, use_tls, path, method, data,
                  headers, timeout):
        assert use_tls is True
        return 302, b"", {"location": "http://svc.example/plain"}

    with pytest.raises(PinnedFetchBlocked):
        fetch_pinned("https://svc.example/start", _policy(),
                     resolve=lambda h: [PUB], connect=transport)


def test_https_to_https_redirect_allowed():
    calls = []

    def transport(host, port, ip, use_tls, path, method, data,
                  headers, timeout):
        calls.append((use_tls, path))
        if path == "/start":
            return 302, b"", {"location": "https://svc.example/next"}
        return 200, b"done", {}

    out = fetch_pinned("https://svc.example/start", _policy(),
                       resolve=lambda h: [PUB], connect=transport)
    assert out["status"] == 200 and out["redirects"] == 1
    assert all(tls for tls, _ in calls)
