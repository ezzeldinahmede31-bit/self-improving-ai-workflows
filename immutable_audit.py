"""Immutable audit log: append-only hash-chained tamper-evident events.

Each event stores id, timestamp, kind, actor, subject, detail, the hash
of the previous event, and its own hash over the canonical encoding of
all fields. Optional HMAC signatures (secret at construction) bind each
event to the platform key. `verify()` replays the chain and reports the
first break; there is deliberately NO update/delete API — correction
happens by appending a superseding event.

Storage is a dedicated SQLite file (default audit_chain.db) so the
existing audit.db schema is never migrated by this subsystem.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import sqlite3
import time

_GENESIS_PREV = "0" * 64


def _canonical(ts: float, kind: str, actor: str, subject: str,
               detail: str, prev: str) -> bytes:
    return json.dumps(
        {"ts": ts, "kind": kind, "actor": actor, "subject": subject,
         "detail": detail, "prev": prev},
        sort_keys=True, separators=(",", ":")).encode("utf-8")


class AuditChain:
    """Append-only event chain with verification."""

    def __init__(self, path: str = "audit_chain.db",
                 secret: bytes | None = None):
        if secret is not None and (not isinstance(secret, bytes)
                                   or len(secret) < 16):
            raise ValueError("secret must be bytes of 16+ bytes")
        self._path = path
        self._secret = secret
        conn = sqlite3.connect(path)
        try:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS events ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, ts REAL NOT NULL,"
                " kind TEXT NOT NULL, actor TEXT NOT NULL,"
                " subject TEXT NOT NULL, detail TEXT NOT NULL,"
                " prev_hash TEXT NOT NULL, event_hash TEXT NOT NULL,"
                " sig TEXT NOT NULL DEFAULT '')")
            conn.commit()
        finally:
            conn.close()

    def _tip(self, conn: sqlite3.Connection) -> str:
        row = conn.execute(
            "SELECT event_hash FROM events ORDER BY id DESC LIMIT 1"
        ).fetchone()
        return row[0] if row else _GENESIS_PREV

    def append(self, *, kind: str, actor: str, subject: str,
               detail: str = "") -> dict:
        """Append one event. Returns {id, event_hash}."""
        ts = time.time()
        conn = sqlite3.connect(self._path)
        try:
            prev = self._tip(conn)
            digest = hashlib.sha256(
                _canonical(ts, str(kind), str(actor), str(subject),
                           str(detail), prev)).hexdigest()
            sig = hmac.new(self._secret, digest.encode(),
                           hashlib.sha256).hexdigest() if self._secret else ""
            cur = conn.execute(
                "INSERT INTO events (ts, kind, actor, subject, detail,"
                " prev_hash, event_hash, sig) VALUES (?,?,?,?,?,?,?,?)",
                (ts, str(kind), str(actor), str(subject), str(detail),
                 prev, digest, sig))
            conn.commit()
            return {"id": cur.lastrowid, "event_hash": digest}
        finally:
            conn.close()

    def verify(self) -> dict:
        """Replay the chain. Returns {ok, checked, broken_at}."""
        conn = sqlite3.connect(self._path)
        try:
            rows = conn.execute(
                "SELECT id, ts, kind, actor, subject, detail,"
                " prev_hash, event_hash, sig FROM events ORDER BY id"
            ).fetchall()
        finally:
            conn.close()
        prev = _GENESIS_PREV
        for rid, ts, kind, actor, subject, detail, ph, eh, sig in rows:
            if ph != prev:
                return {"ok": False, "checked": rid - 1, "broken_at": rid}
            want = hashlib.sha256(
                _canonical(ts, kind, actor, subject, detail, ph)).hexdigest()
            if not hmac.compare_digest(want, eh):
                return {"ok": False, "checked": rid - 1, "broken_at": rid}
            if self._secret:
                wsig = hmac.new(self._secret, eh.encode(),
                                hashlib.sha256).hexdigest()
                if not hmac.compare_digest(wsig, sig):
                    return {"ok": False, "checked": rid - 1,
                            "broken_at": rid}
            prev = eh
        return {"ok": True, "checked": len(rows), "broken_at": None}

    def tail(self, limit: int = 50) -> list[dict]:
        """Newest events first (read-only view for dashboards)."""
        conn = sqlite3.connect(self._path)
        try:
            rows = conn.execute(
                "SELECT id, ts, kind, actor, subject, detail, event_hash"
                " FROM events ORDER BY id DESC LIMIT ?", (int(limit),)
            ).fetchall()
        finally:
            conn.close()
        return [{"id": r[0], "ts": r[1], "kind": r[2], "actor": r[3],
                 "subject": r[4], "detail": r[5], "hash": r[6]}
                for r in rows]
