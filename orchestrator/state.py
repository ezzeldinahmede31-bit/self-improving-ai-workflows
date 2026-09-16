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

STATUSES = ("PENDING", "RUNNING", "DONE", "FAILED", "NEEDS_SPLIT",
            "ESCALATED", "DEFERRED")
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
CREATE TABLE IF NOT EXISTS model_usage(
  model TEXT PRIMARY KEY, attempts INTEGER DEFAULT 0, fallbacks INTEGER DEFAULT 0,
  limit_hits INTEGER DEFAULT 0, updated_at REAL);
CREATE TABLE IF NOT EXISTS model_cooldowns(model TEXT PRIMARY KEY, until REAL);
CREATE TABLE IF NOT EXISTS research(
  id INTEGER PRIMARY KEY AUTOINCREMENT, project_id TEXT, kind TEXT,
  topic TEXT, payload TEXT, created_at REAL);
CREATE TABLE IF NOT EXISTS arch_decisions(
  id TEXT PRIMARY KEY, project_id TEXT, decision TEXT, reason TEXT,
  evidence TEXT, effects TEXT, comparison TEXT, status TEXT, created_at REAL);
CREATE TABLE IF NOT EXISTS research_kb(
  topic TEXT PRIMARY KEY, findings TEXT, sources TEXT, project_id TEXT,
  updated_at REAL);
CREATE INDEX IF NOT EXISTS idx_research_proj ON research(project_id, kind);
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

    def defer_task(self, task_id: str, reason: str,
                   selection: dict | None = None) -> None:
        task = self.get_task(task_id)
        with self._lock:
            self._db.execute(
                "UPDATE tasks SET status='DEFERRED',lease_until=0,"
                "worker_id=NULL,updated_at=? WHERE id=?", (_now(), task_id))
            self._db.commit()
        if task:
            p = {"task_id": task_id, "reason": reason}
            if selection:
                p["selection"] = selection
            self.record_event(task["project_id"], "task_deferred", p)

    def release_deferred(self, project_id: str, reason: str = "manual") -> list[str]:
        out = []
        for t in self.list_tasks(project_id):
            if t["status"] == "DEFERRED":
                self.requeue(t["task_id"], f"deferred_released:{reason}")
                out.append(t["task_id"])
        return sorted(out)

    # -- model routing ledger ------------------------------------------
    def bump_model_usage(self, model: str, field: str) -> None:
        assert field in ("attempts", "fallbacks", "limit_hits")
        with self._lock:
            self._db.execute(
                "INSERT INTO model_usage(model,attempts,fallbacks,limit_hits,"
                "updated_at) VALUES(?,0,0,0,?) "
                "ON CONFLICT(model) DO NOTHING", (model, _now()))
            self._db.execute(
                f"UPDATE model_usage SET {field}={field}+1,updated_at=? "
                "WHERE model=?", (_now(), model))
            self._db.commit()

    def model_usage_summary(self) -> dict:
        with self._lock:
            rows = self._db.execute(
                "SELECT model,attempts,fallbacks,limit_hits FROM model_usage"
            ).fetchall()
        return {m: {"attempts": a, "fallbacks": f, "limit_hits": h}
                for m, a, f, h in rows}

    def set_model_cooldown(self, model: str, until: float) -> None:
        with self._lock:
            self._db.execute(
                "INSERT INTO model_cooldowns(model,until) VALUES(?,?) "
                "ON CONFLICT(model) DO UPDATE SET until=excluded.until",
                (model, until))
            self._db.commit()

    def model_cooldown_active(self, model: str, now: float | None = None) -> bool:
        now = now if now is not None else _now()
        with self._lock:
            row = self._db.execute(
                "SELECT until FROM model_cooldowns WHERE model=?",
                (model,)).fetchone()
        return bool(row and row[0] > now)

    # -- research ------------------------------------------------------
    def add_finding(self, project_id: str, kind: str, topic: str,
                    payload: dict) -> int:
        with self._lock:
            cur = self._db.execute(
                "INSERT INTO research(project_id,kind,topic,payload,created_at)"
                " VALUES(?,?,?,?,?)",
                (project_id, kind, topic, json.dumps(payload), _now()))
            self._db.commit()
            rid = cur.lastrowid
        self.record_event(project_id, "research_finding",
                          {"kind": kind, "topic": topic})
        return rid

    def list_findings(self, project_id: str,
                      kind: str | None = None) -> list[dict]:
        with self._lock:
            if kind:
                rows = self._db.execute(
                    "SELECT id,kind,topic,payload,created_at FROM research "
                    "WHERE project_id=? AND kind=? ORDER BY id",
                    (project_id, kind)).fetchall()
            else:
                rows = self._db.execute(
                    "SELECT id,kind,topic,payload,created_at FROM research "
                    "WHERE project_id=? ORDER BY id", (project_id,)).fetchall()
        return [{"id": r[0], "kind": r[1], "topic": r[2],
                 "payload": json.loads(r[3]), "created_at": r[4]} for r in rows]

    def add_decision(self, project_id: str, decision: str, reason: str,
                     evidence: list[str], effects: dict,
                     comparison: dict) -> str:
        did = "d_" + uuid.uuid4().hex[:12]
        with self._lock:
            self._db.execute(
                "INSERT INTO arch_decisions(id,project_id,decision,reason,"
                "evidence,effects,comparison,status,created_at)"
                " VALUES(?,?,?,?,?,?,?,?,?)",
                (did, project_id, decision, reason, json.dumps(evidence),
                 json.dumps(effects), json.dumps(comparison), "proposed",
                 _now()))
            self._db.commit()
        self.record_event(project_id, "arch_decision_proposed",
                          {"decision": decision})
        return did

    def set_decision_status(self, project_id: str, did: str,
                            status: str) -> None:
        assert status in ("proposed", "approved", "rejected")
        with self._lock:
            self._db.execute("UPDATE arch_decisions SET status=? WHERE id=?",
                             (status, did))
            self._db.commit()
        self.record_event(project_id, "arch_decision_" + status, {"id": did})

    def list_decisions(self, project_id: str,
                       status: str | None = None) -> list[dict]:
        with self._lock:
            if status:
                rows = self._db.execute(
                    "SELECT id,decision,reason,evidence,effects,comparison,"
                    "status,created_at FROM arch_decisions "
                    "WHERE project_id=? AND status=? ORDER BY created_at",
                    (project_id, status)).fetchall()
            else:
                rows = self._db.execute(
                    "SELECT id,decision,reason,evidence,effects,comparison,"
                    "status,created_at FROM arch_decisions WHERE project_id=? "
                    "ORDER BY created_at", (project_id,)).fetchall()
        return [{"id": r[0], "decision": r[1], "reason": r[2],
                 "evidence": json.loads(r[3]), "effects": json.loads(r[4]),
                 "comparison": json.loads(r[5]), "status": r[6],
                 "created_at": r[7]} for r in rows]

    def kb_put(self, topic: str, findings: dict, sources: list[str],
               project_id: str) -> None:
        with self._lock:
            self._db.execute(
                "INSERT INTO research_kb(topic,findings,sources,project_id,"
                "updated_at) VALUES(?,?,?,?,?) "
                "ON CONFLICT(topic) DO UPDATE SET findings=excluded.findings,"
                "sources=excluded.sources,project_id=excluded.project_id,"
                "updated_at=excluded.updated_at",
                (topic, json.dumps(findings), json.dumps(sources),
                 project_id, _now()))
            self._db.commit()

    def kb_get(self, topic: str) -> dict | None:
        with self._lock:
            row = self._db.execute(
                "SELECT findings,sources,project_id,updated_at FROM research_kb"
                " WHERE topic=?", (topic,)).fetchone()
        if not row:
            return None
        return {"findings": json.loads(row[0]), "sources": json.loads(row[1]),
                "project_id": row[2], "updated_at": row[3]}

    def append_attempt(self, task_id: str, entry: dict) -> None:
        """Append a per-attempt record (model, reason, quota, result)."""
        task = self.get_task(task_id)
        if not task:
            return
        details = task["details"] or {}
        log = details.get("attempts_log", [])
        log.append(entry)
        details["attempts_log"] = log
        with self._lock:
            self._db.execute("UPDATE tasks SET details=?,updated_at=? WHERE id=?",
                             (json.dumps(details), _now(), task_id))
            self._db.commit()

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

    def project_events(self, project_id: str) -> list[dict]:
        """Full ordered event stream (for reports/metrics)."""
        with self._lock:
            rows = self._db.execute(
                "SELECT ts,kind,payload FROM events WHERE project_id=? "
                "ORDER BY id", (project_id,)).fetchall()
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
