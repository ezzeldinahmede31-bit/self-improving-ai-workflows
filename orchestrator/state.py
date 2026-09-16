"""Shared State Store: SQLite-backed single source of truth.

Everything durable lives here (or in files it points to). Sessions/workers
are disposable: any worker can die and a new one resumes from this store.
Append-only event log; task details are archivable to summaries.
"""
from __future__ import annotations
import json
import sqlite3
import threading
import time
import uuid

STATUSES = ("PENDING", "RUNNING", "DONE", "FAILED", "NEEDS_SPLIT", "ESCALATED")
TERMINAL = ("DONE", "NEEDS_SPLIT", "ESCALATED")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS projects(id TEXT PRIMARY KEY, name TEXT, created_at REAL, status TEXT);
CREATE TABLE IF NOT EXISTS tasks(
  id TEXT PRIMARY KEY, project_id TEXT, contract TEXT, status TEXT,
  attempts INTEGER, role TEXT, lease_until REAL, worker_id TEXT,
  summary TEXT, details TEXT, updated_at REAL);
CREATE TABLE IF NOT EXISTS events(
  id INTEGER PRIMARY KEY AUTOINCREMENT, project_id TEXT, ts REAL, kind TEXT, payload TEXT);
CREATE INDEX IF NOT EXISTS idx_tasks_proj ON tasks(project_id, status);
CREATE INDEX IF NOT EXISTS idx_events_proj ON events(project_id, id);
"""


def _now() -> float:
    return time.time()


class StateStore:
    def __init__(self, path: str):
        self.path = path
        self._lock = threading.RLock()
        self._db = sqlite3.connect(path, check_same_thread=False)
        with self._lock:
            self._db.execute("PRAGMA journal_mode=WAL")
            self._db.executescript(_SCHEMA)
            self._db.commit()

    # -- projects ------------------------------------------------------
    def create_project(self, name: str) -> str:
        pid = "p_" + uuid.uuid4().hex[:12]
        with self._lock:
            self._db.execute(
                "INSERT INTO projects(id,name,created_at,status) VALUES(?,?,?,?)",
                (pid, name, _now(), "ACTIVE"))
            self._db.commit()
        self.record_event(pid, "project_created", {"name": name})
        return pid

    # -- tasks ---------------------------------------------------------
    def add_task(self, project_id: str, contract: dict) -> str:
        tid = contract.get("task_id") or ("t_" + uuid.uuid4().hex[:12])
        with self._lock:
            self._db.execute(
                "INSERT INTO tasks(id,project_id,contract,status,attempts,role,"
                "lease_until,worker_id,summary,details,updated_at)"
                " VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                (tid, project_id, json.dumps(contract), "PENDING", 0,
                 contract.get("role", ""), 0.0, None, None, None, _now()))
            self._db.commit()
        self.record_event(project_id, "task_added", {"task_id": tid})
        return tid

    def get_task(self, task_id: str) -> dict | None:
        with self._lock:
            row = self._db.execute(
                "SELECT id,project_id,contract,status,attempts,role,lease_until,"
                "worker_id,summary,details,updated_at FROM tasks WHERE id=?",
                (task_id,)).fetchone()
        if not row:
            return None
        return self._row_to_task(row)

    @staticmethod
    def _row_to_task(row) -> dict:
        (tid, pid, contract, status, attempts, role, lease, wid,
         summary, details, updated) = row
        return {"task_id": tid, "project_id": pid,
                "contract": json.loads(contract), "status": status,
                "attempts": attempts, "role": role, "lease_until": lease,
                "worker_id": wid,
                "summary": json.loads(summary) if summary else None,
                "details": json.loads(details) if details else None,
                "updated_at": updated}

    def list_tasks(self, project_id: str) -> list[dict]:
        with self._lock:
            rows = self._db.execute(
                "SELECT id,project_id,contract,status,attempts,role,lease_until,"
                "worker_id,summary,details,updated_at FROM tasks WHERE project_id=?",
                (project_id,)).fetchall()
        return [self._row_to_task(r) for r in rows]

    def ready_tasks(self, project_id: str) -> list[dict]:
        """PENDING tasks whose dependencies are all DONE (deterministic order)."""
        tasks = self.list_tasks(project_id)
        done = {t["task_id"] for t in tasks if t["status"] == "DONE"}
        ready = [t for t in tasks
                 if t["status"] == "PENDING"
                 and all(d in done for d in t["contract"].get("dependencies", []))]
        ready.sort(key=lambda t: t["task_id"])
        return ready

    def claim_task(self, task_id: str, worker_id: str, lease_s: float) -> bool:
        with self._lock:
            cur = self._db.execute("SELECT status FROM tasks WHERE id=?", (task_id,))
            row = cur.fetchone()
            if not row or row[0] != "PENDING":
                return False
            self._db.execute(
                "UPDATE tasks SET status='RUNNING',attempts=attempts+1,"
                "lease_until=?,worker_id=?,updated_at=? WHERE id=?",
                (_now() + lease_s, worker_id, _now(), task_id))
            self._db.commit()
        return True

    def set_status(self, task_id: str, status: str, summary=None,
                   details=None, event_kind: str | None = None,
                   event_payload: dict | None = None) -> None:
        assert status in STATUSES, status
        task = self.get_task(task_id)
        with self._lock:
            self._db.execute(
                "UPDATE tasks SET status=?,summary=?,details=?,"
                "lease_until=0,updated_at=? WHERE id=?",
                (status,
                 json.dumps(summary) if summary is not None else None,
                 json.dumps(details) if details is not None else None,
                 _now(), task_id))
            self._db.commit()
        if event_kind and task:
            p = dict(event_payload or {})
            p["task_id"] = task_id
            self.record_event(task["project_id"], event_kind, p)

    def requeue(self, task_id: str, reason: str, new_role: str | None = None) -> None:
        task = self.get_task(task_id)
        with self._lock:
            if new_role:
                contract = task["contract"]
                contract["role"] = new_role
                self._db.execute(
                    "UPDATE tasks SET status='PENDING',role=?,contract=?,"
                    "lease_until=0,worker_id=NULL,updated_at=? WHERE id=?",
                    (new_role, json.dumps(contract), _now(), task_id))
            else:
                self._db.execute(
                    "UPDATE tasks SET status='PENDING',lease_until=0,"
                    "worker_id=NULL,updated_at=? WHERE id=?", (_now(), task_id))
            self._db.commit()
        if task:
            self.record_event(task["project_id"], "task_requeued",
                              {"task_id": task_id, "reason": reason,
                               "attempts": task["attempts"] + 0})

    def recover_expired_leases(self, project_id: str, now: float | None = None) -> list[str]:
        """Crash recovery: RUNNING tasks with expired lease go back to PENDING."""
        now = now if now is not None else _now()
        reset = []
        for t in self.list_tasks(project_id):
            if t["status"] == "RUNNING" and (t["lease_until"] or 0) < now:
                self.requeue(t["task_id"], "lease_expired_recovery")
                reset.append(t["task_id"])
        return reset

    # -- events / summaries / archive ----------------------------------
    def record_event(self, project_id: str, kind: str, payload: dict) -> None:
        with self._lock:
            self._db.execute(
                "INSERT INTO events(project_id,ts,kind,payload) VALUES(?,?,?,?)",
                (project_id, _now(), kind, json.dumps(payload)))
            self._db.commit()

    def recent_events(self, project_id: str, limit: int = 50) -> list[dict]:
        with self._lock:
            rows = self._db.execute(
                "SELECT ts,kind,payload FROM events WHERE project_id=? "
                "ORDER BY id DESC LIMIT ?", (project_id, limit)).fetchall()
        return [{"ts": ts, "kind": k, "payload": json.loads(p)} for ts, k, p in rows]

    def archive_task(self, task_id: str) -> bool:
        """Drop bulky details, keep the summary. Anti-bloat primitive."""
        task = self.get_task(task_id)
        if not task or task["status"] not in TERMINAL:
            return False
        with self._lock:
            self._db.execute(
                "UPDATE tasks SET details=NULL,updated_at=? WHERE id=?",
                (_now(), task_id))
            self._db.commit()
        self.record_event(task["project_id"], "task_archived", {"task_id": task_id})
        return True

    def counts(self, project_id: str) -> dict:
        out: dict[str, int] = {}
        for t in self.list_tasks(project_id):
            out[t["status"]] = out.get(t["status"], 0) + 1
        return out

    def close(self) -> None:
        with self._lock:
            self._db.commit()
            self._db.close()
