"""Memory governance: provenance, TTL, quarantine, conflict rule.

Wraps plain-dict memory stores (quirks, RAG metadata, scratch) WITHOUT
modifying them: every write carries source/timestamp/confidence/author;
reads serve live entries only (expired TTL filtered, quarantined
sources withheld); conflicting values for one key resolve by source
authority rank, then newest timestamp, then highest confidence — the
loser is archived with its reason instead of silently dropped.

Poisoning rule: sources outside the trusted set land in quarantine and
are never served until a trusted author promotes them. A claimed
admin instruction from an untrusted source stays inert by construction.

Only stdlib is used.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class MemoryRecord:
    key: str
    value: object
    source: str
    author: str
    confidence: float
    created_at: float
    ttl_s: float | None = None
    quarantined: bool = False


class MemoryGovernor:
    """Governance wrapper over an external dict-like store."""

    def __init__(self, *, trusted_sources: tuple[str, ...] = (),
                 authority: dict | None = None,
                 default_ttl_s: float | None = None):
        self._trusted = set(trusted_sources)
        self._authority = dict(authority or {})
        self._default_ttl = default_ttl_s
        self._records: dict[str, list[MemoryRecord]] = {}
        self._archive: list[dict] = []

    def write(self, key: str, value, *, source: str, author: str = "",
              confidence: float = 0.5, ttl_s: float | None = None) -> dict:
        """Store a stamped record (quarantined when source untrusted)."""
        rec = MemoryRecord(
            key=str(key), value=value, source=str(source),
            author=str(author),
            confidence=max(0.0, min(1.0, float(confidence))),
            created_at=time.time(),
            ttl_s=ttl_s if ttl_s is not None else self._default_ttl,
            quarantined=str(source) not in self._trusted)
        self._records.setdefault(rec.key, []).append(rec)
        self._resolve(rec.key)
        return {"key": rec.key, "quarantined": rec.quarantined}

    def _live(self, key: str, now: float) -> list[MemoryRecord]:
        out = []
        for rec in self._records.get(key, []):
            if rec.quarantined:
                continue
            if rec.ttl_s is not None and now > rec.created_at + rec.ttl_s:
                continue
            out.append(rec)
        return out

    def _rank(self, rec: MemoryRecord):
        return (self._authority.get(rec.source, 0), rec.created_at,
                rec.confidence)

    def _resolve(self, key: str) -> None:
        """Keep the top-ranked live record primary; archive the rest."""
        live = self._live(key, time.time())
        if len(live) <= 1:
            return
        live.sort(key=self._rank, reverse=True)
        for loser in live[1:]:
            self._archive.append(
                {"key": key, "value": loser.value, "source": loser.source,
                 "reason": "superseded by higher-ranked record",
                 "ts": time.time()})

    def read(self, key: str):
        """Current primary value, or None when absent/expired/quarantined."""
        live = self._live(str(key), time.time())
        if not live:
            return None
        live.sort(key=self._rank, reverse=True)
        return live[0].value

    def promote(self, key: str, source: str, *, by: str) -> bool:
        """Trusted author releases one quarantined record into service."""
        if by not in self._trusted:
            return False
        changed = False
        for rec in self._records.get(str(key), []):
            if rec.source == source and rec.quarantined:
                rec.quarantined = False
                changed = True
        if changed:
            self._resolve(str(key))
        return changed

    def sweep(self) -> int:
        """Drop expired records. Returns the tally removed."""
        now = time.time()
        removed = 0
        for key in list(self._records):
            keep = [r for r in self._records[key]
                    if r.ttl_s is None or now <= r.created_at + r.ttl_s]
            removed += len(self._records[key]) - len(keep)
            if keep:
                self._records[key] = keep
            else:
                del self._records[key]
        return removed

    def archive(self) -> list[dict]:
        """Superseded records with reasons (read-only copy)."""
        return list(self._archive)

    def quarantine(self) -> list[str]:
        """Keys holding untrusted material (review queue)."""
        return sorted({r.key for rs in self._records.values() for r in rs
                       if r.quarantined})
