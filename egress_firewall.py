"""Egress firewall: runtime destination validation for outbound calls.

Static SSRF scans catch hardcoded bad URLs; this module guards the
RUNTIME path — every destination is validated immediately before use:
literal IPs, DNS-resolved IPs (all answers checked, not just the
first), metadata endpoints, userinfo smuggling, scheme/port policy,
and an optional domain allow-list. Default posture is deny-by-default
for non-public space; public internet requires explicit opt-in.

DNS-rebinding note (honest limit): a name that resolves clean now can
resolve hostile later. This guard validates at check time; callers that
hold connections open across re-resolution must re-check per connect
(the `resolve` hook makes that cheap to wire in).

Only stdlib is used. The default resolver uses socket.getaddrinfo with
a short timeout; tests inject a fake resolver (no network in tests).
"""

from __future__ import annotations

import ipaddress
import socket
from dataclasses import dataclass, field
from urllib.parse import urlsplit

METADATA_HOSTS = {
    "169.254.169.254",           # cloud metadata (link-local v4)
    "fd00:ec2::254",             # cloud metadata (link-local v6)
    "metadata.google.internal",
    "metadata.goog",
    "instance-data",
    "instance-data-compute",
}

LINK_LOCAL_V6 = ipaddress.ip_network("fe80::/10")
UNIQUE_LOCAL_V6 = ipaddress.ip_network("fc00::/7")


@dataclass
class EgressPolicy:
    allow_public_internet: bool = False
    allowed_domains: tuple[str, ...] = ()   # suffix match, e.g. "example.com"
    allowed_ports: tuple[int, ...] = (80, 443)
    allowed_schemes: tuple[str, ...] = ("http", "https")
    extra_blocked_hosts: tuple[str, ...] = ()
    dns_timeout_s: float = 3.0


@dataclass
class EgressVerdict:
    allowed: bool
    reason: str
    resolved_ips: tuple[str, ...] = ()


def _default_resolve(host: str, timeout_s: float) -> list[str]:
    out: list[str] = []
    try:
        old = socket.getdefaulttimeout()
        socket.setdefaulttimeout(timeout_s)
        try:
            for fam, _, _, _, addr in socket.getaddrinfo(host, None):
                if fam in (socket.AF_INET, socket.AF_INET6):
                    out.append(addr[0])
        finally:
            socket.setdefaulttimeout(old)
    except OSError:
        pass
    return out


def _ip_blocked(ip: ipaddress._BaseAddress) -> str | None:
    if ip.is_loopback:
        return "loopback address"
    if ip.is_link_local or ip in LINK_LOCAL_V6:
        return "link-local address (metadata scope)"
    if ip.is_multicast:
        return "multicast address"
    if ip.is_reserved:
        return "reserved address"
    if ip.is_private or ip in UNIQUE_LOCAL_V6:
        return "private-network address"
    if isinstance(ip, ipaddress.IPv4Address):
        if ip.is_global:
            return None
        return "non-global IPv4 address"
    if ip.is_global:
        return None
    return "non-global IPv6 address"


def _domain_allowed(host: str, allowed: tuple[str, ...]) -> bool:
    host = host.lower().rstrip(".")
    for dom in allowed:
        dom = dom.lower().rstrip(".")
        if host == dom or host.endswith("." + dom):
            return True
    return False


def check_url(url: str, policy: EgressPolicy | None = None,
              resolve=None) -> EgressVerdict:
    """Validate one outbound URL. Returns (allowed, reason, resolved_ips)."""
    policy = policy or EgressPolicy()
    try:
        parts = urlsplit(url)
    except ValueError:
        return EgressVerdict(False, "unparseable URL", ())
    if parts.scheme.lower() not in policy.allowed_schemes:
        return EgressVerdict(False, f"scheme not allowed: {parts.scheme}", ())
    host = (parts.hostname or "").lower()
    if not host:
        return EgressVerdict(False, "empty host", ())
    if "@" in (parts.netloc or "") and parts.username:
        return EgressVerdict(False, "userinfo in URL (credential smuggle)", ())
    if host in METADATA_HOSTS or host in policy.extra_blocked_hosts:
        return EgressVerdict(False, f"blocked host: {host}", ())
    port = parts.port
    if port is not None and port not in policy.allowed_ports:
        return EgressVerdict(False, f"port not allowed: {port}", ())

    candidates: list[str] = []
    try:
        ip = ipaddress.ip_address(host)
        candidates = [host]
    except ValueError:
        resolver = resolve or (lambda h: _default_resolve(h, policy.dns_timeout_s))
        try:
            candidates = [str(c) for c in (resolver(host) or [])]
        except OSError:
            candidates = []
        if not candidates:
            return EgressVerdict(False, f"host does not resolve: {host}", ())
    resolved: list[str] = []
    for cand in candidates:
        try:
            ip = ipaddress.ip_address(cand)
        except ValueError:
            return EgressVerdict(False, f"bad resolved address: {cand}", ())
        hit = _ip_blocked(ip)
        if hit is not None:
            return EgressVerdict(False, f"{hit}: {cand}", tuple(candidates))
        resolved.append(cand)
    if policy.allowed_domains and not _domain_allowed(host, policy.allowed_domains):
        return EgressVerdict(False, f"domain outside allow-list: {host}",
                             tuple(resolved))
    if not policy.allowed_domains and not policy.allow_public_internet:
        if all(ipaddress.ip_address(c).is_global for c in resolved):
            return EgressVerdict(False, "public internet not opted in",
                                 tuple(resolved))
    return EgressVerdict(True, "ok", tuple(resolved))
