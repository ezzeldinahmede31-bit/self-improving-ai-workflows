"""Remote-API Quirks & RAG Memory.

External services have idiosyncratic behaviors (Telegram's 4096-char message
cap, Meta's re-auth windows...). Every quirk discovered and fixed by the local
Verifier is stored here, then looked up at generation time so the same mistake
is never made twice. This is a lightweight SQLite-backed RAG until a real
vector DB (Qdrant in Docker) is wired in.
"""

import json
import re
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

QUIRKS_DB_PATH = Path(__file__).parent / "quirks.db"
_DB_LOCK = threading.Lock()


def init_quirks_db() -> None:
    with _DB_LOCK:
        conn = sqlite3.connect(QUIRKS_DB_PATH)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS service_quirks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service TEXT NOT NULL,
                trigger_term TEXT NOT NULL,
                symptom TEXT NOT NULL,
                fix TEXT NOT NULL,
                source TEXT NOT NULL DEFAULT 'verifier',
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_quirks_service ON service_quirks(service)")
        conn.commit()
        conn.close()


def remember_quirk(service: str, symptom: str, fix: str,
                   trigger_terms: Optional[list[str]] = None,
                   source: str = "verifier") -> int:
    """Store one quirk so it can be recalled at generation time."""
    if not trigger_terms:
        words = re.findall(r"[A-Za-z0-9_]{3,}", symptom)
        trigger_terms = words[:5] or [symptom[:20]]
    with _DB_LOCK:
        conn = sqlite3.connect(QUIRKS_DB_PATH)
        cur = conn.execute("""
            INSERT INTO service_quirks (service, trigger_term, symptom, fix, source)
            VALUES (?, ?, ?, ?, ?)
        """, (service, trigger_terms[0], symptom, fix, source))
        conn.commit()
        qid = cur.lastrowid
        conn.close()
    return qid


def query_quirks(service: str, text: str = "", limit: int = 5) -> list[dict]:
    """Retrieve relevant quirks by service and keyword match (RAG-lite)."""
    text_lower = text.lower()
    with _DB_LOCK:
        conn = sqlite3.connect(QUIRKS_DB_PATH)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM service_quirks WHERE service = ? ORDER BY id DESC LIMIT 20",
            (service,),
        ).fetchall()
        conn.close()
    results = []
    for r in rows:
        score = 1  # service match always counts — recall known quirks
        row = dict(r)
        if text_lower:
            for token in re.findall(r"[A-Za-z0-9_]{3,}", text_lower):
                if token in row["symptom"].lower() or token in row["fix"].lower():
                    score += 1
                if token in row["trigger_term"].lower():
                    score += 2
        row["score"] = score
        results.append(row)
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:limit]


def render_as_prompt(service: str, text: str = "") -> str:
    """Format recalled quirks into a prompt-fragment the generator consumes."""
    qs = query_quirks(service, text)
    if not qs:
        return ""
    lines = ["Known quirks for this remote service (apply these):"]
    for q in qs:
        lines.append(f"- {q['symptom']} -> {q['fix']}")
    return "\n".join(lines)


init_quirks_db()

if __name__ == "__main__":
    remember_quirk("telegram", "messages longer than 4096 chars are rejected",
                   "split message into chunks <= 4096", ["4096", "telegram", "message"])
    remember_quirk("stripe", "idempotency key required for retries",
                   "send Idempotency-Key header on create calls", ["idempotency"])
    print(render_as_prompt("telegram", "need to send a long announcement"))