"""Context Enrichment — implicit-intent → explicit-rule lexicon
(weak-model hardening protocol #4). See .opencode/skills/context-enrichment.

A frontier model "catches" implicit intents because it was trained on deep,
broad data. A small model lacks that depth — but it can be compensated by a
RAG built specifically on THIS domain. Every time a human corrects a
misread intent in HITL, the correction becomes a translation rule:

    implicit_pattern (the user's vague phrasing) -> explicit_rule (the exec)

Example:  "لو المستخدم قال 'خليه آمن' في سياق webhook"
          ->  implicit: "آمن | secure | make it safe" (context: webhook)
             rule: "add auth + rate limit + input validation"

Before execution, the lexicon is queried on the same phrasing/category and the
matching explicit rules are injected into the generator prompt as additional
hard constraints. This extends (does not replace) quirks_memory.
"""

from __future__ import annotations

import json
import re
import sqlite3
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

IMPLICIT_DB = Path(__file__).parent / "implicit_lexicon.db"
_LOCK = threading.Lock()

# Seed lexicon: domain-specific translations, extendable from HITL corrections.
DEFAULT_IMPLICIT_RULES = [
    {"implicit": "آمن | secure | secure it | make it safe | خليه آمن",
     "context": "webhook", "rule":
     "Add auth (token/secret check), rate limiting and input validation on the webhook."},
    {"implicit": "قطع | retry | لا تخسر | don't lose | make it reliable",
     "context": "webhook", "rule":
     "Retry-on-fail with exponential backoff and a dead-letter/queue on failure."},
    {"implicit": "بسرعة | fast | realtime | instant",
     "context": "webhook", "rule":
     "Keep chain synchronous; no polling/queue unless unavoidable."},
    {"implicit": "مجانا | free | no cost | رخيص",
     "context": "model", "rule":
     "Use free/local model tier; do not route to paid frontier for routine steps."},
    {"implicit": "دقيق | accurate | correct | صح",
     "context": "verification", "rule":
     "Artifact must pass SecurityGate + QualityGate before deploy; no short-cuts."},
]


@dataclass
class ExplicitRule:
    implicit: str
    context: str
    rule: str
    source: str = "seed"
    count: int = 1

    def to_dict(self) -> dict:
        return {"implicit": self.implicit, "context": self.context,
                "rule": self.rule, "source": self.source}


class ImplicitIntentLexicon:
    """SQLite-backed translation dictionary. Seeded + grown from HITL
    corrections. Query by task text and context category."""

    def __init__(self, db_path: str | Path = IMPLICIT_DB,
                 seed_enabled: bool = True):
        self.db_path = str(db_path)
        self._init_db()
        if seed_enabled:
            for r in DEFAULT_IMPLICIT_RULES:
                self.add_rule(rule=r["rule"], implicit=r["implicit"],
                              context=r["context"], source="seed")

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with _LOCK:
            conn = self._connect()
            conn.execute("""
                CREATE TABLE IF NOT EXISTS implicit_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    implicit TEXT NOT NULL,
                    context TEXT NOT NULL DEFAULT '',
                    rule TEXT NOT NULL,
                    source TEXT NOT NULL DEFAULT 'hitl',
                    usages INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL DEFAULT (datetime('now'))
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_imp_ctx "
                         "ON implicit_rules(context)")
            conn.commit()
            conn.close()

    # ---------- write : grow from HITL corrections ----------

    def add_rule(self, rule: str, implicit: str, context: str = "",
                 source: str = "hitl") -> int:
        """Add or strengthen a translation rule. Same (implicit, context) just
        bumps usage count (more evidence => higher rank)."""
        with _LOCK:
            conn = self._connect()
            row = conn.execute(
                "SELECT id, usages FROM implicit_rules "
                "WHERE implicit = ? AND rule = ?",
                (implicit.strip(), rule.strip()),
            ).fetchone()
            if row:
                conn.execute(
                    "UPDATE implicit_rules SET usages = usages + 1, "
                    "context = ? WHERE id = ?", (context, row["id"]))
                rid = row["id"]
            else:
                cur = conn.execute(
                    "INSERT INTO implicit_rules (implicit, context, rule, source) "
                    "VALUES (?, ?, ?, ?)",
                    (implicit.strip(), context, rule.strip(), source))
                rid = cur.lastrowid
            conn.commit()
            conn.close()
        return rid

    def record_hitl_correction(self, task_text: str, what_user_meant: str,
                               context: str = "general") -> int:
        """Feed a human's intent correction into the lexicon. This is the HITL
        feedback path (the user wants: every HITL misintent correction stored
        as implicit_pattern -> explicit_rule)."""
        implicit = task_text.strip()[:160]
        return self.add_rule(rule=what_user_meant.strip()[:500],
                             implicit=implicit, context=context, source="hitl")

    # ---------- read : query before generation ----------

    def resolve(self, text: str, context: str = "") -> list[ExplicitRule]:
        """Return matching explicit rules for the task phrasing. Matches if any
        token of the implicit pattern appears in the task text OR if the context
        category matches. Sort by usage (evidence)."""
        tokens = set(re.findall(r"[A-Za-z0-9_أ-ي]{3,}", (text or "").lower()))
        with _LOCK:
            conn = self._connect()
            rows = conn.execute("SELECT * FROM implicit_rules").fetchall()
            conn.close()
        hits: list[ExplicitRule] = []
        for r in rows:
            implicit_low = (r["implicit"] or "").lower()
            pat_tokens = set(re.findall(r"[A-Za-z0-9_أ-ي]{3,}", implicit_low))
            matched = bool(tokens & pat_tokens)
            context_matched = bool(context and context.lower() == (r["context"] or "").lower())
            if matched or context_matched:
                hits.append(ExplicitRule(
                    implicit=r["implicit"], context=r["context"], rule=r["rule"],
                    source=r["source"], count=r["usages"]))
        hits.sort(key=lambda e: e.count, reverse=True)
        return hits

    def render_intent_context(self, text: str, context: str = ""):
        """Prompt fragment for the generator: explicit rules resolved from the
        user's (possibly implicit) phrasing. Empty string when no match."""
        rules = self.resolve(text, context)
        if not rules:
            return ""
        lines = ["## Explicit intent rules for this task (must implement):"]
        for r in rules:
            lines.append(f"- ({r.context or 'any'}) {r.rule}")
        return "\n".join(lines)

    def stats(self) -> dict:
        with _LOCK:
            conn = self._connect()
            n = conn.execute("SELECT COUNT(*) c, SUM(usages) u FROM implicit_rules").fetchone()
            conn.close()
        return {"rules": n["c"], "total_usages": n["u"] or 0}


# Keep a module-level default instance for drop-in use.
_DEFAULT = ImplicitIntentLexicon()


def resolve_implicit(text: str, context: str = "") -> list[ExplicitRule]:
    return _DEFAULT.resolve(text, context)


def render_implicit_context(text: str, context: str = "") -> str:
    return _DEFAULT.render_intent_context(text, context)