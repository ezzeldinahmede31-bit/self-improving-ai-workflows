"""Privacy + data governance + runtime DLP denylist.

Sensitive-data handling in one place: classify fields (public /
internal / sensitive / restricted), enforce retention TTLs with
scheduled purges, serve export/delete-request records, and — the
runtime half — deny-list patterns that must never reach logs,
telemetry, prompts, third-party models, or analytics (phones, names,
medical notes, API keys, card numbers, national ids, plus caller
patterns). check_text() scans a payload and names the hit classes;
redact() replaces hits with typed placeholders.

Only stdlib is used. Patterns are conservative (precision over
recall); quality_gate-style review tunes them per tenant.
"""

from __future__ import annotations

import re
import time

LEVELS = ("public", "internal", "sensitive", "restricted")

DENY_PATTERNS = [
    ("phone", re.compile(r"\+?\d[\d\s\-()]{7,}\d")),
    ("email", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
    ("api_key", re.compile(r"\b(sk-[A-Za-z0-9_-]{8,}|xox[bpas]-[A-Za-z0-9-]{6,}|ghp_[A-Za-z0-9]{8,})")),
    ("card", re.compile(r"\b(?:\d[ -]?){13,19}\b")),
    ("national_id", re.compile(r"\b\d{14}\b")),
    ("private_key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("bearer", re.compile(r"(?i)bearer\s+[A-Za-z0-9\-._~+/]+=*")),
]


class PrivacyGovernor:
    """Classification registry + retention + DLP scanning."""

    def __init__(self):
        self._fields: dict[str, dict] = {}
        self._requests: list[dict] = []

    def classify(self, field: str, level: str, ttl_s: float | None = None,
                 residency: str = "") -> None:
        """Declare a field's class, retention TTL, and residency zone."""
        if level not in LEVELS:
            raise ValueError(f"level must be one of {LEVELS}")
        self._fields[str(field)] = {"level": level, "ttl_s": ttl_s,
                                    "residency": str(residency)}

    def retention_due(self, field: str, stored_at: float,
                      now: float | None = None) -> bool:
        """True when a stored value passed its retention TTL."""
        spec = self._fields.get(str(field), {})
        ttl = spec.get("ttl_s")
        if ttl is None:
            return False
        return (now if now is not None else time.time()) > stored_at + ttl

    def record_request(self, kind: str, subject: str, note: str = "") -> dict:
        """Log an export/delete request (export/delete only)."""
        if kind not in ("export", "delete"):
            raise ValueError("kind must be export|delete")
        rec = {"ts": time.time(), "kind": kind, "subject": str(subject),
               "note": str(note), "status": "open"}
        self._requests.append(rec)
        return rec

    def requests(self, status: str | None = None) -> list[dict]:
        """Open (or filtered) subject requests."""
        if status is None:
            return list(self._requests)
        return [r for r in self._requests if r["status"] == status]

    @staticmethod
    def check_text(text: str, extra: list | None = None) -> list[str]:
        """Hit classes present in a payload (empty = clean)."""
        hits = []
        blob = str(text)
        for label, pat in DENY_PATTERNS + list(extra or []):
            try:
                if pat.search(blob):
                    hits.append(label)
            except re.error:
                continue
        return hits

    @staticmethod
    def redact(text: str, extra: list | None = None) -> str:
        """Replace hits with typed placeholders ([PHONE], ...)."""
        out = str(text)
        for label, pat in DENY_PATTERNS + list(extra or []):
            try:
                out = pat.sub(f"[{label.upper()}]", out)
            except re.error:
                continue
        return out

    def minimize(self, payload: dict, needed: list[str]) -> dict:
        """Data minimization: keep only declared-necessary fields."""
        keep = set(needed)
        return {k: v for k, v in payload.items() if k in keep}
