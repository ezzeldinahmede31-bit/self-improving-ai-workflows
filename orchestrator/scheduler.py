"""Deterministic Orchestrator: schedule -> dispatch -> QA -> merge -> next.

Pure control loop, no LLM. Failure policy per task:
  retry (same role) -> reassign (fallback_role) -> split (NEEDS_SPLIT)
  -> human escalation (ESCALATED). Bounded attempts, leases, crash resume.
"""
from __future__ import annotations
import concurrent.futures as cf
import datetime
import os
import threading
import time
import uuid

from . import qa as qa_mod
from . import worker as worker_mod
from . import gates_qa as gates_qa_mod
from . import models as models_mod
from . import dag as dag_mod
from . import opencode_worker as ocw_mod
from .schema import validate, with_defaults
from .state import StateStore
from .tasklog import TaskLog


def _iso(ts: float) -> str:
    return datetime.datetime.fromtimestamp(ts).isoformat(timespec="seconds")


class Orchestrator:
    def __init__(self, store: StateStore, work_root: str, registry: dict,
                 max_workers: int = 4, worktree_provider=None,
                 repo_root: str | None = None, tasklog_path: str | None = None,
                 router=None, models_registry: dict | None = None,
                 models_catalog: list | None = None):
        self.store = store
        self.work_root = work_root
        self.registry = registry
        self.max_workers = max(1, max_workers)
        self.worktree_provider = worktree_provider  # optional gitiso hooks
        self.repo_root = repo_root or os.getcwd()
        self.tasklog = TaskLog(tasklog_path or os.path.join(
            work_root, "tasklog.jsonl"))
        self.router = router or models_mod.ModelRouter(
            models_registry, models_catalog, store)
        self._selections: dict[str, dict] = {}
        os.makedirs(work_root, exist_ok=True)

    # -- project setup -------------------------------------------------
    def submit_project(self, name: str, contracts: list[dict]) -> str:
        for c in contracts:
            errs = validate(c)
            if errs:
                raise ValueError(f"invalid contract {c.get('task_id')}: {errs}")
        pid = self.store.create_project(name)
        for c in contracts:
            self.store.add_task(pid, with_defaults(c))
        return pid

    # -- main loop -----------------------------------------------------
    def _effective_ready(self, project_id: str) -> list[dict]:
        """Ready = PENDING with all EFFECTIVE deps DONE.

        Effective deps = declared dependencies + automatic file-overlap
        edges (two tasks writing the same file never run in parallel).
        """
        tasks = self.store.list_tasks(project_id)
        contracts = [t["contract"] for t in tasks]
        try:
            edges = dag_mod.build_edges(contracts)
        except Exception:  # noqa: BLE001 - fall back to declared deps
            edges = {t["task_id"]: set(t["contract"].get("dependencies", []))
                     for t in tasks}
        done = {t["task_id"] for t in tasks if t["status"] == "DONE"}
        ready = []
        for t in tasks:
            if t["status"] != "PENDING":
                continue
            deps = edges.get(t["task_id"], set())
            if all(d in done for d in deps):
                ready.append(t)
        ready.sort(key=lambda t: t["task_id"])
        return ready

    def run(self, project_id: str) -> dict:
        self.store.recover_expired_leases(project_id)
        with cf.ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            in_flight: dict[str, cf.Future] = {}
            while True:
                self._collect_done(project_id, in_flight)
                counts = self.store.counts(project_id)
                capacity = self.max_workers - len(in_flight)
                for t in self._effective_ready(project_id):
                    if len(in_flight) >= self.max_workers:
                        break
                    tid = t["task_id"]
                    sel = self.router.select(t["contract"], tid)
                    if sel["deferred"]:
                        self.store.defer_task(tid, sel["reason"], sel)
                        continue
                    if not self.router.try_acquire(sel["model"]):
                        continue  # no quota headroom this tick; stays PENDING
                    self._selections[tid] = sel
                    try:
                        fut = pool.submit(self._run_one, project_id, tid, sel)
                    except Exception:  # noqa: BLE001 - never leak quota
                        self.router.release(sel["model"])
                        raise
                    in_flight[tid] = fut
                counts = self.store.counts(project_id)
                active = counts.get("PENDING", 0) + counts.get("RUNNING", 0)
                if not in_flight and active == 0:
                    if counts.get("DEFERRED", 0):
                        self.store.record_event(
                            project_id, "project_deferred_pending",
                            {"counts": counts})
                    break
                if not in_flight and active > 0:
                    # pending tasks but none ready => blocked on FAILED deps
                    self.store.record_event(project_id, "project_blocked",
                                            {"counts": counts})
                    break
                time.sleep(0.05)
                self.store.recover_expired_leases(project_id)
        counts = self.store.counts(project_id)
        self.store.record_event(project_id, "project_finished", {"counts": counts})
        return counts

    def _collect_done(self, project_id: str, in_flight: dict) -> None:
        for tid in [t for t, f in in_flight.items() if f.done()]:
            fut = in_flight.pop(tid)
            try:
                fut.result()
            except Exception as e:  # noqa: BLE001 - never kill the loop
                self.store.record_event(project_id, "worker_crashed",
                                        {"task_id": tid, "error": str(e)})
                self._fail(project_id, tid, "WORKER_CRASH", str(e))

    # -- single task ---------------------------------------------------
    def _run_one(self, project_id: str, task_id: str,
                 selection: dict | None = None) -> None:
        worker_id = "w_" + uuid.uuid4().hex[:8]
        task = self.store.get_task(task_id)
        contract = task["contract"]
        sel = selection or self._selections.get(task_id) or \
            self.router.select(contract, task_id)
        model = sel.get("model")
        attempt_no = task["attempts"] + 1
        lease_s = float(contract.get("timeout_s", 120)) + 30.0
        if not self.store.claim_task(task_id, worker_id, lease_s):
            self.router.release(model)
            return
        t0 = time.time()
        self.store.record_event(project_id, "task_started",
                                {"task_id": task_id, "worker": worker_id,
                                 "role": contract.get("role"),
                                 "attempt": attempt_no, "model": model,
                                 "model_type": sel.get("model_type"),
                                 "selection_reason": sel.get("reason")})
        if model:
            self.store.bump_model_usage(model, "attempts")
            if sel.get("fallback_used"):
                self.store.bump_model_usage(model, "fallbacks")
        work_dir, wt = self._prepare_workdir(project_id, task_id)
        attempt_rec = {"attempt": attempt_no, "worker": worker_id,
                       "model": model, "model_type": sel.get("model_type"),
                       "selection_reason": sel.get("reason"),
                       "quota_status": sel.get("quota_status"),
                       "fallback_used": bool(sel.get("fallback_used"))}
        try:
            provided = self._gather_inputs(project_id, contract)
            if contract.get("kind") == "opencode":
                res = ocw_mod.execute_opencode_task(contract, work_dir, provided,
                                                    model=model)
            else:
                fn = self.registry.get(contract.get("kind", "generic"))
                if fn is None:
                    self._fail(project_id, task_id, "NO_HANDLER",
                               f"no worker for kind={contract.get('kind')}",
                               t0, worker_id, None)
                    return
                res = worker_mod.execute_task(contract, work_dir, provided, fn)
            if not res["ok"]:
                # runtime limit-hit on a limited model -> cooldown + primary
                if res["reason"] == "WORKER_ERROR" and \
                        self.router.model_type(model) == "limited" and \
                        self.router.is_limit_hit(res.get("detail", "")):
                    self.router.report_limit_hit(model, project_id, task_id)
                    self.router.force_primary(task_id)
                self._fail(project_id, task_id, res["reason"],
                           res.get("detail", ""), t0, worker_id,
                           res.get("session_id"), extra=res)
                return
            checks = qa_mod.run_acceptance(work_dir, contract.get("acceptance", []))
            passed, failed = qa_mod.verdict(checks)
            gate_report: dict | None = None
            if passed and contract.get("gates", True):
                gate_report = gates_qa_mod.gate_changed_files(
                    work_dir, res.get("changed", []), self.repo_root,
                    int(contract.get("gate_timeout_s", 180)))
                if not gate_report["passed"]:
                    self._fail(
                        project_id, task_id, "GATES_REJECTED",
                        f"gates failed: {[v['path'] for v in gate_report['failed']]}",
                        t0, worker_id, res.get("session_id"),
                        extra={"checks": checks, "gates": gate_report,
                               "summary": res["summary"]})
                    return
            if not passed:
                self._fail(project_id, task_id, "QA_FAIL",
                           f"failed checks: {failed}", t0, worker_id,
                           res.get("session_id"),
                           extra={"checks": checks, "summary": res["summary"]})
                return
            if wt:
                offenders = self._live_overlap(project_id, task_id,
                                               res.get("changed", []))
                if offenders:
                    self._fail(project_id, task_id, "INTEGRATION_CONFLICT",
                               f"live overlap with: {offenders}", t0, worker_id,
                               res.get("session_id"),
                               extra={"summary": res["summary"]})
                    return
                mg = self._merge_workdir(project_id, task_id, work_dir, wt)
                if not mg["ok"]:
                    self._fail(project_id, task_id, "INTEGRATION_CONFLICT",
                               mg.get("detail", ""), t0, worker_id,
                               res.get("session_id"),
                               extra={"summary": res["summary"]})
                    return
            self.store.set_status(
                task_id, "DONE", summary=res["summary"],
                details={"outputs": res["outputs"], "changed": res["changed"],
                         "checks": checks, "gates": gate_report,
                         "worker": worker_id,
                         "session_id": res.get("session_id")},
                event_kind="task_done",
                event_payload={"role": contract.get("role"),
                               "changed": res["changed"],
                               "session_id": res.get("session_id"),
                               "model": model})
            attempt_rec["result"] = "DONE"
            self.store.append_attempt(task_id, attempt_rec)
            self.tasklog.emit({
                "task_id": task_id, "worker": worker_id,
                "session_id": res.get("session_id"), "attempt": attempt_no,
                "model": model, "model_type": sel.get("model_type"),
                "selection_reason": sel.get("reason"),
                "quota_status": sel.get("quota_status"),
                "fallback_used": bool(sel.get("fallback_used")),
                "started": _iso(t0), "ended": _iso(time.time()),
                "result": "DONE", "reason": None,
                "qa": {"acceptance": "PASS",
                       "gates": (gate_report["verdicts"]
                                 if gate_report else "SKIPPED_NO_CHANGES")},
                "files": res.get("changed", [])})
        finally:
            self.router.release(model)
            self._cleanup_workdir(wt)

    def _fail(self, project_id: str, task_id: str, reason: str,
              detail: str = "", t0: float | None = None,
              worker_id: str | None = None, session_id: str | None = None,
              extra: dict | None = None) -> None:
        task = self.store.get_task(task_id)
        contract = task["contract"]
        sel = self._selections.get(task_id, {})
        attempts = task["attempts"]
        max_attempts = int(contract.get("max_attempts", 3))
        payload = {"reason": reason, "detail": detail[:1000], "attempts": attempts,
                   "model": sel.get("model"),
                   "selection_reason": sel.get("reason"),
                   "fallback_used": bool(sel.get("fallback_used"))}
        if extra and isinstance(extra.get("summary"), dict):
            payload["summary"] = extra["summary"]
        if session_id:
            payload["session_id"] = session_id
        outcome = ""
        if attempts < max_attempts:
            self.store.requeue(task_id, f"{reason}:attempt_{attempts}")
            self.store.record_event(project_id, "task_retry", payload)
            outcome = "RETRY_QUEUED"
        elif contract.get("fallback_role") and contract.get("role") != contract["fallback_role"]:
            self.store.requeue(task_id, f"{reason}:reassign", new_role=contract["fallback_role"])
            self.store.record_event(project_id, "task_reassigned", payload)
            outcome = "REASSIGNED"
        elif contract.get("splittable"):
            self.store.set_status(task_id, "NEEDS_SPLIT", summary=None,
                                 details=payload, event_kind="task_needs_split",
                                 event_payload=payload)
            outcome = "NEEDS_SPLIT"
        else:
            self.store.set_status(task_id, "ESCALATED", summary=None,
                                 details=payload, event_kind="task_escalated",
                                 event_payload=payload)
            outcome = "ESCALATED"
        self.store.append_attempt(task_id, {
            "attempt": attempts, "worker": worker_id, "result": outcome,
            "reason": reason, "model": sel.get("model"),
            "model_type": sel.get("model_type"),
            "selection_reason": sel.get("reason"),
            "quota_status": sel.get("quota_status"),
            "fallback_used": bool(sel.get("fallback_used"))})
        self.tasklog.emit({
            "task_id": task_id, "worker": worker_id, "session_id": session_id,
            "attempt": attempts,
            "model": sel.get("model"), "model_type": sel.get("model_type"),
            "selection_reason": sel.get("reason"),
            "quota_status": sel.get("quota_status"),
            "fallback_used": bool(sel.get("fallback_used")),
            "started": _iso(t0) if t0 else None, "ended": _iso(time.time()),
            "result": outcome, "reason": reason, "reason_detail": detail[:500],
            "qa": {"checks": (extra or {}).get("checks"),
                   "gates": ((extra or {}).get("gates") or {}).get("verdicts")},
            "files": (extra or {}).get("changed", [])})

    # -- report --------------------------------------------------------
    def release_deferred(self, project_id: str, reason: str = "manual") -> list[str]:
        return self.store.release_deferred(project_id, reason)

    def report(self, project_id: str) -> dict:
        """Measured evidence: wall clock, durations, observed parallelism,
        model usage, critical path. Speedup is estimate-based (labeled)."""
        events = self.store.project_events(project_id)
        tasks = {t["task_id"]: t for t in self.store.list_tasks(project_id)}
        est = {tid: float(t["contract"].get("estimate_s", 60)) for tid, t in tasks.items()}
        t0 = next((e["ts"] for e in events if e["kind"] == "project_created"), None)
        t1 = next((e["ts"] for e in reversed(events)
                   if e["kind"] == "project_finished"), None) or \
            (events[-1]["ts"] if events else t0)
        wall = round((t1 - t0), 2) if t0 and t1 else 0.0
        # per-task busy time: started -> terminal event
        busy: dict[str, float] = {}
        workers: set[str] = set()
        running = 0
        peak = 0
        starts: dict[str, float] = {}
        for e in events:
            p = e["payload"]
            k = e["kind"]
            if k == "task_started":
                tid = p.get("task_id")
                starts[(tid, p.get("attempt"))] = e["ts"]
                workers.add(str(p.get("worker")))
                running += 1
                peak = max(peak, running)
            elif k in ("task_done", "task_escalated", "task_needs_split",
                       "task_retry", "task_reassigned"):
                tid = p.get("task_id")
                key = (tid, p.get("attempts", p.get("attempt")))
                s = starts.pop(key, None)
                if s is None:
                    # fall back to latest start for the task
                    cands = [(kk, vv) for kk, vv in starts.items() if kk[0] == tid]
                    s = min([vv for _, vv in cands]) if cands else e["ts"]
                    for kk in [kk for kk, _ in cands]:
                        starts.pop(kk, None)
                busy[tid] = round(busy.get(tid, 0.0) + max(0.0, e["ts"] - s), 2)
                running = max(0, running - 1)
        # critical path over effective edges by estimates
        try:
            edges = dag_mod.build_edges([t["contract"] for t in tasks.values()])
            order = dag_mod.levels(edges)
            longest: dict[str, float] = {}
            for lv in order:
                for n in lv:
                    preds = edges.get(n, set())
                    longest[n] = est.get(n, 60.0) + max(
                        [longest.get(p, 0.0) for p in preds] or [0.0])
            cp_len = round(max(longest.values()) if longest else 0.0, 2)
        except Exception:  # noqa: BLE001
            cp_len = 0.0
        base = round(sum(est.values()), 2)
        tot_busy = round(sum(busy.values()), 2)
        denom = wall * max(1, len(workers))
        return {"counts": self.store.counts(project_id),
                "wall_clock_s": wall,
                "baseline_sequential_estimate_s": base,
                "critical_path_estimate_s": cp_len,
                "actual_speedup_vs_estimate": round(base / wall, 2) if wall else 0.0,
                "max_parallelism_observed": peak,
                "distinct_workers": len(workers),
                "agent_utilization": round(tot_busy / denom, 3) if denom else 0.0,
                "task_busy_s": busy,
                "model_usage": self.store.model_usage_summary()}

    # -- workdirs / inputs ---------------------------------------------
    def _prepare_workdir(self, project_id: str, task_id: str):
        if self.worktree_provider:
            wt = self.worktree_provider("create", project_id, task_id)
            return wt["path"], wt
        d = os.path.join(self.work_root, f"plain-{task_id}")
        os.makedirs(d, exist_ok=True)
        return d, None

    def _live_overlap(self, project_id: str, task_id: str,
                        changed: list[str]) -> list[str]:
        """Defense-in-depth: refuse merge if a RUNNING task may touch the
        same files (mirrors openorchestrator's runtime overlap check)."""
        offenders = []
        for t in self.store.list_tasks(project_id):
            if t["task_id"] == task_id or t["status"] != "RUNNING":
                continue
            overlap = set(changed) & set(t["contract"].get("allowed_files", []))
            if overlap:
                offenders.append(f"{t['task_id']}:{sorted(overlap)}")
        return sorted(offenders)

    def _merge_workdir(self, project_id: str, task_id: str, work_dir: str, wt: dict) -> dict:
        if not self.worktree_provider:
            return {"ok": True}
        try:
            sha = self.worktree_provider("commit", project_id, task_id, work_dir, wt)
            out = self.worktree_provider("merge", project_id, task_id, work_dir, wt)
            self.store.record_event(project_id, "task_merged",
                                    {"task_id": task_id, "sha": sha})
            return out
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "detail": str(e)}

    def _cleanup_workdir(self, wt) -> None:
        if wt and self.worktree_provider:
            try:
                self.worktree_provider("remove", None, None, None, wt)
            except Exception:  # noqa: BLE001, S110 - best effort cleanup
                pass

    def _gather_inputs(self, project_id: str, contract: dict) -> dict:
        provided: dict = {}
        for dep_id in contract.get("dependencies", []):
            dep = self.store.get_task(dep_id)
            if dep and dep["status"] == "DONE" and dep["details"]:
                provided[dep_id] = dep["details"].get("outputs", {})
        return provided


def git_worktree_provider(repo: str, work_root: str):
    """Adapt gitiso functions to the provider protocol used above."""
    from . import gitiso as g

    def call(op, project_id=None, task_id=None, work_dir=None, wt=None):
        if op == "create":
            return g.create_worktree(repo, task_id, work_root)
        if op == "commit":
            msg = f"task {task_id} done"
            return g.commit_all(work_dir, msg)
        if op == "merge":
            return g.merge_branch(repo, wt["branch"])
        if op == "remove":
            g.remove_worktree(repo, wt["path"], wt["branch"])
            return None
        raise ValueError(op)

    return call
