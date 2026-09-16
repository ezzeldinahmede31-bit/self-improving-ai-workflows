"""MVP tests for the Multi-Agent Orchestrator.

Covers: contract validation, DAG levels/cycles/file-overlap, parallel
execution, worker failure + retry + escalation, worktree isolation +
integration, QA gates, context budgets, crash recovery, archiving.
"""
import json
import os
import threading
import time

from orchestrator import dag as dag_mod
from orchestrator import gitiso as g
from orchestrator.dashboard import snapshot
from orchestrator.scheduler import Orchestrator, git_worktree_provider
from orchestrator.schema import validate, with_defaults
from orchestrator.state import StateStore


def _store(tmp_path):
    return StateStore(str(tmp_path / "s.db"))


def _contract(tid, kind="k", role="R", files=None, deps=None, acc=None, **kw):
    c = {"task_id": tid, "kind": kind, "role": role, "goal": f"g {tid}",
         "outputs": [], "allowed_files": files or [f"{tid}.txt"],
         "dependencies": deps or [],
         "acceptance": acc if acc is not None else [
             {"id": "a", "kind": "file_exists", "path": f"{tid}.txt"}]}
    c.update(kw)
    c.setdefault("gates", False)  # MVP scope: gates covered in Phase-1 tests
    return c


def _writer(name, text="x", outputs=None, notes=""):
    def fn(ctx, work_dir):
        with open(os.path.join(work_dir, name), "w") as fh:
            fh.write(text)
        return {"notes": notes, "outputs": outputs or {}}
    return fn


# -- schema -----------------------------------------------------------
def test_contract_validation_rejects_uncheckable():
    errs = validate({"task_id": "t"})
    assert any("missing required field" in e for e in errs)
    bad = _contract("t", acc=[{"id": "a", "kind": "vibes"}])
    assert any("kind" in e for e in validate(bad))
    good = _contract("t")
    assert validate(good) == []


# -- dag --------------------------------------------------------------
def test_dag_levels_diamond():
    contracts = [_contract("db"), _contract("api", deps=["db"]),
                 _contract("fe", deps=["api"]),
                 _contract("integ", deps=["api"]),
                 _contract("e2e", deps=["fe", "integ"])]
    edges = dag_mod.build_edges(contracts)
    assert dag_mod.detect_cycle(edges) is None
    assert dag_mod.levels(edges) == [["db"], ["api"], ["fe", "integ"], ["e2e"]]


def test_dag_cycle_detected():
    edges = {"a": {"b"}, "b": {"a"}}
    assert dag_mod.detect_cycle(edges) is not None


def test_file_overlap_serializes():
    a = _contract("a", files=["shared.txt"])
    b = _contract("b", files=["shared.txt"])
    edges = dag_mod.build_edges([a, b])
    assert edges["b"] == {"a"}  # never parallel on the same file


# -- scheduler: parallel ----------------------------------------------
def test_parallel_execution(tmp_path):
    marks = {}
    lock = threading.Lock()

    def slow(name, delay=0.4):
        def fn(ctx, work_dir):
            with lock:
                marks[name] = (time.time(), None)
            time.sleep(delay)
            with lock:
                s, _ = marks[name]
                marks[name] = (s, time.time())
            with open(os.path.join(work_dir, f"{name}.txt"), "w") as fh:
                fh.write("ok")
            return {"notes": name}
        return fn

    store = _store(tmp_path)
    orch = Orchestrator(store, str(tmp_path / "w"),
                        {"s1": slow("s1"), "s2": slow("s2")}, max_workers=2)
    pid = orch.submit_project("par", [
        _contract("t1", kind="s1", files=["s1.txt"], gates=False,
                  acc=[{"id": "a", "kind": "file_exists", "path": "s1.txt"}]),
        _contract("t2", kind="s2", files=["s2.txt"], gates=False,
                  acc=[{"id": "a", "kind": "file_exists", "path": "s2.txt"}]),
    ])
    t0 = time.time()
    counts = orch.run(pid)
    wall = time.time() - t0
    assert counts.get("DONE") == 2
    (s1, e1), (s2, e2) = marks["s1"], marks["s2"]
    assert max(s1, s2) < min(e1, e2), "tasks did not overlap in time"
    assert wall < 0.8, f"not parallel: wall={wall}"
    store.close()


# -- scheduler: failure policy ----------------------------------------
def test_retry_then_success(tmp_path):
    calls = {"n": 0}

    def flaky(ctx, work_dir):
        calls["n"] += 1
        if calls["n"] < 3:
            raise RuntimeError("boom")
        with open(os.path.join(work_dir, "t1.txt"), "w") as fh:
            fh.write("ok")
        return {"notes": "recovered"}

    store = _store(tmp_path)
    orch = Orchestrator(store, str(tmp_path / "w"), {"k": flaky}, max_workers=1)
    pid = orch.submit_project("flaky", [_contract("t1", max_attempts=3)])
    assert orch.run(pid).get("DONE") == 1
    assert store.get_task("t1")["attempts"] == 3
    store.close()


def test_exhaustion_escalates(tmp_path):
    def always(ctx, work_dir):
        raise RuntimeError("dead")

    store = _store(tmp_path)
    orch = Orchestrator(store, str(tmp_path / "w"), {"k": always}, max_workers=1)
    pid = orch.submit_project("dead", [_contract("t1", max_attempts=2)])
    assert orch.run(pid).get("ESCALATED") == 1
    kinds = [e["kind"] for e in store.recent_events(pid, 20)]
    assert "task_escalated" in kinds
    store.close()


def test_reassign_uses_fallback_role(tmp_path):
    def always(ctx, work_dir):
        raise RuntimeError("dead")

    store = _store(tmp_path)
    orch = Orchestrator(store, str(tmp_path / "w"), {"k": always}, max_workers=1)
    pid = orch.submit_project("re", [_contract("t1", max_attempts=1,
                                              fallback_role="Specialist")])
    orch.run(pid)
    kinds = [e["kind"] for e in store.recent_events(pid, 20)]
    assert "task_reassigned" in kinds
    # fallback also fails with max_attempts=1 -> escalated
    assert store.get_task("t1")["status"] == "ESCALATED"
    store.close()


# -- qa gates ----------------------------------------------------------
def test_qa_fail_blocks_task(tmp_path):
    store = _store(tmp_path)
    orch = Orchestrator(store, str(tmp_path / "w"),
                        {"k": _writer("t1.txt", text="wrong")}, max_workers=1)
    pid = orch.submit_project("qa", [_contract(
        "t1", max_attempts=1,
        acc=[{"id": "a", "kind": "file_contains", "path": "t1.txt",
              "text": "EXPECTED"}])])
    assert orch.run(pid).get("ESCALATED") == 1
    kinds = [e["kind"] for e in store.recent_events(pid, 20)]
    assert "task_escalated" in kinds
    store.close()


def test_file_violation_blocks_task(tmp_path):
    def rogue(ctx, work_dir):
        with open(os.path.join(work_dir, "elsewhere.txt"), "w") as fh:
            fh.write("x")
        with open(os.path.join(work_dir, "t1.txt"), "w") as fh:
            fh.write("x")
        return {"notes": "rogue"}

    store = _store(tmp_path)
    orch = Orchestrator(store, str(tmp_path / "w"), {"k": rogue}, max_workers=1)
    pid = orch.submit_project("rogue", [_contract("t1", max_attempts=1)])
    orch.run(pid)
    assert store.get_task("t1")["status"] == "ESCALATED"
    store.close()


# -- context budget ----------------------------------------------------
def test_context_overflow_fails_task_cleanly(tmp_path):
    big_inputs = {"blob": "Z" * 5000}
    store = _store(tmp_path)
    orch = Orchestrator(store, str(tmp_path / "w"),
                        {"k": _writer("t1.txt")}, max_workers=1)
    pid = orch.submit_project("ctx", [
        _contract("t0", acc=[{"id": "a", "kind": "file_exists", "path": "t0.txt"}]),
        _contract("t1", deps=["t0"], context_limit_bytes=100, max_attempts=1),
    ])

    # inject an oversized dependency output to force overflow
    t0 = store.get_task("t0")
    assert t0 is not None
    store.set_status("t0", "DONE", summary={"task_id": "t0"},
                     details={"outputs": big_inputs, "changed": [], "checks": []},
                     event_kind="task_done", event_payload={})
    # remove the plain workdir file expectation: t1 has no handler output issue;
    # run only t1 by marking t0 done (already) -> t1 ready, will overflow
    orch.run(pid)
    t1 = store.get_task("t1")
    assert t1["status"] == "ESCALATED"
    assert t1["details"]["reason"] == "CONTEXT_OVERFLOW"
    store.close()


# -- crash recovery ----------------------------------------------------
def test_crash_recovery_requeues_lease(tmp_path):
    store = StateStore(str(tmp_path / "s.db"))
    pid = store.create_project("crash")
    store.add_task(pid, with_defaults(_contract("t1")))
    assert store.claim_task("t1", "dead-worker", lease_s=0.05)
    time.sleep(0.1)
    reset = store.recover_expired_leases(pid)
    assert reset == ["t1"]
    assert store.get_task("t1")["status"] == "PENDING"
    # a fresh orchestrator instance completes it (simulates restart)
    orch = Orchestrator(store, str(tmp_path / "w"),
                        {"k": _writer("t1.txt")}, max_workers=1)
    assert orch.run(pid).get("DONE") == 1
    store.close()


# -- archiving ---------------------------------------------------------
def test_archive_drops_details_keeps_summary(tmp_path):
    store = _store(tmp_path)
    pid = store.create_project("arc")
    store.add_task(pid, with_defaults(_contract("t1")))
    store.set_status("t1", "DONE", summary={"task_id": "t1", "notes": "s"},
                     details={"outputs": {}, "bulk": "Z" * 1000},
                     event_kind="task_done", event_payload={})
    assert store.archive_task("t1") is True
    t = store.get_task("t1")
    assert t["details"] is None and t["summary"]["notes"] == "s"
    store.close()


# -- git isolation -----------------------------------------------------
def test_worktree_isolation_and_merge(tmp_path):
    repo = str(tmp_path / "repo")
    g.init_repo(repo)
    with open(os.path.join(repo, "base.txt"), "w") as fh:
        fh.write("base")
    assert g._git(["add", "-A"], repo)[0] == 0
    assert g._git(["commit", "-m", "base"], repo)[0] == 0

    store = _store(tmp_path)
    provider = git_worktree_provider(repo, str(tmp_path / "wt"))
    orch = Orchestrator(store, str(tmp_path / "w"),
                        {"a": _writer("a.txt", text="from-a"),
                         "b": _writer("b.txt", text="from-b")},
                        max_workers=2, worktree_provider=provider)
    pid = orch.submit_project("git", [
        _contract("ta", kind="a", files=["a.txt"],
                  acc=[{"id": "a", "kind": "file_contains", "path": "a.txt",
                        "text": "from-a"}]),
        _contract("tb", kind="b", files=["b.txt"],
                  acc=[{"id": "a", "kind": "file_contains", "path": "b.txt",
                        "text": "from-b"}]),
    ])
    assert orch.run(pid).get("DONE") == 2
    for name, text in (("a.txt", "from-a"), ("b.txt", "from-b")):
        with open(os.path.join(repo, name)) as fh:
            assert fh.read() == text
    store.close()


def test_merge_conflict_reported(tmp_path):
    repo = str(tmp_path / "repo")
    g.init_repo(repo)
    with open(os.path.join(repo, "same.txt"), "w") as fh:
        fh.write("v0\n")
    g._git(["add", "-A"], repo)
    g._git(["commit", "-m", "base"], repo)
    g._git(["checkout", "-b", "wt/conflict"], repo)
    with open(os.path.join(repo, "same.txt"), "w") as fh:
        fh.write("theirs\n")
    g._git(["commit", "-am", "theirs"], repo)
    g._git(["checkout", "main"], repo)
    with open(os.path.join(repo, "same.txt"), "w") as fh:
        fh.write("ours\n")
    g._git(["commit", "-am", "ours"], repo)
    out = g.merge_branch(repo, "wt/conflict")
    assert out["ok"] is False and out["reason"] == "CONFLICT"


# -- dashboard ----------------------------------------------------------
def test_dashboard_snapshot(tmp_path):
    store = _store(tmp_path)
    orch = Orchestrator(store, str(tmp_path / "w"),
                        {"k": _writer("t1.txt")}, max_workers=1)
    pid = orch.submit_project("dash", [_contract("t1")])
    orch.run(pid)
    snap = snapshot(store, pid)
    assert snap["counts"].get("DONE") == 1
    assert snap["tasks"][0]["task_id"] == "t1"
    store.close()


# -- selective integration: stale worktree reaper -------------------------
def test_reap_stale_removes_only_inactive(tmp_path):
    from orchestrator import gitiso as g2
    repo = str(tmp_path / "repo")
    g2.init_repo(repo)
    wt1 = g2.create_worktree(repo, "keep", str(tmp_path / "wt"))
    wt2 = g2.create_worktree(repo, "stale", str(tmp_path / "wt"))
    assert os.path.isdir(wt1["path"]) and os.path.isdir(wt2["path"])
    rep = g2.reap_stale(repo, str(tmp_path / "wt"), {wt1["path"]})
    assert rep["removed_worktrees"] == [wt2["path"]]
    assert "wt/stale" in rep["deleted_branches"]
    assert os.path.isdir(wt1["path"]) and not os.path.exists(wt2["path"])
    # main branch untouched
    rc, out = g2._git(["branch", "--list", "main"], repo)
    assert rc == 0 and "main" in out


# -- selective integration: merge-time live-overlap assert ------------------
def test_live_overlap_helper(tmp_path):
    from orchestrator.scheduler import Orchestrator as O2
    store = _store(tmp_path)
    pid = store.create_project("ov")
    store.add_task(pid, with_defaults(_contract("ta", files=["shared.txt"])))
    store.add_task(pid, with_defaults(_contract("tb", files=["shared.txt"])))
    assert store.claim_task("ta", "ext", lease_s=600)
    orch = O2(store, str(tmp_path / "w"), {}, max_workers=1)
    assert orch._live_overlap(pid, "tb", ["shared.txt"]) == ["ta:['shared.txt']"]
    assert orch._live_overlap(pid, "tb", ["other.txt"]) == []
    store.close()


def test_live_overlap_blocks_merge(tmp_path):
    from orchestrator import gitiso as g2
    from orchestrator.scheduler import Orchestrator as O2
    from orchestrator.scheduler import git_worktree_provider as gwp
    repo = str(tmp_path / "repo")
    g2.init_repo(repo)

    def writer(ctx, work_dir):
        with open(os.path.join(work_dir, "shared.txt"), "w") as fh:
            fh.write("b")
        return {"notes": "b"}

    store = _store(tmp_path)
    pid = store.create_project("ovm")
    store.add_task(pid, with_defaults(_contract("ta", files=["shared.txt"])))
    assert store.claim_task("ta", "external-slow-worker", lease_s=600)
    store.add_task(pid, with_defaults(_contract(
        "tb", kind="k", files=["shared.txt"], max_attempts=1,
        acc=[{"id": "a", "kind": "file_contains", "path": "shared.txt",
              "text": "b"}])))
    orch = O2(store, str(tmp_path / "w"), {"k": writer}, max_workers=1,
              worktree_provider=gwp(repo, str(tmp_path / "wt")))
    orch.run(pid)
    tb = store.get_task("tb")
    assert tb["status"] == "ESCALATED"
    assert tb["details"]["reason"] == "INTEGRATION_CONFLICT"
    store.close()
