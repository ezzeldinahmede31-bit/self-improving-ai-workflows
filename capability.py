"""Capability tokens: scoped, expiring, revocable permissions.

Replaces all-or-nothing API access with least-privilege grants. A token
carries an explicit action allow-list (fnmatch globs), a resource scope,
an expiry timestamp, and a unique id. Verification is local and offline
(HMAC-SHA256 over a canonical payload); revocation is a server-side id
set. Tokens never embed the signing secret.

Security properties:
  - Only the token hash (sha256) is stored server-side; the raw token is
    shown once at issuance (same pattern as the key-rotation gate).
  - Expiry enforced with skew-tolerant comparison (60s leeway on one
    shared clock here).
  - A child token can only NARROW its parent (subset of actions, tighter
    resource scope, shorter TTL) — privilege can never widen by descent.
"""

from __future__ import annotations

import base64
import fnmatch
import hashlib
import hmac
import json
import secrets
import time

_SKEW_S = 60

# GAP-02 closure (capability side): no token may outlive MAX_TTL_S, no
# matter what a caller requests. issue() fails closed (raises) above the
# cap instead of silently minting a long-lived grant; attenuate() can only
# narrow (its TTL is additionally bounded by the parent's expiry).
MAX_TTL_S = 86400  # 24h; production callers use 600-900s task tokens


def _b64e(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _b64d(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


class CapabilityError(ValueError):
    """Raised when a token is malformed or fails verification."""


class CapabilityIssuer:
    """Issues and verifies capability tokens (one secret per issuer)."""

    def __init__(self, secret: bytes):
        if not isinstance(secret, bytes) or len(secret) < 16:
            raise ValueError("secret must be bytes of 16+ bytes")
        self._secret = secret
        self._revoked: set[str] = set()
        self._hashes: dict[str, dict] = {}

    def _sign(self, payload: bytes) -> str:
        return _b64e(hmac.new(self._secret, payload, hashlib.sha256).digest())

    def issue(self, *, actions: list[str], resource: str = "*",
              ttl_s: int = 3600, meta: dict | None = None) -> str:
        """Mint a token. `actions` is a non-empty allow-list of globs."""
        acts = [str(a) for a in actions]
        if not acts:
            raise ValueError("actions allow-list must be non-empty")
        try:
            ttl = int(ttl_s)  # type: ignore[arg-type]
        except (TypeError, ValueError, OverflowError):
            raise ValueError(f"ttl_s must be an integer number of seconds, "
                             f"got {ttl_s!r}")
        if isinstance(ttl_s, float) and (ttl_s != ttl_s or ttl_s in
                                         (float("inf"), float("-inf"))):
            raise ValueError(f"ttl_s must be finite, got {ttl_s!r}")
        if ttl <= 0:
            raise ValueError("ttl_s must be positive")
        if ttl > MAX_TTL_S:
            raise ValueError(
                f"ttl_s={ttl} exceeds maximum {MAX_TTL_S}s: mint "
                "short-lived tokens and re-issue instead of long grants")
        now = int(time.time())
        body = {"v": 1, "id": secrets.token_hex(8), "act": acts,
                "res": str(resource), "iat": now, "exp": now + ttl,
                "meta": dict(meta or {})}
        raw = json.dumps(body, sort_keys=True,
                         separators=(",", ":")).encode("utf-8")
        token = _b64e(raw) + "." + self._sign(raw)
        self._hashes[body["id"]] = {
            "sha256": hashlib.sha256(token.encode()).hexdigest(),
            "revoked": False, "exp": body["exp"],
        }
        return token

    def _decode(self, token: str) -> dict:
        try:
            part, sig = token.split(".")
            raw = _b64d(part)
        except (ValueError, Exception):
            raise CapabilityError("malformed token envelope")
        if not hmac.compare_digest(self._sign(raw), sig):
            raise CapabilityError("bad signature")
        try:
            body = json.loads(raw.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            raise CapabilityError("bad payload encoding")
        if not isinstance(body, dict) or body.get("v") != 1:
            raise CapabilityError("unsupported token version")
        return body

    def verify(self, token: str, *, action: str,
               resource: str = "") -> tuple[bool, str]:
        """Check a token against one proposed (action, resource) pair."""
        try:
            body = self._decode(token)
        except CapabilityError as exc:
            return False, str(exc)
        tid = str(body.get("id", ""))
        if tid in self._revoked:
            return False, "token revoked"
        if int(body.get("exp", 0)) < int(time.time()) - _SKEW_S:
            return False, "token expired"
        if not any(fnmatch.fnmatchcase(str(action), pat)
                   for pat in body.get("act", [])):
            return False, "action outside token scope"
        if not fnmatch.fnmatchcase(str(resource), str(body.get("res", "*"))):
            return False, "resource outside token scope"
        return True, "ok"

    def attenuate(self, token: str, *, actions: list[str] | None = None,
                   resource: str | None = None,
                   ttl_s: int | None = None) -> str:
        """Mint a narrowed child of a valid token (never wider)."""
        body = self._decode(token)  # raises on forgery/tampering
        tid = str(body.get("id", ""))
        if tid in self._revoked:
            raise CapabilityError("parent token revoked")
        if int(body.get("exp", 0)) < int(time.time()) - _SKEW_S:
            raise CapabilityError("parent token expired")
        parent_acts = set(body.get("act", []))
        child_acts = set(actions) if actions is not None else parent_acts
        if not child_acts.issubset(parent_acts) and not all(
                any(fnmatch.fnmatchcase(a, p) for p in parent_acts)
                for a in child_acts):
            raise CapabilityError("child scope exceeds parent scope")
        child_res = resource if resource is not None else body.get("res", "*")
        parent_res = str(body.get("res", "*"))
        if child_res != parent_res and parent_res != "*":
            if any(c in str(child_res) for c in "*?["):
                raise CapabilityError("child resource exceeds parent scope")
            if not fnmatch.fnmatchcase(str(child_res), parent_res):
                raise CapabilityError("child resource exceeds parent scope")
        parent_exp = int(body.get("exp", 0))
        child_ttl = ttl_s if ttl_s is not None else max(
            1, parent_exp - int(time.time()))
        child_ttl = min(child_ttl, max(1, parent_exp - int(time.time())))
        return self.issue(actions=sorted(child_acts), resource=child_res,
                          ttl_s=child_ttl,
                          meta={"parent": body.get("id")})

    def revoke(self, token_id: str) -> bool:
        """Revoke by token id. Returns True when the id was known."""
        self._revoked.add(str(token_id))
        known = str(token_id) in self._hashes
        if known:
            self._hashes[str(token_id)]["revoked"] = True
        return known
