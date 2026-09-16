"""Safe-Split Optimizer + remaining-gap closures.

LOCAL: split verdicts (SAFE/UNSAFE/DEFERRED), DAG rebuild verification,
cost-model refusal, hub isolation, KB fuzzy match, spawn-hook kill.
LIVE (-m live): split E2E on real workers, real timeout, real kill.
"""
import os
import time

import pytest

from orchestrator import research as R
from orchestrator import splitter as S
from orchestrator.scheduler import Orchestrator
from orchestrator.schema import with_defaults
from orchestrator.state import StateStore

LIVE = os.environ.get("RUN_LIVE_WORKERS") == "1"
needs_live = pytest.mark.skipif(not LIVE, reason="needs RUN_LIVE_WORKERS=1")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _store(tmp_path):
    return StateStore(str(tmp_path / "s.db"))


def _big(files, groups=None, est=120, **kw):
    acc = [{"id": f"a{i}", "kind": "file_contains", "path": f,
            "text": "x"} for i, f in enumerate(files)]
    c = {"task_id": "big", "kind": "opencode", "role": "Backend",
         "goal": "write the files", "outputs": [],
         "allowed_files": files, "dependencies": [],
         "acceptance": acc, "splittable": True, "split_by": "files",
         "file_groups": groups or [], "estimate_s": est, "gates": False,
         "model_policy": "primary-only"}
    c.update(kw)
    return with_defaults(c)


# ---------- LOCAL: decisions --------------------------------------------
def test_safe_via_declared_groups():
    d = S.decide(_big(["a.py", "b.py", "c.py"],
                      groups=[["a.py"], ["b.py", "c.py"]]))
    assert d["verdict"] == "SAFE_SPLIT", d
    assert len(d["generated_subtasks"]) == 2
    assert d["gain_s"] > 0 and d["cost_s"] >= 0
    assert d["evidence"]["rollback"]


def test_unsafe_single_file():
    assert S.decide(_big(["only.py"]))["verdict"] == "UNSAFE_SPLIT"


def test_unsafe_shared_state():
    d = S.decide(_big(["a.py", "config.yaml"],
                      groups=[["a.py"], ["config.yaml"]]))
    assert d["verdict"] == "UNSAFE_SPLIT"
    assert d["reason"] == "shared-state-files"


def test_unsafe_outputs():
    d = S.decide(_big(["a.py", "b.py"], groups=[["a.py"], ["b.py"]],
                      outputs=["bundle"]))
    assert d["verdict"] == "UNSAFE_SPLIT"


def test_unsafe_acceptance_outside_files():
    c = _big(["a.py", "b.py"], groups=[["a.py"], ["b.py"]])
    c["acceptance"].append({"id": "zx", "kind": "file_exists",
                            "path": "ghost.py"})
    assert S.decide(c)["verdict"] == "UNSAFE_SPLIT"


def test_unsafe_economics_tiny_task():
    d = S.decide(_big(["a.py", "b.py"], groups=[["a.py"], ["b.py"]], est=4))
    assert d["verdict"] == "UNSAFE_SPLIT"
    assert d["reason"] == "coordination-exceeds-gain"


def test_deferred_when_files_missing(tmp_path):
    c = _big(["a.py", "b.py"])
    d = S.decide(c, repo_root=str(tmp_path))
    assert d["verdict"] == "DEFERRED_REVIEW"


def test_unsafe_dense_coupling(tmp_path):
    for name, body in (("a.py", "import b\nimport c\n"),
                       ("b.py", "import a\nimport c\n"),
                       ("c.py", "import a\nimport b\n")):
        with open(os.path.join(str(tmp_path), name), "w") as fh:
            fh.write(body)
    c = _big(["a.py", "b.py", "c.py"], est=200)
    d = S.decide(c, repo_root=str(tmp_path))
    assert d["verdict"] == "UNSAFE_SPLIT", d


def test_greedy_keeps_test_with_source(tmp_path):
    with open(os.path.join(str(tmp_path), "m.py"), "w") as fh:
        fh.write("X = 1\n")
    with open(os.path.join(str(tmp_path), "test_m.py"), "w") as fh:
        fh.write("import m\n")
    with open(os.path.join(str(tmp_path), "z.py"), "w") as fh:
        fh.write("Y = 2\n")
    c = _big(["m.py", "test_m.py", "z.py"], est=200)
    d = S.decide(c, repo_root=str(tmp_path))
    assert d["verdict"] == "SAFE_SPLIT", d
    parts = d["partitions"]
    together = [p for p in parts if "m.py" in p]
    assert together and "test_m.py" in together[0]


# ---------- LOCAL: DAG rebuild --------------------------------------------
def _wf(est_map=None, tail_dep=None):
    est_map = est_map or {}
    def c(tid, deps=None, **kw):
        d = {"task_id": tid, "kind": "k", "role": "R", "goal": "g",
             "outputs": [], "allowed_files": [f"{tid}.txt"],
             "dependencies": deps or [],
             "acceptance": [{"id": "a", "kind": "file_exists",
                             "path": f"{tid}.txt"}],
             "estimate_s": est_map.get(tid, 60), "gates": False}
        d.update(kw)
        return with_defaults(d)
    return [c("db"), c("api", ["db"]), c("fe", ["api"]),
            c("e2e", ["fe"] + ([tail_dep] if tail_dep else []))]


def test_optimize_rewires_and_verifies():
    contracts = _wf(tail_dep="big") + [_big(["w1.py", "w2.py"],
                                            groups=[["w1.py"], ["w2.py"]],
                                            est=300)]
    contracts[-1]["task_id"] = "big"
    contracts[-1]["allowed_files"] = ["w1.py", "w2.py"]
    contracts[-1]["acceptance"] = [
        {"id": "a0", "kind": "file_contains", "path": "w1.py", "text": "x"},
        {"id": "a1", "kind": "file_contains", "path": "w2.py", "text": "x"}]
    out, rep = S.optimize_project(contracts)
    assert rep["cycle"] is None
    assert rep["decisions"][-1]["verdict"] == "SAFE_SPLIT"
    assert rep["makespan_gain_s"] > 0
    assert rep["metrics_after"]["max_width"] >= 2
    ids = [c["task_id"] for c in out]
    assert "big#1" in ids and "big#2" in ids and "big" not in ids


def test_optimize_refuses_unsafe_keeps_task():
    contracts = _wf()
    bad = _big(["only.py"])
    bad["task_id"] = "solo"
    bad["allowed_files"] = ["solo.py"]
    bad["acceptance"] = [{"id": "a", "kind": "file_exists",
                          "path": "solo.py"}]
    contracts.append(bad)
    out, rep = S.optimize_project(contracts)
    assert any(d["task_id"] == "solo" and d["verdict"] == "UNSAFE_SPLIT"
               for d in rep["decisions"])
    assert "solo" in [c["task_id"] for c in out]


# ---------- LOCAL: KB fuzzy + spawn hook ------------------------------------
def test_kb_fuzzy_match(tmp_path):
    store = _store(tmp_path)
    R.kb_save(store, "url shortener", {"pick": "a"}, ["https://s"], "p1")
    assert R.kb_lookup(store, "URL Shortener")["match"] == "exact"
    fuzzy = R.kb_lookup(store, "url shorteners self hosted")
    assert fuzzy and fuzzy["match"] == "fuzzy" and fuzzy["score"] >= 0.35
    assert R.kb_lookup(store, "quantum banana firmware") is None
    store.close()


def test_spawn_hook_kills_child(tmp_path):
    from orchestrator import opencode_worker as ocw
    c = with_defaults({"task_id": "t", "kind": "opencode", "role": "R",
                       "goal": "g", "outputs": [], "allowed_files": [],
                       "dependencies": [],
                       "acceptance": [{"id": "a", "kind": "file_exists",
                                       "path": "never.txt"}]})
    killed = []

    def hook(proc):
        time.sleep(0.2)
        proc.kill()
        killed.append(True)

    t0 = time.time()
    rep = ocw.run_opencode_task(c, str(tmp_path), {},
                                _argv_override=["sleep", "30"],
                                spawn_hook=hook)
    assert rep["ok"] is False and rep["reason"] == "WORKER_KILLED"
    assert killed and (time.time() - t0) < 10
    full = ocw.execute_opencode_task(c, str(tmp_path), {},
                                     _argv_override=["sleep", "30"],
                                     spawn_hook=lambda p: p.kill())
    assert full["reason"] in ("WORKER_KILLED", "WORKER_ERROR")


# ---------- LIVE ---------------------------------------------------------------
@pytest.mark.live
@needs_live
def test_live_split_e2e_parallel(tmp_path):
    from orchestrator.models import ModelRouter, load_live_catalog, \
        resolve_primary
    catalog = load_live_catalog()
    primary = resolve_primary(catalog)
    assert primary
    store = _store(tmp_path)
    work = str(tmp_path / "w")
    log = str(tmp_path / "tasklog.jsonl")
    router = ModelRouter({"models": {primary: {"type": "unlimited",
                                               "max_parallel": 4}}},
                         catalog, store)
    orch = Orchestrator(store, work, {}, max_workers=3, repo_root=ROOT,
                        tasklog_path=log, router=router)
    big = _big(["p1.py", "p2.py"], groups=[["p1.py"], ["p2.py"]], est=120)
    big.update({
        "goal": "Write p1.py containing LINE_ONE = 1 and p2.py containing "
                "LINE_TWO = 2 (exact identifiers, small files).",
        "acceptance": [
            {"id": "a0", "kind": "file_contains", "path": "p1.py",
             "text": "LINE_ONE"},
            {"id": "a1", "kind": "file_contains", "path": "p2.py",
             "text": "LINE_TWO"}],
        "timeout_s": 240, "gates": True})
    new_contracts, rep = S.optimize_project([big])
    assert rep["decisions"][0]["verdict"] == "SAFE_SPLIT"
    assert rep["makespan_gain_s"] > 0
    pid = orch.submit_project("live-split", new_contracts)
    counts = orch.run(pid)
    assert counts.get("DONE") == 2, store.recent_events(pid, 10)
    import json as _json
    lines = [_json.loads(l) for l in open(log, encoding="utf-8")]
    starts = sorted(l["started"] for l in lines)
    ends = sorted(l["ended"] for l in lines)
    assert starts[1] < ends[0], "subtasks must overlap (parallel)"
    assert all(l.get("model") == primary for l in lines)
    store.close()


@pytest.mark.live
@needs_live
def test_live_timeout_enforced(tmp_path):
    from orchestrator.models import ModelRouter, load_live_catalog, \
        resolve_primary
    catalog = load_live_catalog()
    primary = resolve_primary(catalog)
    assert primary
    store = _store(tmp_path)
    router = ModelRouter({"models": {primary: {"type": "unlimited",
                                               "max_parallel": 4}}},
                         catalog, store)
    orch = Orchestrator(store, str(tmp_path / "w"), {}, max_workers=1,
                        repo_root=ROOT,
                        tasklog_path=str(tmp_path / "tasklog.jsonl"),
                        router=router)
    c = with_defaults({"task_id": "slow", "kind": "opencode",
                       "role": "Writer", "goal": "Write f1.txt then f2.txt then "
                       "f3.txt, each with 80 lines of documented Python code, "
                       "then reply DONE.", "outputs": [],
                       "allowed_files": ["f1.txt", "f2.txt", "f3.txt"],
                       "dependencies": [],
                       "acceptance": [{"id": "a", "kind": "file_exists",
                                       "path": "f1.txt"}],
                       "timeout_s": 5, "max_attempts": 1, "gates": False,
                       "model_policy": "primary-only"})
    pid = orch.submit_project("live-timeout", [c])
    assert orch.run(pid).get("ESCALATED") == 1
    assert store.get_task("slow")["details"]["reason"] == "WORKER_TIMEOUT"
    store.close()


@pytest.mark.live
@needs_live
def test_live_kill_enforced(tmp_path):
    from orchestrator.models import load_live_catalog, resolve_primary, \
        ModelRouter
    catalog = load_live_catalog()
    primary = resolve_primary(catalog)
    assert primary
    store = _store(tmp_path)
    router = ModelRouter({"models": {primary: {"type": "unlimited",
                                               "max_parallel": 4}}},
                         catalog, store)

    def killer(proc):
        time.sleep(6)
        proc.kill()

    orch = Orchestrator(store, str(tmp_path / "w"), {}, max_workers=1,
                        repo_root=ROOT,
                        tasklog_path=str(tmp_path / "tasklog.jsonl"),
                        router=router, spawn_hook=killer)
    c = with_defaults({"task_id": "doomed", "kind": "opencode",
                       "role": "Writer",
                       "goal": "Write out.txt with the word hello.",
                       "outputs": [], "allowed_files": ["out.txt"],
                       "dependencies": [],
                       "acceptance": [{"id": "a", "kind": "file_exists",
                                       "path": "out.txt"}],
                       "timeout_s": 200, "max_attempts": 1, "gates": False,
                       "model_policy": "primary-only"})
    pid = orch.submit_project("live-kill", [c])
    assert orch.run(pid).get("ESCALATED") == 1
    assert store.get_task("doomed")["details"]["reason"] == "WORKER_KILLED"
    store.close()
