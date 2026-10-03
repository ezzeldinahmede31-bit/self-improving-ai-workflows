"""Local-first Egress layer for n8n/Docker automation.

Everything outside the machine (SaaS, external DBs, Meta/Telegram) is a remote
resource. This module is the single choke-point for touching them:

1. Digital Twin routing: in test mode, requests to a real external host are
   re-pointed at a LOCAL mock (Prism/WireMock or the bundled mock_server.py) so
   no real API quota is burned and no production DB is polluted.
2. Egress telemetry: every call logs host, status, latency, retries into a
   local SQLite table so slow/unhealthy remote servers get flagged.
3. Rate-limit resilience: 429 / 503 are retried with exponential backoff that
   honours the server's `Retry-After` header.
"""

import json
import sqlite3
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional

TELEMETRY_DB_PATH = Path(__file__).parent / "remote_telemetry.db"
_DB_LOCK = threading.Lock()

# Remote hosts that require human approval before real traffic. The Digital
# Twin mock list is user-supplied; this is a safety net for the most dangerous
# targets.
SENSITIVE_REMOTE_HOSTS = {
    'supabase.co', 'stripe.com', 'api.openai.com', 'graph.facebook.com',
    'graph.instagram.com', 'api.telegram.org', 'api.hubspot.com',
    '*.supabase.co', '*.okta.com', 'login.microsoftonline.com',
}


class EgressBlockedError(Exception):
    """Raised when egress to a sensitive host is attempted with no mock."""


@dataclass
class TelemetryEntry:
    service: str
    url: str
    status: int
    latency_ms: float
    retries: int = 0
    went_to_mock: bool = False
    timestamp: str = ""


def init_telemetry_db() -> None:
    with _DB_LOCK:
        conn = sqlite3.connect(TELEMETRY_DB_PATH)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS remote_telemetry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service TEXT NOT NULL,
                url TEXT NOT NULL,
                status INTEGER NOT NULL,
                latency_ms REAL NOT NULL,
                retries INTEGER DEFAULT 0,
                went_to_mock INTEGER DEFAULT 0,
                timestamp TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()


def record_telemetry(entry: TelemetryEntry) -> None:
    with _DB_LOCK:
        conn = sqlite3.connect(TELEMETRY_DB_PATH)
        conn.execute("""
            INSERT INTO remote_telemetry (
                service, url, status, latency_ms, retries, went_to_mock, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            entry.service, entry.url, entry.status, entry.latency_ms,
            entry.retries, 1 if entry.went_to_mock else 0, entry.timestamp,
        ))
        conn.commit()
        conn.close()


def health_summary(limit: int = 500) -> list[dict]:
    """Per-service health: avg latency, error count, request count."""
    with _DB_LOCK:
        conn = sqlite3.connect(TELEMETRY_DB_PATH)
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT service,
                   COUNT(*) AS calls,
                   ROUND(AVG(latency_ms), 1) AS avg_ms,
                   ROUND(MAX(latency_ms), 1) AS max_ms,
                   SUM(CASE WHEN status >= 400 THEN 1 ELSE 0 END) AS errors
            FROM remote_telemetry
            GROUP BY service
            ORDER BY avg_ms DESC
        """).fetchall()
        conn.close()
    return [dict(r) for r in rows]


def _target_host_is_blocked_literal(host: str) -> str | None:
    """Fail-closed literal-IP check for the connection target.

    Mock routing intentionally produces loopback targets (127.0.0.1) from
    public original URLs — that path is allowed only when the original URL
    was mock-routed (went_to_mock). A DIRECT literal private/loopback/
    link-local target with no mock routing is refused here even when no
    egress_policy is configured (legacy mode), so legacy clients cannot be
    used as an SSRF primitive.     Numeric-IP evasions (hex/octal/short/decimal)
    are canonicalized via egress_firewall before classification.

    DNS names return None here: without an egress_policy there is no
    resolver hook, so DNS-resolved private targets are NOT blocked in
    legacy mode. Legacy (egress_policy=None) clients are therefore NOT
    an SSRF security boundary against DNS-based targets — production
    deployments MUST set egress_policy (orchestrator wires it from
    enforcement.egress). This function only closes the literal-IP path,
    which needs no resolver.
    """
    import ipaddress
    h = (host or "").lower().rstrip(".")
    try:
        from egress_firewall import _normalize_numeric_ip
        canon = _normalize_numeric_ip(h)
    except Exception:
        canon = None
    candidate = canon or h
    try:
        ip = ipaddress.ip_address(candidate)
    except ValueError:
        return None  # DNS name: handled by egress_policy DNS path when set
    if ip.is_loopback:
        return "loopback address"
    if getattr(ip, "is_link_local", False):
        return "link-local address (metadata scope)"
    if getattr(ip, "is_multicast", False):
        return "multicast address"
    if getattr(ip, "is_reserved", False):
        return "reserved address"
    if getattr(ip, "is_private", False):
        return "private-network address"
    if not getattr(ip, "is_global", True):
        return "non-global address"
    return None


class MockRouter:
    """Maps a real external host to a local mock base URL (Digital Twin)."""

    def __init__(self, mappings: Optional[dict[str, str]] = None,
                 strict: bool = True):
        self.mappings = mappings or {}   # {"api.example.com": "http://127.0.0.1:9000"}
        self.strict = strict

    def is_mocked(self, url: str) -> bool:
        host = urllib.parse.urlparse(url).netloc
        return any(host == h or host.endswith('.' + h) for h in self.mappings)

    def resolve(self, url: str) -> str:
        """Return the mock URL if mapped; otherwise the real URL."""
        parsed = urllib.parse.urlparse(url)
        host = parsed.netloc
        for real_host, mock_base in self.mappings.items():
            if host == real_host or host.endswith('.' + real_host):
                mock_parsed = urllib.parse.urlparse(mock_base)
                path = parsed.path or '/'
                return urllib.parse.urlunparse((
                    mock_parsed.scheme, mock_parsed.netloc, path,
                    parsed.params, parsed.query, parsed.fragment,
                ))
        return url

    def assert_safe(self, url: str) -> None:
        """Block real traffic to sensitive hosts that have no mock configured.

        A sensitive host is matched if the request host equals it OR is a
        subdomain of it (api.stripe.com counts as stripe.com). Any exact
        match in SENSITIVE_REMOTE_HOSTS or *-prefixed entry covers subdomains.
        """
        host = urllib.parse.urlparse(url).netloc.lower().strip()
        # is this host sensitive?
        sensitive_match = None
        for sensitive in SENSITIVE_REMOTE_HOSTS:
            s = sensitive.lower().lstrip('*.')
            if host == s or host.endswith('.' + s):
                sensitive_match = s
                break
        if sensitive_match is None:
            return  # not sensitive; allow
        if self.is_mocked(url):
            return  # has a local Digital-Twin mock; allow test traffic
        if self.strict:
            raise EgressBlockedError(
                f"Egress to sensitive host {host} blocked: no local mock "
                f"configured for it (Digital Twin required before real traffic)"
            )
        # non-strict: warn but proceed (explicit opt-in for trusted envs)
        print(f"[WARN] egress to sensitive host {host} with no mock "
              f"(strict=False)", file=sys.stderr)


class RemoteAPIClient:
    """Resilient HTTP client that goes through MockRouter + telemetry + backoff."""

    def __init__(
        self,
        router: Optional[MockRouter] = None,
        max_retries: int = 3,
        base_backoff_seconds: float = 0.2,
        max_backoff_seconds: float = 8.0,
        sleep: Callable[[float], None] = time.sleep,
        egress_policy=None,
        egress_resolve: Optional[Callable[[str], list]] = None,
    ):
        self.router = router or MockRouter()
        self.max_retries = max_retries
        self.base_backoff_seconds = base_backoff_seconds
        self.max_backoff_seconds = max_backoff_seconds
        self.sleep = sleep
        # Optional runtime SSRF firewall (egress_firewall.EgressPolicy).
        # None = legacy behavior (MockRouter.assert_safe only). When set,
        # EVERY request target is validated and blocked destinations raise
        # EgressBlockedError before any socket is opened.
        self.egress_policy = egress_policy
        self.egress_resolve = egress_resolve

    def _backoff_wait(self, retry_after: Optional[int], attempt: int) -> float:
        if retry_after is not None and retry_after > 0:
            return float(retry_after)
        exp = min(self.base_backoff_seconds * (2 ** attempt), self.max_backoff_seconds)
        return exp

    def request(
        self,
        method: str,
        url: str,
        headers: Optional[dict] = None,
        body: Any = None,
        timeout: float = 10.0,
    ) -> dict:
        """Perform an HTTP call with Digital-Twin routing, telemetry, backoff.

        Returns {"status": int, "body": parsed, "headers": dict, "mock": bool}.
        Raises EgressBlockedError for un-mocked sensitive hosts.
        """
        headers = headers or {}
        self.router.assert_safe(url)
        if self.egress_policy is not None:
            from egress_firewall import check_url as _check_url
            verdict = _check_url(url, self.egress_policy,
                                 resolve=self.egress_resolve)
            if not verdict.allowed:
                raise EgressBlockedError(
                    f"Egress firewall blocked {url}: {verdict.reason}")
        went_to_mock = self.router.is_mocked(url)
        target = self.router.resolve(url)
        if not went_to_mock:
            # Connection-target check: the socket opens `target`, not `url`.
            # A direct literal non-global target without mock routing is
            # refused even in legacy mode (no egress_policy).
            target_host = (urllib.parse.urlparse(target).hostname or "")
            hit = _target_host_is_blocked_literal(target_host)
            if hit is not None:
                raise EgressBlockedError(
                    f"Egress to non-global target blocked: {hit}")
            # When an egress policy is set, the TARGET gets the same DNS +
            # IP-classification screening as the URL: a router mapping (or
            # any host swap between url and target) must not smuggle a
            # private/loopback/metadata destination past the url check.
            if self.egress_policy is not None:
                from egress_firewall import check_url as _check_target
                tverdict = _check_target(target, self.egress_policy,
                                         resolve=self.egress_resolve)
                if not tverdict.allowed:
                    raise EgressBlockedError(
                        f"Egress firewall blocked connection target "
                        f"{target}: {tverdict.reason}")
        else:
            # Mock plane: the target is operator-configured loopback. Pin
            # it to loopback literally — a mapping that resolves anywhere
            # else is refused instead of followed.
            target_host = (urllib.parse.urlparse(target).hostname or "")
            try:
                import ipaddress as _ip
                _tip = _ip.ip_address(target_host)
                if not _tip.is_loopback:
                    raise EgressBlockedError(
                        "mock target must be loopback: "
                        f"{target_host}")
            except ValueError:
                raise EgressBlockedError(
                    f"mock target must be a loopback literal, not a DNS "
                    f"name: {target_host}")
        service = urllib.parse.urlparse(url).netloc
        retries = 0

        for attempt in range(self.max_retries + 1):
            start = time.perf_counter()
            try:
                req = urllib.request.Request(
                    target, method=method,
                    headers=headers,
                    data=None if body is None else
                    (json.dumps(body).encode() if not isinstance(body, bytes) else body),
                )
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    latency_ms = (time.perf_counter() - start) * 1000
                    raw = resp.read()
                    entry = TelemetryEntry(
                        service=service, url=url, status=resp.status,
                        latency_ms=round(latency_ms, 1), retries=retries,
                        went_to_mock=went_to_mock,
                        timestamp=datetime.now(timezone.utc).isoformat(),
                    )
                    record_telemetry(entry)
                    return {
                        "status": resp.status,
                        "body": self._parse_body(raw),
                        "headers": dict(resp.headers),
                        "mock": went_to_mock,
                    }
            except urllib.error.HTTPError as e:
                latency_ms = (time.perf_counter() - start) * 1000
                retry_after = int(e.headers.get('Retry-After', 0)) if e.headers else 0
                status_code = e.code
                if status_code in (429, 503) and attempt < self.max_retries:
                    retries += 1
                    wait = self._backoff_wait(retry_after, attempt)
                    record_telemetry(TelemetryEntry(
                        service=service, url=url, status=status_code,
                        latency_ms=round(latency_ms, 1), retries=retries,
                        went_to_mock=went_to_mock,
                        timestamp=datetime.now(timezone.utc).isoformat(),
                    ))
                    self.sleep(wait)
                    continue
                # Non-retryable or exhausted
                self._record_failure(service, url, status_code, latency_ms,
                                     retries, went_to_mock)
                return {
                    "status": status_code,
                    "body": {"error": e.reason},
                    "headers": dict(e.headers) if e.headers else {},
                    "mock": went_to_mock,
                    "retries": retries,
                }
            except urllib.error.URLError as e:
                latency_ms = (time.perf_counter() - start) * 1000
                if attempt < self.max_retries:
                    retries += 1
                    self.sleep(self._backoff_wait(None, attempt))
                    continue
                self._record_failure(service, url, 0, latency_ms,
                                     retries, went_to_mock)
                return {
                    "status": 0,
                    "body": {"error": str(e.reason)},
                    "headers": {},
                    "mock": went_to_mock,
                    "retries": retries,
                }

        return {"status": -1, "body": {"error": "unreachable"}, "retries": retries,
                "mock": went_to_mock}

    def _record_failure(self, service, url, status_code, latency_ms, retries,
                        went_to_mock):
        record_telemetry(TelemetryEntry(
            service=service, url=url, status=status_code,
            latency_ms=round(latency_ms, 1), retries=retries,
            went_to_mock=went_to_mock,
            timestamp=datetime.now(timezone.utc).isoformat(),
        ))

    @staticmethod
    def _parse_body(raw: bytes) -> Any:
        text = raw.decode('utf-8', errors='replace')
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return text


init_telemetry_db()


# ============================================================
# Self-test
# ============================================================
if __name__ == "__main__":
    router = MockRouter({"api.example.com": "http://127.0.0.1:9000"}, strict=False)
    client = RemoteAPIClient(router=router, max_retries=1, base_backoff_seconds=0.05)
    print("mapped URL:", router.resolve("https://api.example.com/v1/users"))
    print("health:", health_summary())