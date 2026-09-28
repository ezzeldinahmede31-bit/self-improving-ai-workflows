"""Short-lived secrets vault: issue scoped leases, redeem, revoke, audit.

Agents never hold long-lived credentials. They receive a lease token
valid for one scope and a short TTL; the raw token is shown ONCE at
issuance while only its sha256 is stored (same pattern as the rotation
gate). Redemption checks scope, expiry, use budget, and revocation.
Every security-relevant event appends to an in-memory log with an
optional JSONL file sink for durable audit.

Backed only by stdlib. No network. Thread-unsafe by design (wrap with
a lock when shared across threads).
"""

from __future__ import annotations

import fnmatch
import hashlib
import json
import os
import secrets
import time
from dataclasses import dataclass, field


@dataclass
class Lease:
    lease_id: str
    token_sha256: str
    scope: tuple[str, ...]
    uses_left: int | None
    created_at: float
    expires_at: float
    revoked: bool = False
    redeemed_total: int = 0


class Vault:
    """Issue/redeem/revoke scoped short-lived credential leases."""

    def __init__(self, *, log_path: str | None = None):
        self._leases: dict[str, Lease] = {}
        self._events: list[dict] = []
        self._log_path = log_path

    def _log(self, kind: str, lease_id: str, detail: str = "") -> None:
        entry = {"ts": time.time(), "kind": kind, "lease": lease_id,
                 "detail": detail}
        self._events.append(entry)
        if self._log_path:
            try:
                with open(self._log_path, "a", encoding="utf-8") as fh:
                    fh.write(json.dumps(entry, sort_keys=True) + "\n")
            except OSError:
                pass

    def issue(self, *, scope: list[str], ttl_s: int = 300,
              max_uses: int | None = 1) -> tuple[str, str]:
        """Create a lease. Returns (lease_id, raw_token shown once)."""
        if not scope:
            raise ValueError("scope must be non-empty")
        if ttl_s <= 0:
            raise ValueError("ttl_s must be positive")
        if max_uses is not None and max_uses <= 0:
            raise ValueError("max_uses must be positive or None")
        raw = "vlt_" + secrets.token_urlsafe(32)
        lid = "ls_" + secrets.token_hex(8)
        now = time.time()
        self._leases[lid] = Lease(
            lease_id=lid,
            token_sha256=hashlib.sha256(raw.encode()).hexdigest(),
            scope=tuple(scope), uses_left=max_uses,
            created_at=now, expires_at=now + ttl_s)
        self._log("issue", lid, f"scope={len(scope)} ttl={ttl_s}")
        return lid, raw

    def _find(self, raw_token: str) -> Lease | None:
        digest = hashlib.sha256(raw_token.encode()).hexdigest()
        for lease in self._leases.values():
            if lease.token_sha256 == digest:
                return lease
        return None

    def redeem(self, raw_token: str, *, operation: str) -> tuple[bool, str]:
        """Spend one use of a lease for an operation inside its scope."""
        lease = self._find(raw_token)
        if lease is None:
            return False, "unknown token"
        if lease.revoked:
            self._log("redeem_denied", lease.lease_id, "revoked")
            return False, "lease revoked"
        if time.time() > lease.expires_at:
            self._log("redeem_denied", lease.lease_id, "expired")
            return False, "lease expired"
        if lease.uses_left is not None and lease.uses_left <= 0:
            self._log("redeem_denied", lease.lease_id, "use budget spent")
            return False, "use budget spent"
        if not any(fnmatch.fnmatchcase(str(operation), pat)
                   for pat in lease.scope):
            self._log("redeem_denied", lease.lease_id, "outside scope")
            return False, "operation outside lease scope"
        if lease.uses_left is not None:
            lease.uses_left -= 1
        lease.redeemed_total += 1
        self._log("redeem", lease.lease_id, str(operation))
        return True, "ok"

    def revoke(self, lease_id: str) -> bool:
        """Revoke a lease immediately. True when the id existed."""
        lease = self._leases.get(str(lease_id))
        if lease is None:
            return False
        lease.revoked = True
        self._log("revoke", lease.lease_id, "")
        return True

    def rotate(self, lease_id: str, *, ttl_s: int = 300) -> tuple[str, str] | None:
        """Revoke a live lease and issue a same-scope replacement."""
        lease = self._leases.get(str(lease_id))
        if lease is None or lease.revoked:
            return None
        self.revoke(lease_id)
        return self.issue(scope=list(lease.scope), ttl_s=ttl_s,
                          max_uses=lease.uses_left)

    def sweep_expired(self) -> int:
        """Drop expired leases from memory. Returns the tally removed."""
        now = time.time()
        dead = [lid for lid, ls in self._leases.items()
                if now > ls.expires_at]
        for lid in dead:
            del self._leases[lid]
            self._log("sweep", lid, "expired")
        return len(dead)

    def events(self) -> list[dict]:
        """Read-only copy of the in-memory access log."""
        return list(self._events)

    def active(self) -> list[str]:
        """Ids of live (unrevoked, unexpired) leases."""
        now = time.time()
        return [lid for lid, ls in self._leases.items()
                if not ls.revoked and now <= ls.expires_at]
