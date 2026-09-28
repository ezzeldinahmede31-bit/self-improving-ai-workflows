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


def _parse_numeric_part(part: str) -> int | None:
    """Parse one inet_aton-style numeric part (decimal/octal/hex).

    Returns None when the part is not purely numeric (i.e. a DNS label).
    Browsers, curl and glibc accept these forms, so the firewall must too:
      '0x7f' -> 127, '0177' -> 127, '127' -> 127.
    """
    if not part:
        return None
    try:
        if len(part) > 2 and part[:2].lower() == "0x":
            return int(part[2:], 16)
        if len(part) > 1 and part[0] == "0" and part.isdigit():
            if any(c in "89" for c in part):
                return None  # invalid octal: not a numeric IP part
            return int(part, 8)
        if part.isdigit():
            return int(part, 10)
    except ValueError:
        return None
    return None


def _normalize_numeric_ip(host: str) -> str | None:
    """Canonicalize inet_aton-style numeric hosts to dotted decimal.

    Covers what `ipaddress.ip_address` REFUSES but real resolvers accept:
      - bare 32-bit decimal/hex: '2130706433' / '0x7f000001' -> 127.0.0.1
      - short dotted forms: '127.1' -> 127.0.0.1, '10.1' -> 10.0.0.1
      - per-part hex/octal: '0x7f.0x0.0x0.0x1', '0177.0.0.1'
    Returns the canonical dotted quad, or None when the host is not a
    numeric-IP form (normal DNS name -> None, resolved via DNS path).
    """
    h = host.lower().rstrip(".")
    if not h or any(c not in "0123456789abcdefx." for c in h):
        return None
    if "." not in h:
        # bare integer: decimal or 0x-hex 32-bit value
        try:
            n = int(h[2:], 16) if h.startswith("0x") else int(h, 10)
        except ValueError:
            return None
        if 0 <= n <= 0xFFFFFFFF:
            return ".".join(str((n >> s) & 0xFF)
                            for s in (24, 16, 8, 0))
        return None
    parts = h.split(".")
    if not 1 <= len(parts) <= 4:
        return None
    nums = [_parse_numeric_part(p) for p in parts]
    if any(n is None or n < 0 for n in nums):
        return None
    if len(nums) == 4:
        if any(n > 255 for n in nums):
            return None
        quads = nums
    else:
        # inet_aton short forms: leading parts are single bytes, the last
        # part fills the remaining bytes (up to 3).
        head, last = nums[:-1], nums[-1]
        if any(n > 255 for n in head):
            return None
        remaining = 4 - len(head)
        max_last = 256 ** remaining - 1
        if last > max_last:
            return None
        tail = [(last >> (8 * i)) & 0xFF
                for i in range(remaining - 1, -1, -1)]
        quads = head + tail
    try:
        return str(ipaddress.ip_address(".".join(str(q) for q in quads)))
    except ValueError:
        return None


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
    numeric = _normalize_numeric_ip(host)
    if numeric is not None:
        # Numeric-IP form (decimal/hex/octal/short): resolve LOCALLY to the
        # canonical address. Never send these to DNS — a resolver that
        # answers them differently (or at all) must not change the verdict.
        candidates = [numeric]
    else:
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
