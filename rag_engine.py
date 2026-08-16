"""Real task-scoped RAG — #4.

`quirks_memory` was a start (service -> quirk lookup). This is the real RAG:
  - Corpus: official n8n docs snippets, past SUCCESSFUL workflows that passed
    HITL, and documented common error patterns.
  - Retrieval: hybrid keyword + a tiny embedding-free TF scoring so the weak
    model gets the facts IN CONTEXT instead of needing to "know" them.
  - Isolation: ingestions are tagged (task, approved, source); queryable by
    scope so each task only sees its own knowledge + durable approved examples.
"""

from __future__ import annotations

import json
import re
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

RAG_DB = Path(__file__).parent / "rag_memory.db"
_LOCK = threading.Lock()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class RagMemory:
    def __init__(self, db_path: str | Path = RAG_DB):
        self.db_path = str(db_path)
        self._init_db()

    def _conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with _LOCK:
            conn = self._conn()
            conn.execute("""
                CREATE TABLE IF NOT EXISTS rag_docs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,          -- n8n-docs | approved-workflow | error-pattern
                    scope TEXT DEFAULT 'global',   -- task-scope or 'global'
                    title TEXT,
                    content TEXT NOT NULL,
                    keywords TEXT,
                    approved INTEGER DEFAULT 0,    -- 1 if passed HITL
                    created_at TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_rag_scope ON rag_docs(scope)
            """)
            conn.commit()
            conn.close()

    def ingest(self, source: str, content: str, title: str = "",
               scope: str = "global", keywords: Optional[list[str]] = None,
               approved: bool = False) -> int:
        kw = " ".join(keywords or self._auto_kw(title, content))
        with _LOCK:
            conn = self._conn()
            cur = conn.execute(
                "INSERT INTO rag_docs (source, scope, title, content, keywords, "
                "approved, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (source, scope, title, content, kw, 1 if approved else 0, _now()))
            conn.commit()
            conn.close()
        return cur.lastrowid

    @staticmethod
    def _auto_kw(title: str, content: str) -> list[str]:
        words = re.findall(r"[A-Za-z][A-Za-z0-9_\-]{2,}", f"{title} {content}")
        counts: dict[str, int] = {}
        for w in words:
            counts[w.lower()] = counts.get(w.lower(), 0) + 1
        top = sorted(counts.items(), key=lambda kv: -kv[1])[:8]
        return [w for w, _ in top]

    def query(self, text: str, scope: Optional[str] = None,
              sources: Optional[list[str]] = None, limit: int = 5) -> list[dict]:
        tokens = [t for t in re.findall(r"[A-Za-z0-9_]{3,}", text.lower())]
        clauses = []
        params: list[Any] = []
        if scope:
            clauses.append("scope = ?")
            params.append(scope)
        if sources:
            marks = ",".join("?" for _ in sources)
            clauses.append(f"source IN ({marks})")
            params.extend(sources)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        with _LOCK:
            conn = self._conn()
            rows = conn.execute(
                f"SELECT * FROM rag_docs {where} ORDER BY approved DESC, id DESC LIMIT 60",
                params).fetchall()
            conn.close()

        results = []
        for r in rows:
            doc = dict(r)
            score = 0
            hay = f"{doc['title']} {doc['content']} {doc['keywords']}".lower()
            for t in tokens:
                if t in hay:
                    score += 2 if t in doc["keywords"].lower() else 1
            doc["score"] = score
            results.append(doc)
        # only docs with at least one token match are relevant
        if tokens:
            results = [d for d in results if d["score"] > 0]
        results.sort(key=lambda d: (d["approved"], d["score"]), reverse=True)
        return results[:limit]

    def render_context(self, text: str, scope: Optional[str] = None,
                       limit: int = 5) -> str:
        """Build the exact prompt fragment the weak model should see."""
        docs = self.query(text, scope=scope, limit=limit)
        if not docs:
            return ""
        lines = ["## Context (retrieved for this task only):"]
        for d in docs:
            tag = "[APPROVED]" if d["approved"] else f"[{d['source']}]"
            lines.append(f"- {tag} {d['title']}: {d['content'][:220]}")
        return "\n".join(lines)

    def ingest_approved_workflow(self, workflow: dict, title: str = "",
                                 scope: str = "global") -> int:
        """Store a workflow that passed HITL as a retrievable positive example."""
        return self.ingest(
            source="approved-workflow", content=json.dumps(workflow, default=str),
            title=title or "approved workflow", scope=scope,
            keywords=["workflow", *self._auto_kw(title, json.dumps(workflow)[:800])],
            approved=True)

    def summary(self) -> dict:
        with _LOCK:
            conn = self._conn()
            row = conn.execute(
                "SELECT source, COUNT(*) AS n FROM rag_docs GROUP BY source").fetchall()
            conn.close()
        return {r["source"]: r["n"] for r in row}


def default_rag() -> RagMemory:
    rag = RagMemory()
    # seed with durable, version-agnostic best practices (no fictional URLs)
    if rag.summary().get("n8n-docs", 0) == 0:
        rag.ingest(
            "n8n-docs",
            "Keep a webhook's httpMethod + path unique; a second workflow with the "
            "same path/method will conflict on activation.",
            title="webhook uniqueness", keywords=["webhook", "path", "conflict"])
        rag.ingest(
            "n8n-docs",
            "Prefer HTTP Request with named credential over a hardcoded header; "
            "headers with secrets trigger the security gate.",
            title="credential hygiene", keywords=["credential", "header", "auth"])
        rag.ingest(
            "error-pattern",
            "Missing pinnedData on trigger nodes blocks instant unit-testing; "
            "add pinnedData on the trigger for every hand-built workflow.",
            title="pinnedData", keywords=["pinnedData", "test", "trigger"])
    return rag


if __name__ == "__main__":
    rag = default_rag()
    rag.ingest_approved_workflow(
        {"nodes": [{"name": "Receive Webhook", "type": "webhook"}]},
        title="approved ingest example", scope="orders")
    print(rag.render_context("how to build a webhook with pinnedData", scope="orders"))