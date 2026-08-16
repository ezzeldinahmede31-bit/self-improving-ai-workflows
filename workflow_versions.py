"""Workflow version control — snapshot / diff / rollback.

Catches the "deployed + broke in prod, now what?" failure before it matters:
every deploy writes an immutable snapshot (JSON + sha256) into a ledger table;
diff() tells you exactly what changed between versions; rollback() restores the
previous snapshot and records the reversal. One command, or one call.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any, Optional

VERSIONS_DB = Path(__file__).parent / "versions.db"
_LOCK = threading.Lock()


class WorkflowVersionControl:
    def __init__(self, db_path: str | Path = VERSIONS_DB):
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
                CREATE TABLE IF NOT EXISTS workflow_versions (
                    workflow_id TEXT,
                    version INTEGER NOT NULL,
                    name TEXT,
                    snapshot_json TEXT NOT NULL,
                    sha256 TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT (datetime('now')),
                    kind TEXT NOT NULL DEFAULT 'deploy',   -- deploy | manual | rollback
                    PRIMARY KEY (workflow_id, version)
                )
            """)
            conn.commit()
            conn.close()

    @staticmethod
    def _sha(content: Any) -> str:
        raw = json.dumps(content, default=str, sort_keys=True)
        return hashlib.sha256(raw.encode()).hexdigest()

    def snapshot(self, workflow_id: str, workflow: dict,
                 name: str = "", kind: str = "deploy") -> int:
        """Store a new version; returns its version number."""
        with _LOCK:
            conn = self._connect()
            row = conn.execute(
                "SELECT COALESCE(MAX(version), 0) AS v FROM workflow_versions "
                "WHERE workflow_id = ?", (workflow_id,)
            ).fetchone()
            version = (row["v"] or 0) + 1
            conn.execute(
                "INSERT INTO workflow_versions (workflow_id, version, name, "
                "snapshot_json, sha256, kind) VALUES (?, ?, ?, ?, ?, ?)",
                (workflow_id, version, name,
                 json.dumps(workflow, default=str), self._sha(workflow), kind),
            )
            conn.commit()
            conn.close()
        return version

    def get(self, workflow_id: str, version: Optional[int] = None) -> Optional[dict]:
        with _LOCK:
            conn = self._connect()
            if version:
                row = conn.execute(
                    "SELECT * FROM workflow_versions WHERE workflow_id = ? AND version = ?",
                    (workflow_id, version)).fetchone()
            else:
                row = conn.execute(
                    "SELECT * FROM workflow_versions WHERE workflow_id = ? "
                    "ORDER BY version DESC LIMIT 1", (workflow_id,)).fetchone()
            conn.close()
        if row is None:
            return None
        return dict(row) | {"snapshot": json.loads(row["snapshot_json"])}

    def diff(self, workflow_id: str, a: int, b: int) -> dict:
        va = self.get(workflow_id, a)
        vb = self.get(workflow_id, b)
        if not va or not vb:
            return {"error": "version not found"}
        sa, sb = va["snapshot"], vb["snapshot"]

        # node-level structural diff (name stays the key)
        nodes_a = {n.get("name", ""): n for n in sa.get("nodes", [])}
        nodes_b = {n.get("name", ""): n for n in sb.get("nodes", [])}
        added = [n for n in nodes_b if n not in nodes_a]
        removed = [n for n in nodes_a if n not in nodes_b]
        changed = [n for n in nodes_a if n in nodes_b and nodes_a[n] != nodes_b[n]]

        return {
            "from": a, "to": b, "added_nodes": added, "removed_nodes": removed,
            "changed_nodes": changed,
            "raw_changed": self._sha(sa) != self._sha(sb),
        }

    def rollback(self, workflow_id: str,
                 to_version: Optional[int] = None) -> dict:
        """Restore to a previous snapshot (default: one back). Records the
        revert itself as a 'rollback' version so history is intact."""
        latest = self.get(workflow_id, None)
        if latest is None:
            return {"ok": False, "reason": "no history"}
        cur = latest["version"]
        target = to_version if to_version is not None else max(1, cur - 1)
        target_row = self.get(workflow_id, target)
        if target_row is None:
            return {"ok": False, "reason": f"version {target} not found",
                    "latest": cur}
        restored = target_row["snapshot"]
        new_version = self.snapshot(
            workflow_id, restored, name="rollback-to-v%d" % target, kind="rollback")
        return {"ok": True, "restored_version": new_version,
                "targets_snapshot": target, "from_version": cur}

    def history(self, workflow_id: str, limit: int = 20) -> list[dict]:
        with _LOCK:
            conn = self._connect()
            rows = conn.execute(
                "SELECT version, name, sha256, created_at, kind FROM workflow_versions "
                "WHERE workflow_id = ? ORDER BY version DESC LIMIT ?",
                (workflow_id, limit)).fetchall()
            conn.close()
        return [dict(r) for r in rows]


if __name__ == "__main__":
    import tempfile
    vc = WorkflowVersionControl(db_path=tempfile.mktemp(suffix="_v.db"))
    v1 = {"nodes": [{"name": "A", "type": "n8n-nodes-base.webhook"}]}
    v2 = {"nodes": [{"name": "A", "type": "n8n-nodes-base.webhook"},
                    {"name": "B", "type": "n8n-nodes-base.httpRequest",
                     "parameters": {"url": "https://bad.invalid"}}]}
    assert vc.snapshot("wf1", v1, "first") == 1
    assert vc.snapshot("wf1", v2, "touched") == 2
    print("diff:", vc.diff("wf1", 1, 2))
    print("rollback:", vc.rollback("wf1"))
    print("history:", vc.history("wf1"))