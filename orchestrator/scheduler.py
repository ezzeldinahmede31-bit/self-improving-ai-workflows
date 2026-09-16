"""Deterministic Orchestrator: schedule -> dispatch -> QA -> merge -> next.

Pure control loop, no LLM. Failure policy per task:
  retry (same role) -> reassign (fallback_role) -> split (NEEDS_SPLIT)
  -> human escalation (ESCALATED). Bounded attempts, leases, crash resume.
"""
from __future__ import annotations
import concurrent.futures as cf
import os
import threading
import time
import uuid

from . import qa as qa_mod
from . import worker as worker_mod
from .schema import validate, with_defaults
from .state import StateStore


class Orchestrator:
    def __init__(self, store: StateStore, work_root: str, registry: dict,
                 max_workers: int = 4, worktree_provider=None):
        self.store = store
        self.work_root = work_root
        self.registry = registry
        self.max_workers = max(1, max_workers)
        self.worktree_provider = worktree_provider  # optional gitiso hooks
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
    def run(self, project_id: str) -> dict:
        self.store.recover_expired_leases(project_id)
        with cf.ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            in_flight: dict[str, cf.Future] = {}
            while True:
                self._collect_done(project_id, in_flight)
                counts = self.store.counts(project_id)
                running = counts.get("RUNNING", 0)
                pending_ready = self.store.ready_tasks(project_id)
                capacity = self.max_workers - len(in_flight)
                for t in pending_ready[:capacity]:
                    fut = pool.submit(self._run_one, project_id, t["task_id"])
                    in_flight[t["task_id"]] = fut
                counts = self.store.counts(project_id)
                active = counts.get("PENDING", 0) + counts.get("RUNNING", 0)
                if not in_flight and active == 0:
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
    def _run_one(self, project_id: str, task_id: str) -> None:
        worker_id = "w_" + uuid.uuid4().hex[:8]
        task = self.store.get_task(task_id)
        contract = task["contract"]
        lease_s = float(contract.get("timeout_s", 120)) + 30.0
        if not self.store.claim_task(task_id, worker_id, lease_s):
            return
        self.store.record_event(project_id, "task_started",
                                {"task_id": task_id, "worker": worker_id,
                                 "role": contract.get("role")})
        work_dir, wt = self._prepare_workdir(project_id, task_id)
        try:
            provided = self._gather_inputs(project_id, contract)
            fn = self.registry.get(contract.get("kind", "generic"))
            if fn is None:
                self._fail(project_id, task_id, "NO_HANDLER",
                           f"no worker for kind={contract.get('kind')}")
                return
            res = worker_mod.execute_task(contract, work_dir, provided, fn)
            if not res["ok"]:
                self._fail(project_id, task_id, res["reason"],
                           res.get("detail", ""), extra=res)
                return
            checks = qa_mod.run_acceptance(work_dir, contract.get("acceptance", []))
            passed, failed = qa_mod.verdict(checks)
            if not passed:
                self._fail(project_id, task_id, "QA_FAIL",
                           f"failed checks: {failed}",
                           extra={"checks": checks, "summary": res["summary"]})
                return
            if wt:
                mg = self._merge_workdir(project_id, task_id, work_dir, wt)
                if not mg["ok"]:
                    self._fail(project_id, task_id, "INTEGRATION_CONFLICT",
                               mg.get("detail", ""), extra={"summary": res["summary"]})
                    return
            self.store.set_status(
                task_id, "DONE", summary=res["summary"],
                details={"outputs": res["outputs"], "changed": res["changed"],
                         "checks": checks, "worker": worker_id},
                event_kind="task_done",
                event_payload={"role": contract.get("role"),
                               "changed": res["changed"]})
        finally:
            self._cleanup_workdir(wt)

    def _fail(self, project_id: str, task_id: str, reason: str,
              detail: str = "", extra: dict | None = None) -> None:
        task = self.store.get_task(task_id)
        contract = task["contract"]
        attempts = task["attempts"]
        max_attempts = int(contract.get("max_attempts", 3))
        payload = {"reason": reason, "detail": detail[:1000], "attempts": attempts}
        if extra and isinstance(extra.get("summary"), dict):
            payload["summary"] = extra["summary"]
        if attempts < max_attempts:
            self.store.requeue(task_id, f"{reason}:attempt_{attempts}")
            self.store.record_event(project_id, "task_retry", payload)
        elif contract.get("fallback_role") and contract.get("role") != contract["fallback_role"]:
            self.store.requeue(task_id, f"{reason}:reassign", new_role=contract["fallback_role"])
            self.store.record_event(project_id, "task_reassigned", payload)
        elif contract.get("splittable"):
            self.store.set_status(task_id, "NEEDS_SPLIT", summary=None,
                                 details=payload, event_kind="task_needs_split",
                                 event_payload=payload)
        else:
            self.store.set_status(task_id, "ESCALATED", summary=None,
                                 details=payload, event_kind="task_escalated",
                                 event_payload=payload)

    # -- workdirs / inputs ---------------------------------------------
    def _prepare_workdir(self, project_id: str, task_id: str):
        if self.worktree_provider:
            wt = self.worktree_provider("create", project_id, task_id)
            return wt["path"], wt
        d = os.path.join(self.work_root, f"plain-{task_id}")
        os.makedirs(d, exist_ok=True)
        return d, None

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
