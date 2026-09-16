"""Phase-1 tests: real `opencode run` workers + build-gates QA hook.

Two tiers, labeled honestly:
  - LOCAL (always run): prompt construction, budgets, output parsing,
    runner timeout/crash via command override, real gates verdicts on
    fixture files, gates blocking a merge, tasklog format.
  - LIVE (RUN_LIVE_WORKERS=1 + `-m live`): real `opencode run` sessions —
    success, failure->retry->escalation, crash recovery. Each attempt is a
    separate disposable OS process + session; sessions asserted distinct.
"""
import json
import os

import pytest

from orchestrator import gates_qa as gates_mod
from orchestrator import opencode_worker as ocw
from orchestrator.scheduler import Orchestrator
from orchestrator.schema import with_defaults
from orchestrator.state import StateStore
from orchestrator.tasklog import TaskLog

LIVE = os.environ.get("RUN_LIVE_WORKERS") == "1"
needs_live = pytest.mark.skipif(not LIVE, reason="needs RUN_LIVE_WORKERS=1")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _store(tmp_path):
    return StateStore(str(tmp_path / "s.db"))


def _contract(tid, files=None, deps=None, acc=None, **kw):
    c = {"task_id": tid, "kind": "opencode", "role": "R", "goal": f"g {tid}",
         "outputs": [], "allowed_files": files or [f"{tid}.txt"],
         "dependencies": deps or [],
         "acceptance": acc if acc is not None else [
             {"id": "a", "kind": "file_exists", "path": f"{tid}.txt"}]}
    c.update(kw)
    return c


# ---------- LOCAL ----------------------------------------------------
def test_prompt_contains_only_task_context(tmp_path):
    c = with_defaults(_contract("t1", files=["a.txt"]))
    ctx, _ = __import__("orchestrator.worker", fromlist=["x"]).build_worker_context(
        c, {})
    prompt = ocw.build_task_prompt(c, ctx, str(tmp_path))
    assert "t1" in prompt and "a.txt" in prompt
    for forbidden in ("SECRET_PROJECT_HISTORY_BLOB", "conversation history",
                      "previous session", "whole project"):
        assert forbidden not in prompt


def test_prompt_budget_refuses_before_spawn(tmp_path):
    c = with_defaults(_contract("t1", prompt_limit_bytes=10))
    rep = ocw.run_opencode_task(c, str(tmp_path), {},
                                _argv_override=["false"])
    assert rep["ok"] is False and rep["reason"] == "CONTEXT_OVERFLOW"


def test_parse_run_output():
    raw = "\n".join([
        '{"type":"step_start","sessionID":"ses_abc"}',
        '{"type":"text","sessionID":"ses_abc","part":{"text":"DONE"}}',
        '{"type":"tool_use","sessionID":"ses_abc"}',
        "not json",
    ])
    p = ocw.parse_run_output(raw)
    assert p["session_id"] == "ses_abc"
    assert p["texts"] == ["DONE"] and p["tool_uses"] == 1


def test_runner_timeout_kills_child(tmp_path):
    c = with_defaults(_contract("t1", timeout_s=1))
    rep = ocw.run_opencode_task(c, str(tmp_path), {},
                                _argv_override=["sleep", "10"])
    assert rep["ok"] is False and rep["reason"] == "WORKER_TIMEOUT"


def test_runner_crash_is_worker_error(tmp_path):
    c = with_defaults(_contract("t1"))
    rep = ocw.run_opencode_task(c, str(tmp_path), {},
                                _argv_override=["sh", "-c", "kill -9 $$"])
    assert rep["ok"] is False and rep["reason"] == "WORKER_KILLED"


def _audit_files():
    d = os.path.join(ROOT, "memory", "audits")
    return set(os.listdir(d)) if os.path.isdir(d) else set()


def test_gates_ready_on_clean_file(tmp_path):
    f = tmp_path / "clean.py"
    f.write_text('def add(a, b):\n    """Add two numbers."""\n    return a + b\n')
    before = _audit_files()
    try:
        v = gates_mod.run_gates_on_file(str(f), ROOT)
    finally:
        for x in _audit_files() - before:
            try:
                os.remove(os.path.join(ROOT, "memory", "audits", x))
            except OSError:
                pass
    assert v["verdict"] == "READY_FOR_DEPLOYMENT", v


BAD_WORKFLOW = json.dumps({"nodes": [
    {"name": "Start", "type": "n8n-nodes-base.webhook", "typeVersion": 1,
     "parameters": {"path": "x"}},
    {"name": "Do", "type": "n8n-nodes-base.code", "typeVersion": 1,
     "parameters": {"jsCode": "return $json;"}}],
    "connections": {"Start": {"main": [[{"node": "Do"}]]}}})


def test_gates_reject_dangerous_code(tmp_path):
    f = tmp_path / "evil.json"
    f.write_text(BAD_WORKFLOW)
    before = _audit_files()
    try:
        v = gates_mod.run_gates_on_file(str(f), ROOT)
    finally:
        for x in _audit_files() - before:
            try:
                os.remove(os.path.join(ROOT, "memory", "audits", x))
            except OSError:
                pass
    assert v["verdict"] != "READY_FOR_DEPLOYMENT", v


def test_gates_block_merge_on_rejection(tmp_path):
    def writer(ctx, work_dir):
        with open(os.path.join(work_dir, "t1.json"), "w") as fh:
            fh.write(BAD_WORKFLOW)
        return {"notes": "bad workflow"}

    store = _store(tmp_path)
    work = str(tmp_path / "w")
    orch = Orchestrator(store, work, {"k": writer}, max_workers=1,
                        repo_root=ROOT,
                        tasklog_path=str(tmp_path / "tasklog.jsonl"))
    pid = store.create_project("gblock")
    store.add_task(pid, with_defaults(_contract(
        "t1", kind="k", files=["t1.json"], max_attempts=1,
        acc=[{"id": "a", "kind": "file_contains", "path": "t1.json",
              "text": "webhook"}])))
    counts = orch.run(pid)
    assert counts.get("ESCALATED") == 1
    t = store.get_task("t1")
    assert t["details"]["reason"] == "GATES_REJECTED"
    log = TaskLog(str(tmp_path / "tasklog.jsonl")).read_all()
    assert log and log[0]["task_id"] == "t1"
    assert log[0]["qa"]["gates"][0]["verdict"] != "READY_FOR_DEPLOYMENT"
    store.close()


def test_tasklog_has_required_fields(tmp_path):
    def writer(ctx, work_dir):
        with open(os.path.join(work_dir, "t1.txt"), "w") as fh:
            fh.write("ok")
        return {"notes": "n"}

    store = _store(tmp_path)
    orch = Orchestrator(store, str(tmp_path / "w"), {"k": writer},
                        max_workers=1, repo_root=ROOT,
                        tasklog_path=str(tmp_path / "tasklog.jsonl"))
    pid = store.create_project("tl")
    store.add_task(pid, with_defaults(_contract("t1", kind="k", gates=False)))
    assert orch.run(pid).get("DONE") == 1
    rec = TaskLog(str(tmp_path / "tasklog.jsonl")).read_all()[0]
    for key in ("task_id", "worker", "attempt", "started", "ended",
                "result", "qa", "files"):
        assert key in rec, key
    assert rec["result"] == "DONE" and rec["files"] == ["t1.txt"]
    store.close()


# ---------- LIVE (real opencode run sessions) --------------------------
@pytest.mark.live
@needs_live
def test_live_success_two_tasks_two_sessions(tmp_path):
    store = _store(tmp_path)
    orch = Orchestrator(store, str(tmp_path / "w"), {}, max_workers=2,
                        repo_root=ROOT,
                        tasklog_path=str(tmp_path / "tasklog.jsonl"))
    pid = orch.submit_project("live-ok", [
        _contract("la", files=["a.py"], timeout_s=240,
                  acc=[{"id": "a", "kind": "file_contains", "path": "a.py",
                        "text": 'GREETING = "salam"'}],
                  **{"goal": 'Create a.py containing exactly: GREETING = "salam"'}),
        _contract("lb", files=["b.py"], timeout_s=240,
                  acc=[{"id": "a", "kind": "file_contains", "path": "b.py",
                        "text": 'FAREWELL = "bye"'}],
                  **{"goal": 'Create b.py containing exactly: FAREWELL = "bye"'}),
    ])
    counts = orch.run(pid)
    assert counts.get("DONE") == 2, store.recent_events(pid, 25)
    sessions = [store.get_task(t)["details"]["session_id"] for t in ("la", "lb")]
    assert all(s and s.startswith("ses_") for s in sessions), sessions
    assert len(set(sessions)) == 2, "each attempt must be its own session"
    with open(os.path.join(str(tmp_path / "w"), "plain-la", "a.py")) as fh:
        assert 'GREETING = "salam"' in fh.read()
    store.close()


@pytest.mark.live
@needs_live
def test_live_failure_retries_then_escalates(tmp_path):
    store = _store(tmp_path)
    orch = Orchestrator(store, str(tmp_path / "w"), {}, max_workers=1,
                        repo_root=ROOT,
                        tasklog_path=str(tmp_path / "tasklog.jsonl"))
    pid = orch.submit_project("live-fail", [
        _contract("lf", files=["f.txt"], timeout_s=240, max_attempts=2,
                  acc=[{"id": "a", "kind": "file_contains", "path": "f.txt",
                        "text": "IMPOSSIBLE_STRING_XYZ"}],
                  **{"goal": "Create f.txt containing exactly: hello"}),
    ])
    counts = orch.run(pid)
    assert counts.get("ESCALATED") == 1, store.recent_events(pid, 25)
    t = store.get_task("lf")
    assert t["attempts"] == 2
    kinds = [e["kind"] for e in store.recent_events(pid, 25)]
    assert "task_retry" in kinds and "task_escalated" in kinds
    store.close()


@pytest.mark.live
@needs_live
def test_live_recovery_after_orchestrator_stop(tmp_path):
    store = _store(tmp_path)
    pid = store.create_project("live-recover")
    store.add_task(pid, with_defaults(_contract(
        "lr", files=["r.txt"], timeout_s=240,
        acc=[{"id": "a", "kind": "file_contains", "path": "r.txt",
              "text": "recovered"}],
        **{"goal": "Create r.txt containing exactly: recovered"})))
    assert store.claim_task("lr", "dead-worker", lease_s=0.05)
    import time as _t
    _t.sleep(0.1)
    assert store.recover_expired_leases(pid) == ["lr"]
    orch = Orchestrator(store, str(tmp_path / "w"), {}, max_workers=1,
                        repo_root=ROOT,
                        tasklog_path=str(tmp_path / "tasklog.jsonl"))
    assert orch.run(pid).get("DONE") == 1
    store.close()
