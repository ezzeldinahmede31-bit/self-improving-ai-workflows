"""Egress firewall: runtime destination validation for outbound calls.

Static SSRF scans catch hardcoded bad URLs; this module guards the
RUNTIME path — every destination is validated immediately before use:
literal IPs, DNS-resolved IPs (all answers checked, not just the
first), metadata endpoints, userinfo smuggling, scheme/port policy,
and an optional domain allow-list. Default posture is deny-by-default
for non-public space; public internet requires explicit opt-in.

DNS-rebinding note: check_url() validates at check time. Callers that fetch
must use fetch_pinned(), which pins the connection to the AUTHORIZED IP
(no second DNS lookup), re-resolves at connect time and re-validates on
any change, and re-validates every redirect hop — the TOCTOU window is
closed at the connection boundary, not just at check time. DNS answers
flow through DnsCache with TTL clamped into
[min_dns_ttl_s, max_dns_ttl_s]: no entry outlives policy.

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
    # --- Explicit loopback allowance (named hosts only) ---
    # Loopback is DENIED by default everywhere. An operator may name
    # specific local endpoints (e.g. their own n8n on localhost) that are
    # allowed DESPITE resolving to loopback. This is an explicit,
    # auditable opt-in — never a blanket "allow 127/8". Matching is exact
    # (after lowercasing + trailing-dot strip), never suffix.
    allow_loopback_hosts: tuple[str, ...] = ()
    # --- DNS cache policy (GAP-02 closure) ---
    # No cached DNS entry may live longer than max_dns_ttl_s, no matter what
    # TTL a resolver claims. Entries claiming less than min_dns_ttl_s are
    # rounded UP (prevents 0-TTL rebinding races); claims above the max are
    # clamped DOWN. Negative (NXDOMAIN/error) answers get their own short
    # budget so a transient failure cannot be weaponized into a long block
    # (or a long hole).
    max_dns_ttl_s: float = 300.0
    min_dns_ttl_s: float = 5.0
    negative_cache_ttl_s: float = 30.0
    # Entries learned from the OS resolver (getaddrinfo exposes no TTL)
    # are stored with default_dns_ttl_s, itself clamped into [min, max].
    default_dns_ttl_s: float = 60.0


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


def clamp_dns_ttl(ttl_s: float | None, policy: EgressPolicy) -> float:
    """Clamp a claimed DNS TTL into the policy window [min, max].

    Rules (all deterministic, all tested at the boundaries):
      - missing/None TTL  -> default_dns_ttl_s (clamped)
      - negative / NaN     -> min_dns_ttl_s (never cache "forever ago",
                             never treat as immortal)
      - below min         -> min_dns_ttl_s (kills 0/1-second rebind races)
      - above max         -> max_dns_ttl_s (a hostile resolver cannot pin
                             a stale answer past policy)
    """
    lo, hi = policy.min_dns_ttl_s, policy.max_dns_ttl_s
    if hi < 0:
        hi = 0.0
    if lo < 0:
        lo = 0.0
    if hi < lo:
        hi = lo
    if ttl_s is None:
        ttl_s = policy.default_dns_ttl_s
    try:
        ttl = float(ttl_s)
    except (TypeError, ValueError):
        return lo
    if ttl != ttl:  # NaN
        return lo
    if ttl < lo:
        return lo
    if ttl > hi:
        return hi
    return ttl


class DnsCache:
    """Tiny TTL-bounded DNS cache with separate negative entries.

    Positive entries: host -> (ips, expires_at). Negative entries
    (resolution returned nothing): host -> expires_at, living at most
    negative_cache_ttl_s. NOTHING lives past its clamped TTL — there is
    no stale-serve path: an expired entry is re-resolved, never reused.
    `now` is injectable for deterministic tests.
    """

    def __init__(self, policy: EgressPolicy | None = None):
        self.policy = policy or EgressPolicy()
        self._positive: dict[str, tuple[tuple[str, ...], float]] = {}
        self._negative: dict[str, float] = {}

    def lookup(self, host: str, resolve, ttl_s: float | None = None,
               now: float | None = None) -> list[str]:
        """Return cached IPs or resolve + cache with a clamped TTL.

        `resolve` is the underlying resolver callable (host -> list[str]).
        `ttl_s` is the TTL the resolver claims for this answer (None when
        the resolver exposes none, e.g. getaddrinfo).
        """
        import time as _time
        t = now if now is not None else _time.monotonic()
        key = host.lower().rstrip(".")
        hit = self._positive.get(key)
        if hit is not None:
            ips, expires = hit
            if t < expires:
                return list(ips)
            del self._positive[key]
        neg_expires = self._negative.get(key)
        if neg_expires is not None:
            if t < neg_expires:
                return []
            del self._negative[key]
        try:
            ips = [str(c) for c in (resolve(key) or [])]
        except OSError:
            ips = []
        if ips:
            clamped = clamp_dns_ttl(ttl_s, self.policy)
            self._positive[key] = (tuple(ips), t + clamped)
            return list(ips)
        neg_ttl = self.policy.negative_cache_ttl_s
        if neg_ttl < 0:
            neg_ttl = 0.0
        if neg_ttl > self.policy.max_dns_ttl_s:
            neg_ttl = self.policy.max_dns_ttl_s
        self._negative[key] = t + neg_ttl
        return []

    def invalidate(self, host: str) -> None:
        key = host.lower().rstrip(".")
        self._positive.pop(key, None)
        self._negative.pop(key, None)

    def clear(self) -> None:
        self._positive.clear()
        self._negative.clear()


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


def _check_host_core(host: str, policy: EgressPolicy,
                       resolve=None, dns_cache: DnsCache | None = None,
                       resolve_ttl_s: float | None = None,
                       check_domain: bool = True) -> EgressVerdict:
    """Shared host-resolution + IP-classification core.

    Used by check_url() (after scheme/userinfo/port screening) and by
    check_host() (for non-URL destinations such as raw TCP probes). Reason
    strings are stable: tests assert on them.
    """
    host = (host or "").lower().rstrip(".")
    if not host:
        return EgressVerdict(False, "empty host", ())
    if host in METADATA_HOSTS or host in policy.extra_blocked_hosts:
        return EgressVerdict(False, f"blocked host: {host}", ())
    allowed_loop = {str(h).lower().rstrip(".")
                    for h in policy.allow_loopback_hosts}
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
            base_resolve = resolve or (lambda h: _default_resolve(h, policy.dns_timeout_s))
            if dns_cache is not None:
                candidates = dns_cache.lookup(host, base_resolve,
                                              ttl_s=resolve_ttl_s)
            else:
                try:
                    candidates = [str(c) for c in (base_resolve(host) or [])]
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
            # Named loopback allowance: an operator-pinned local endpoint
            # (their own n8n on localhost) survives ONLY when the requested
            # host itself is on the explicit allow list. Anything else —
            # including suffix lookalikes — stays denied.
            if not (ip.is_loopback and host in allowed_loop):
                return EgressVerdict(False, f"{hit}: {cand}",
                                     tuple(candidates))
        resolved.append(cand)
    if check_domain and policy.allowed_domains and not _domain_allowed(host, policy.allowed_domains):
        return EgressVerdict(False, f"domain outside allow-list: {host}",
                             tuple(resolved))
    if not policy.allowed_domains and not policy.allow_public_internet:
        if all(ipaddress.ip_address(c).is_global for c in resolved):
            return EgressVerdict(False, "public internet not opted in",
                                 tuple(resolved))
    return EgressVerdict(True, "ok", tuple(resolved))


def check_host(host: str, port: int | None = None,
               policy: EgressPolicy | None = None, resolve=None,
               dns_cache: DnsCache | None = None) -> EgressVerdict:
    """Validate a non-URL destination (raw TCP probe, Vault addr host, ...).

    Same DNS + IP-classification core as check_url(); port (when given)
    is screened against policy.allowed_ports. No scheme/userinfo layer
    applies — callers pass the bare hostname or literal.
    """
    policy = policy or EgressPolicy()
    host = (host or "").lower().rstrip(".")
    if port is not None and port not in policy.allowed_ports:
        return EgressVerdict(False, f"port not allowed: {port}", ())
    return _check_host_core(host, policy, resolve=resolve, dns_cache=dns_cache)


def check_url(url: str, policy: EgressPolicy | None = None,
               resolve=None, dns_cache: DnsCache | None = None,
               resolve_ttl_s: float | None = None) -> EgressVerdict:
    """Validate one outbound URL. Returns (allowed, reason, resolved_ips).

    When `dns_cache` is supplied, DNS answers flow through it (TTL clamped
    to policy); otherwise resolution is direct. `resolve_ttl_s` carries the
    TTL the resolver claims for this answer (tests / TTL-aware resolvers).
    URL-layer screening (scheme/userinfo/port) runs first; host resolution
    shares the _check_host_core path with check_host().
    """
    policy = policy or EgressPolicy()
    try:
        parts = urlsplit(url)
    except ValueError:
        return EgressVerdict(False, "unparseable URL", ())
    if parts.scheme.lower() not in policy.allowed_schemes:
        return EgressVerdict(False, f"scheme not allowed: {parts.scheme}", ())
    host = (parts.hostname or "").lower()
    if "@" in (parts.netloc or "") and parts.username:
        return EgressVerdict(False, "userinfo in URL (credential smuggle)", ())
    port = parts.port
    if port is not None and port not in policy.allowed_ports:
        return EgressVerdict(False, f"port not allowed: {port}", ())
    return _check_host_core(host, policy, resolve=resolve,
                            dns_cache=dns_cache,
                            resolve_ttl_s=resolve_ttl_s)


# ---------------------------------------------------------------------------
# Connection-boundary enforcement (GAP-03 closure: DNS rebinding / TOCTOU)
#
# check_url() authorizes a destination, but DNS can change between the check
# and the connect. fetch_pinned() closes that window: it resolves + checks,
# then connects to the AUTHORIZED IP literally (no second DNS lookup), and
# re-resolves at connect time — if the answer changed, the new answer must
# pass check_url again or the fetch aborts. Redirects are followed manually
# (never by a client that would skip validation), each hop re-validated,
# with a hop ceiling. Numeric-IP smuggling (decimal/hex/octal/short forms)
# is canonicalized by _normalize_numeric_ip before any resolution, so those
# forms can never dodge the check.
# ---------------------------------------------------------------------------

class PinnedFetchBlocked(RuntimeError):
    """Raised when a pinned fetch is denied at any boundary."""


def _split_url(url: str):
    parts = urlsplit(url)
    host = (parts.hostname or "").lower()
    port = parts.port or (443 if parts.scheme.lower() == "https" else 80)
    path = parts.path or "/"
    if parts.query:
        path += "?" + parts.query
    return parts, host, port, path


def fetch_pinned(url: str, policy: EgressPolicy | None = None, *,
                 method: str = "GET", data: bytes | None = None,
                 headers: dict | None = None,
                 timeout_s: float = 10.0, max_redirects: int = 3,
                 resolve=None, dns_cache: DnsCache | None = None,
                 connect=None) -> dict:
    """Fetch one URL with connection-boundary pinning (stdlib only).

    Returns {"status", "body", "url" (final), "redirects"}.
    Raises PinnedFetchBlocked on any denied boundary (initial check,
    connect-time re-resolution mismatch, redirect hop, port/scheme).
    `connect` is an injectable transport (host, port, ip, use_tls, path,
    method, data, headers, timeout) -> (status, body, resp_headers) used
    by deterministic tests; the default transport connects to the pinned
    IP literally with SNI/Host set to the original hostname.
    """
    import http.client as _httpc
    import ssl as _ssl

    policy = policy or EgressPolicy()
    current_url = url
    redirects = 0
    headers = dict(headers or {})
    _, _initial_host, _, _ = _split_url(url)
    _initial_tls = urlsplit(url).scheme.lower() == "https"

    def _default_connect(host, port, ip, use_tls, path, method,
                         data, headers, timeout):
        if use_tls:
            ctx = _ssl.create_default_context()

            class _PinnedHTTPS(_httpc.HTTPSConnection):
                def connect(self):  # noqa: D102 - connect to IP, SNI=host
                    sock = socket.create_connection((ip, port),
                                                    timeout=timeout)
                    self.sock = ctx.wrap_socket(sock,
                                                server_hostname=host)
            conn = _PinnedHTTPS(host, port, timeout=timeout)
        else:
            conn = _httpc.HTTPConnection(ip, port, timeout=timeout)
        try:
            send_headers = dict(headers)
            # When connecting to a literal IP for a named host, the Host
            # header must carry the ORIGINAL name (virtual hosting).
            if not use_tls:
                send_headers.setdefault("Host", host)
            conn.request(method, path, body=data, headers=send_headers)
            resp = conn.getresponse()
            body = resp.read()
            resp_headers = {k.lower(): v
                            for k, v in resp.getheaders()}
            return resp.status, body, resp_headers
        finally:
            try:
                conn.close()
            except OSError:
                pass

    transport = connect or _default_connect

    while True:
        verdict = check_url(current_url, policy, resolve=resolve,
                            dns_cache=dns_cache)
        if not verdict.allowed:
            raise PinnedFetchBlocked(
                f"boundary check denied {current_url}: {verdict.reason}")
        parts, host, port, path = _split_url(current_url)
        use_tls = parts.scheme.lower() == "https"
        authorized = set(verdict.resolved_ips)

        # Re-resolve at connect time: the destination must not have moved
        # past authorization. A changed answer is re-checked, not trusted.
        # IP literals / numeric forms skip re-resolution entirely: the
        # literal IS the destination, there is nothing to rebind.
        numeric_host = _normalize_numeric_ip(host)
        try:
            _literal = ipaddress.ip_address(numeric_host or host)
            is_literal = True
        except ValueError:
            is_literal = False
        if verdict.resolved_ips and not is_literal:
            base_resolve = resolve or (
                lambda h: _default_resolve(h, policy.dns_timeout_s))
            try:
                fresh = {str(c) for c in (base_resolve(host) or [])}
            except OSError:
                fresh = set()
            numeric = _normalize_numeric_ip(host)
            if numeric is not None:
                fresh = {numeric}
            else:
                try:
                    ipaddress.ip_address(host)
                    fresh = {host}
                except ValueError:
                    pass
            if fresh and not fresh <= authorized:
                recheck = check_url(current_url, policy, resolve=resolve,
                                    dns_cache=None)
                if not recheck.allowed:
                    raise PinnedFetchBlocked(
                        "destination changed after authorization: "
                        f"{current_url}: {recheck.reason}")
                authorized = set(recheck.resolved_ips)
            target_ip = sorted(authorized)[0]
        else:
            # IP literal / numeric form: connect to the canonical address.
            numeric = _normalize_numeric_ip(host)
            try:
                ipaddress.ip_address(numeric or host)
            except ValueError:
                raise PinnedFetchBlocked(
                    f"no authorized address for {current_url}")
            target_ip = numeric or host

        status, body, resp_headers = transport(
            host, port, target_ip, use_tls, path, method, data,
            headers, timeout_s)
        if status in (301, 302, 303, 307, 308) and redirects < max_redirects:
            location = (resp_headers.get("location") or "").strip()
            if not location:
                return {"status": status, "body": body,
                        "url": current_url, "redirects": redirects}
            from urllib.parse import urljoin as _urljoin
            current_url = _urljoin(current_url, location)
            # No silent https -> http downgrade inside a pinned fetch: an
            # attacker-controlled redirect must not strip transport security.
            if _initial_tls and urlsplit(current_url).scheme.lower() != "https":
                raise PinnedFetchBlocked(
                    f"refusing https->http downgrade to {current_url}")
            redirects += 1
            if method not in ("GET", "HEAD") and status in (301, 302, 303):
                method, data = "GET", None
            continue
        if status in (301, 302, 303, 307, 308) and redirects >= max_redirects:
            raise PinnedFetchBlocked(
                f"redirect ceiling exceeded ({max_redirects}) at {current_url}")
        return {"status": status, "body": body,
                "url": current_url, "redirects": redirects}
