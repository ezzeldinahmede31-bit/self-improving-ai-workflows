"""Per-workflow / per-tenant cost ledger.

LiteLLM enforces a GLOBAL budget; this ledger attributes spend to individual
workflows and tenants so multi-user/multi-team deployments can be measured and
capped separately. Records are append-only with a running window; the
`tenant_budget()` view answers "is this tenant over its ceiling?" directly.
"""

from __future__ import annotations

import json
import sqlite3
import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

COST_DB = Path(__file__).parent / "cost_ledger.db"
_LOCK = threading.Lock()


class CostLedger:
    def __init__(self, db_path: str | Path = COST_DB):
        self.db_path = str(db_path)
        self._init_db()

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with _LOCK:
            conn = self._connect()
            conn.execute("""
                CREATE TABLE IF NOT EXISTS spend_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts TEXT NOT NULL,
                    workflow_id TEXT NOT NULL,
                    tenant TEXT NOT NULL DEFAULT 'default',
                    model TEXT NOT NULL,
                    tokens_in INTEGER NOT NULL DEFAULT 0,
                    tokens_out INTEGER NOT NULL DEFAULT 0,
                    cost_usd REAL NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tenant_budgets (
                    tenant TEXT PRIMARY KEY,
                    budget_usd REAL NOT NULL,
                    period TEXT NOT NULL DEFAULT 'monthly'
                )
            """)
            conn.commit()
            conn.close()

    def record(self, workflow_id: str, model: str, tokens_in: int, tokens_out: int,
               cost_usd: float, tenant: str = "default") -> int:
        with _LOCK:
            conn = self._connect()
            cur = conn.execute(
                "INSERT INTO spend_records (ts, workflow_id, tenant, model, "
                "tokens_in, tokens_out, cost_usd) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (datetime.now(timezone.utc).isoformat(), workflow_id, tenant,
                 model, tokens_in, tokens_out, cost_usd))
            conn.commit()
            conn.close()
        return cur.lastrowid

    def set_budget(self, tenant: str, budget_usd: float) -> None:
        with _LOCK:
            conn = self._connect()
            conn.execute(
                "INSERT INTO tenant_budgets (tenant, budget_usd, period) "
                "VALUES (?, ?, 'monthly') "
                "ON CONFLICT(tenant) DO UPDATE SET budget_usd = excluded.budget_usd",
                (tenant, budget_usd))
            conn.commit()
            conn.close()

    def spend_by_workflow(self, tenant: str = "default") -> list[dict]:
        with _LOCK:
            conn = self._connect()
            rows = conn.execute(
                "SELECT workflow_id, SUM(cost_usd) AS total_usd, COUNT(*) AS calls "
                "FROM spend_records WHERE tenant = ? GROUP BY workflow_id "
                "ORDER BY total_usd DESC", (tenant,)).fetchall()
            conn.close()
        return [dict(r) for r in rows]

    def tenant_spend(self, tenant: str = "default") -> float:
        with _LOCK:
            conn = self._connect()
            row = conn.execute(
                "SELECT SUM(cost_usd) AS total FROM spend_records WHERE tenant = ?",
                (tenant,)).fetchone()
            conn.close()
        return round(row["total"] or 0.0, 6)

    def tenant_budget_status(self, tenant: str = "default") -> dict:
        budget_row = None
        with _LOCK:
            conn = self._connect()
            budget_row = conn.execute(
                "SELECT budget_usd FROM tenant_budgets WHERE tenant = ?",
                (tenant,)).fetchone()
            conn.close()
        budget = budget_row["budget_usd"] if budget_row else float("inf")
        spend = self.tenant_spend(tenant)
        pct = (spend / budget * 100) if budget != float("inf") and budget > 0 else 0.0
        return {
            "tenant": tenant, "spend_usd": spend,
            "budget_usd": None if budget == float("inf") else budget,
            "percent_used": round(pct, 2),
            "over_budget": budget != float("inf") and spend > budget,
        }


class LiteLLMFeeder:
    """Drives the ledger from LiteLLM spend data — plot: a cron pulls
    /get/spend/report and calls ledger.record for each (key, workflow) row.
    We model the row adapter here so the integration point is explicit, not
    theoretical."""

    @staticmethod
    def ingest_report_rows(ledger: CostLedger, rows: list[dict]) -> int:
        """rows: [{workflow_id, tenant, model, tokens_in, tokens_out, cost_usd}]"""
        n = 0
        for row in rows:
            ledger.record(
                workflow_id=row["workflow_id"],
                tenant=row.get("tenant", "default"),
                model=row.get("model", "unknown"),
                tokens_in=row.get("tokens_in", 0),
                tokens_out=row.get("tokens_out", 0),
                cost_usd=row.get("cost_usd", 0.0),
            )
            n += 1
        return n


if __name__ == "__main__":
    import tempfile
    ledger = CostLedger(db_path=tempfile.mktemp(suffix="_cost.db"))
    ledger.set_budget("acme", 10.0)
    ledger.record("wf_orders", "deepseek-chat", 1000, 500, 0.00028, tenant="acme")
    ledger.record("wf_orders", "deepseek-chat", 2000, 1000, 0.00056, tenant="acme")
    ledger.record("wf_other", "qwen2.5-coder:7b", 500, 300, 0.0, tenant="acme")
    print("by workflow:", ledger.spend_by_workflow("acme"))
    print("status:", ledger.tenant_budget_status("acme"))