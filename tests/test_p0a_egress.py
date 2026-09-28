"""Tests for egress_firewall.py (runtime destination validation)."""

from egress_firewall import EgressPolicy, check_url


def _resolve(host):
    table = {"api.example.com": ["93.184.216.34"],
             "internal.corp": ["10.4.5.6"],
             "bad.example.com": ["10.0.0.9", "93.184.216.34"]}
    return table.get(host, [])


def test_public_needs_opt_in():
    v = check_url("https://api.example.com/v1",
                  EgressPolicy(), resolve=_resolve)
    assert not v.allowed and "opt" in v.reason


def test_public_allowed_with_opt_in_and_allowlist():
    p = EgressPolicy(allow_public_internet=True,
                     allowed_domains=("example.com",))
    v = check_url("https://api.example.com/v1", p, resolve=_resolve)
    assert v.allowed, v.reason


def test_private_ip_blocked_even_if_first_answer_is_public():
    p = EgressPolicy(allow_public_internet=True)
    v = check_url("https://bad.example.com/", p, resolve=_resolve)
    assert not v.allowed and "private" in v.reason


def test_literal_private_ip_blocked():
    v = check_url("http://10.1.2.3/admin",
                  EgressPolicy(allow_public_internet=True))
    assert not v.allowed


def test_loopback_and_metadata_blocked():
    p = EgressPolicy(allow_public_internet=True)
    assert not check_url("http://127.0.0.1/", p).allowed
    assert not check_url("http://169.254.169.254/", p).allowed
    assert not check_url("http://[::1]/", p).allowed


def test_userinfo_smuggling_denied():
    p = EgressPolicy(allow_public_internet=True)
    v = check_url("https://user:pass@api.example.com/", p,
                  resolve=_resolve)
    assert not v.allowed and "userinfo" in v.reason


def test_domain_allowlist_enforced():
    p = EgressPolicy(allow_public_internet=True,
                     allowed_domains=("example.com",))
    v = check_url("https://other.example.org/", p,
                  resolve=lambda h: ["93.184.216.34"])
    assert not v.allowed and "allow-list" in v.reason


def test_bad_scheme_and_port_denied():
    p = EgressPolicy(allow_public_internet=True)
    assert not check_url("ftp://api.example.com/", p,
                         resolve=_resolve).allowed
    assert not check_url("https://api.example.com:22/", p,
                         resolve=_resolve).allowed


def test_unresolvable_denied():
    v = check_url("https://no-such-host.invalid/", EgressPolicy(),
                  resolve=lambda h: [])
    assert not v.allowed


def test_numeric_ip_forms_canonicalized_and_blocked():
    """Golden regression: inet_aton numeric forms must not bypass the wall.

    Root cause (found 2026-09-28 by test_adversarial_full_stack): Python's
    ipaddress module rejects decimal/hex/short IPv4 forms that real
    resolvers (glibc/curl/browsers) accept, so they fell into the DNS path
    and could be ALLOWED while the socket connected to 127.0.0.1/10.x.
    """
    pol = EgressPolicy(allow_public_internet=True)
    for url, why in [
        ("http://2130706433/", "decimal 127.0.0.1"),
        ("http://0x7f000001/", "hex 127.0.0.1"),
        ("http://0x7f.0x0.0x0.0x1/", "dotted hex 127.0.0.1"),
        ("http://127.1/", "short 127.0.0.1"),
        ("http://0177.0.0.1/", "octal 127.0.0.1"),
        ("http://3232235521/", "decimal 192.168.0.1"),
        ("http://10.1/", "short 10.0.0.1"),
    ]:
        v = check_url(url, pol, resolve=_resolve)
        assert not v.allowed, f"BYPASS via {why}: {url}"
