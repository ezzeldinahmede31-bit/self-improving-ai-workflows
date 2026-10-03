"""Health probes: credentials, dependencies, synthetic end-to-end.

Three pre-execution safety nets, all caller-wired and stdlib-only:
  - CredentialHealth: dated secrets (expires_at epoch) report days of
    headroom; renew-before-failure alerts fire under the warning window.
    Undated secrets report unknown (never assumed healthy).
  - DependencyHealth: named TCP/connect probes with timeouts; a failing
    dependency blocks its dependents (fail-closed start).
  - SyntheticProbes: scripted fake-booking-style runs (act -> verify ->
    cleanup); a probe that cannot clean up after itself fails loudly so
    fake traffic never pollutes production.

Only stdlib is used. Probes never mutate real state by themselves.
"""

from __future__ import annotations

import socket
import time

DAY_S = 86400.0


class CredentialHealth:
    """Expiry headroom for dated secrets."""

    def __init__(self, *, warn_days: float = 7.0):
        self._warn = float(warn_days)
        self._creds: dict[str, dict] = {}

    def track(self, name: str, expires_at: float | None) -> None:
        """Register a credential (None expiry = undated)."""
        self._creds[str(name)] = {"expires_at": expires_at}

    def check(self, name: str, now: float | None = None) -> dict:
        """ok / renew-soon / expired / unknown for one credential."""
        spec = self._creds.get(str(name))
        if spec is None:
            return {"credential": str(name), "state": "unknown",
                    "reason": "untracked"}
        exp = spec["expires_at"]
        if exp is None:
            return {"credential": str(name), "state": "unknown",
                    "reason": "no expiry date recorded"}
        days = ((float(exp) - (now if now is not None else time.time()))
                / DAY_S)
        if days < 0:
            return {"credential": str(name), "state": "expired",
                    "days_left": round(days, 2)}
        if days < self._warn:
            return {"credential": str(name), "state": "renew-soon",
                    "days_left": round(days, 2)}
        return {"credential": str(name), "state": "ok",
                "days_left": round(days, 2)}


class DependencyHealth:
    """Named TCP/connect probes with timeouts; dependents gate on results.

    Pass egress_policy to pin probes behind the firewall: the registered
    host is validated with check_host() (same DNS + IP-classification core
    as URLs) before any socket opens, so a misconfigured/poisoned endpoint
    name cannot turn a health check into an SSRF probe. Without a policy
    (default) behavior is unchanged — operator-registered names only.
    """

    def __init__(self, *, timeout_s: float = 3.0, egress_policy=None):
        self._timeout = float(timeout_s)
        self._egress_policy = egress_policy
        self._deps: dict[str, dict] = {}

    def add(self, name: str, host: str, port: int) -> None:
        """Register a dependency endpoint."""
        self._deps[str(name)] = {"host": str(host), "port": int(port)}

    def probe(self, name: str) -> dict:
        """One TCP connect probe (no protocol chatter)."""
        spec = self._deps.get(str(name))
        if spec is None:
            return {"dependency": str(name), "up": False,
                    "reason": "unregistered"}
        if self._egress_policy is not None:
            from egress_firewall import check_host as _check_host
            verdict = _check_host(spec["host"], spec["port"],
                                  self._egress_policy)
            if not verdict.allowed:
                return {"dependency": str(name), "up": False,
                        "reason": f"egress blocked: {verdict.reason}"}
        try:
            sock = socket.create_connection(
                (spec["host"], spec["port"]), timeout=self._timeout)
            sock.close()
        except OSError as exc:
            return {"dependency": str(name), "up": False,
                    "reason": str(exc)}
        return {"dependency": str(name), "up": True}

    def gate(self, names: list[str]) -> dict:
        """ok only when every named dependency probes up."""
        downs = [n for n in names if not self.probe(n)["up"]]
        return {"ok": not downs, "down": downs}


class SyntheticProbes:
    """Fake-traffic end-to-end probes with mandatory cleanup."""

    def __init__(self):
        self._probes: dict[str, dict] = {}
        self.runs: list[dict] = []

    def add(self, name: str, act, verify, cleanup) -> None:
        """Register act/verify/cleanup callables for one probe."""
        for fn in (act, verify, cleanup):
            if not callable(fn):
                raise TypeError("probe phases must be callable")
        self._probes[str(name)] = {"act": act, "verify": verify,
                                   "cleanup": cleanup}

    def run(self, name: str) -> dict:
        """Act -> verify -> cleanup(always). Uncleaned runs fail."""
        spec = self._probes.get(str(name))
        if spec is None:
            return {"probe": str(name), "healthy": False,
                    "reason": "unregistered"}
        cleaned, note, produced = False, "", None
        try:
            produced = spec["act"]()
            ok, note = spec["verify"](produced)
            healthy = bool(ok)
        except Exception as exc:  # noqa: BLE001 - record, still clean up
            healthy, note = False, f"probe raised: {exc}"
        finally:
            try:
                spec["cleanup"](produced)
                cleaned = True
            except Exception as exc:  # noqa: BLE001 - loud failure
                cleaned, note = False, f"cleanup failed: {exc}"
        out = {"probe": str(name),
               "healthy": bool(healthy and cleaned), "note": str(note),
               "cleaned": cleaned}
        self.runs.append(out)
        return out
