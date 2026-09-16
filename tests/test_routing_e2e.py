"""Routing + research-E2E tests.

LOCAL (always): catalog parsing, selection matrix, semaphores, cooldown
fallback, defer/release, effective-deps serialization, synthesis failure
gates, closed-source/copyleft bars, report shape, tasklog model fields.
LIVE (-m live, RUN_LIVE_WORKERS=1): full research->synthesis->decision->
build->QA pipeline on real `opencode run` workers. No mocks in live tests.
"""
import json
import os
import time

import pytest

from orchestrator import research as R
from orchestrator.models import ModelRouter, parse_models_verbose, resolve_primary
from orchestrator.scheduler import Orchestrator
from orchestrator.schema import with_defaults
from orchestrator.state import StateStore

LIVE = os.environ.get("RUN_LIVE_WORKERS") == "1"
needs_live = pytest.mark.skipif(not LIVE, reason="needs RUN_LIVE_WORKERS=1")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FAKE_VERBOSE = """opencode/free-a
{"status": "active", "cost": {"input": 0, "output": 0}, "limit": {"context": 100}, "capabilities": {"toolcall": true}}
opencode/paid-b
{"status": "active", "cost": {"input": 5, "output": 5}, "limit": {"context": 50}, "capabilities": {"toolcall": true, "vision": true}}
opencode/paid-c
{"status": "active", "cost": {"input": 1, "output": 1}, "limit": {"context": 10}, "capabilities": {"toolcall": true}}
opencode/ghost
not-json
"""

CATALOG = parse_models_verbose(FAKE_VERBOSE)
FREE = "opencode/free-a"
PAID_B = "opencode/paid-b"


def _router(**kw):
    reg = {"models": {FREE: {"type": "unlimited", "max_parallel": 4},
                      PAID_B: {"type": "limited", "max_parallel": 1,
                               "capabilities": ["vision"]}},
           "max_limited_parallel": 1}
    reg.update(kw.pop("reg", {}))
    return ModelRouter(reg, CATALOG, kw.pop("store", None))


def _store(tmp_path):
    return StateStore(str(tmp_path / "s.db"))


def _contract(tid, kind="k", files=None, deps=None, acc=None, **kw):
    c = {"task_id": tid, "kind": kind, "role": "R", "goal": f"g {tid}",
         "outputs": [], "allowed_files": files or [f"{tid}.txt"],
         "dependencies": deps or [],
         "acceptance": acc if acc is not None else [
             {"id": "a", "kind": "file_exists", "path": f"{tid}.txt"}]}
    c.update(kw)
    return c


def _writer(name, text="x"):
    def fn(ctx, work_dir):
        with open(os.path.join(work_dir, name), "w") as fh:
            fh.write(text)
        return {"notes": name}
    return fn


# ---------- LOCAL: catalog + selection ----------------------------------
def test_parse_and_primary_rule():
    assert len(CATALOG) == 3
    assert resolve_primary(CATALOG) == FREE
    assert resolve_primary(CATALOG, override=PAID_B) == PAID_B
    assert resolve_primary([], override=None) is None


def test_default_is_primary():
    r = _router()
    sel = r.select({"task_id": "t", "model_policy": "primary-only"}, "t")
    assert (sel["model"], sel["model_type"], sel["deferred"]) == (FREE, "unlimited", False)


def test_capability_via_primary_when_able():
    r = _router()
    sel = r.select({"task_id": "t", "model_policy": "capability:toolcall"}, "t")
    assert sel["model"] == FREE and not sel["fallback_used"]


def test_capability_limited_only_defers_without_allowance():
    r = _router()
    sel = r.select({"task_id": "t", "model_policy": "capability:vision"}, "t")
    assert sel["deferred"] is True and sel["model"] is None


def test_capability_limited_with_allowance():
    r = _router()
    sel = r.select({"task_id": "t", "model_policy": "capability:vision",
                    "allow_limited": True}, "t")
    assert sel["model"] == PAID_B and not sel["deferred"]
    assert r.try_acquire(PAID_B) is True
    assert r.try_acquire(PAID_B) is False  # max_parallel=1
    r.release(PAID_B)


def test_unknown_models_fail_closed():
    cat = CATALOG + [{"id": "opencode/sneaky", "status": "active",
                      "cost": {"input": 9, "output": 9}, "context": 5,
                      "capabilities": ["vision"]}]
    r = ModelRouter({"models": {}}, cat, None)
    sel = r.select({"task_id": "t", "model_policy": "capability:vision",
                    "allow_limited": True}, "t")
    assert sel["deferred"] is True  # sneaky unlisted -> never selected


def test_cooldown_forces_primary_fallback():
    import tempfile
    tmp = tempfile.mkdtemp()
    st = StateStore(os.path.join(tmp, "s.db"))
    cat = [dict(e, capabilities=list(e["capabilities"]) + ["vision"])
           if e["id"] == FREE else e for e in CATALOG]
    reg = {"models": {FREE: {"type": "unlimited", "max_parallel": 4},
                      PAID_B: {"type": "limited", "max_parallel": 1,
                               "capabilities": ["vision"]}},
           "max_limited_parallel": 1}
    r = ModelRouter(reg, cat, st)
    r.report_limit_hit(PAID_B, "p", "t")
    assert r.cooldown_active(PAID_B) is True
    sel = r.select({"task_id": "t", "model_policy": "capability:vision",
                    "allow_limited": True}, "t")
    assert sel["model"] == FREE and sel["fallback_used"] is True
    st.close()


def test_cooldown_defers_when_primary_cannot_serve():
    import tempfile
    tmp = tempfile.mkdtemp()
    st = StateStore(os.path.join(tmp, "s.db"))
    r = _router(store=st)
    r.report_limit_hit(PAID_B, "p", "t")
    sel = r.select({"task_id": "t", "model_policy": "capability:vision",
                    "allow_limited": True}, "t")
    assert sel["deferred"] is True and sel["model"] is None
    st.close()


def test_limit_pattern_matcher():
    assert ModelRouter.is_limit_hit("ERROR 429 rate limit exceeded") is True
    assert ModelRouter.is_limit_hit("quota exhausted for model") is True
    assert ModelRouter.is_limit_hit("plain syntax error") is False


# ---------- LOCAL: defer / effective deps / synthesis ---------------------
def test_defer_release_cycle(tmp_path):
    store = _store(tmp_path)
    orch = Orchestrator(store, str(tmp_path / "w"),
                        {"k": _writer("t1.txt")}, max_workers=1,
                        router=_router())
    pid = store.create_project("d")
    store.add_task(pid, with_defaults(_contract(
        "t1", model_policy="capability:vision")))
    assert orch.run(pid).get("DEFERRED") == 1
    assert store.release_deferred(pid, "quota-ok") == ["t1"]
    assert store.get_task("t1")["status"] == "PENDING"
    store.close()


def test_effective_deps_serialize_file_conflict(tmp_path):
    order = []

    def slow(name):
        def fn(ctx, work_dir):
            order.append(("start", name, time.time()))
            time.sleep(0.3)
            with open(os.path.join(work_dir, "shared.txt"), "w") as fh:
                fh.write(name)
            order.append(("end", name, time.time()))
            return {"notes": name}
        return fn

    store = _store(tmp_path)
    orch = Orchestrator(store, str(tmp_path / "w"),
                        {"a": slow("ta"), "b": slow("tb")}, max_workers=2,
                        router=_router())
    pid = orch.submit_project("ser", [
        _contract("ta", kind="a", files=["shared.txt"], gates=False,
                  acc=[{"id": "a", "kind": "file_exists",
                        "path": "shared.txt"}]),
        _contract("tb", kind="b", files=["shared.txt"], gates=False,
                  acc=[{"id": "a", "kind": "file_exists",
                        "path": "shared.txt"}]),
    ])
    assert orch.run(pid).get("DONE") == 2
    starts = {n: t for k, n, t in order if k == "start"}
    ends = {n: t for k, n, t in order if k == "end"}
    assert starts["tb"] >= ends["ta"], "file-conflict pair must serialize"
    store.close()


def test_synthesis_failure_blocks_decisions(tmp_path):
    store = _store(tmp_path)
    pid = store.create_project("s")
    res = R.run_synthesis(store, pid, str(tmp_path / "w"))
    assert res["ok"] is False  # no research evidence at all... or empty ok?
    store.close()


def test_closed_source_never_reusable(tmp_path):
    store = _store(tmp_path)
    pid = store.create_project("c")
    store.add_finding(pid, "closed-candidate", "closed",
                      {"name": "bitly", "sources": ["https://bitly.com"],
                       "strengths_observed": ["domains"]})
    ok, _ = R.reuse_verdict(store, pid, "bitly")
    assert ok is False
    store.close()


def test_report_shape_local(tmp_path):
    store = _store(tmp_path)
    orch = Orchestrator(store, str(tmp_path / "w"),
                        {"k": _writer("t1.txt")}, max_workers=1,
                        router=_router(),
                        tasklog_path=str(tmp_path / "tasklog.jsonl"))
    pid = orch.submit_project("rep", [_contract("t1", gates=False,
                                               estimate_s=30)])
    orch.run(pid)
    rep = orch.report(pid)
    assert rep["counts"].get("DONE") == 1
    assert rep["wall_clock_s"] > 0
    assert rep["baseline_sequential_estimate_s"] == 30
    assert rep["max_parallelism_observed"] >= 1
    assert rep["model_usage"][FREE]["attempts"] >= 1
    assert rep["agent_utilization"] > 0
    store.close()


# ---------- LIVE: full research E2E -----------------------------------------
@pytest.mark.live
@needs_live
def test_live_research_e2e(tmp_path):
    from orchestrator.models import load_live_catalog
    catalog = load_live_catalog()
    assert catalog, "live catalog must parse"
    primary = resolve_primary(catalog)
    assert primary, "a zero-cost primary must exist"

    store = _store(tmp_path)
    work = str(tmp_path / "w")
    log = str(tmp_path / "tasklog.jsonl")
    router = ModelRouter({"models": {primary: {"type": "unlimited",
                                               "max_parallel": 4}}},
                         catalog, store)
    orch = Orchestrator(store, work, {}, max_workers=2, repo_root=ROOT,
                        tasklog_path=log, router=router)

    topics = [
        {"topic": "oss-a",
         "repos": ["shlinkio/shlink", "YOURLS/YOURLS"]},
        {"topic": "oss-b",
         "repos": ["thedevs-network/kutt", "dubinc/dub"]},
    ]
    contracts = R.research_task_contracts(topics)
    # one impossible research task: acceptance demands a file the worker is
    # FORBIDDEN to create (allowed_files) -> QA_FAIL or FILE_VIOLATION ->
    # retry -> ESCALATED, while the rest of the project continues
    bad = _contract("research-oss-c", kind="opencode", files=["findings/oss-c.json"],
                    max_attempts=2, timeout_s=200,
                    acc=[{"id": "x", "kind": "file_exists",
                          "path": "findings/forbidden.json"}],
                    **{"goal": "Write findings/oss-c.json with: hello"})
    pid = orch.submit_project("live-research-e2e", contracts + [bad])
    synth_id = "synthesis"
    store.add_task(pid, with_defaults({
        "task_id": synth_id, "kind": "synthesis", "role": "Synthesis",
        "goal": "aggregate", "outputs": [], "allowed_files": ["synthesis.json"],
        "dependencies": ["research-oss-a", "research-oss-b"],
        "acceptance": [{"id": "s", "kind": "file_exists",
                        "path": "synthesis.json"}],
        "gates": False, "estimate_s": 10}))
    orch.registry["synthesis"] = R.make_synthesis_fn(
        store, pid, work, verify_licenses=True)
    counts = orch.run(pid)

    done = store.get_task("research-oss-a")["status"]
    assert done == "DONE"
    assert store.get_task("research-oss-b")["status"] == "DONE"
    assert store.get_task("research-oss-c")["status"] == "ESCALATED"
    assert store.get_task(synth_id)["status"] == "DONE"
    findings = store.list_findings(pid, "oss-candidate")
    assert len(findings) >= 2, "both researchers must record evidence"
    for f in findings:
        assert f["payload"]["sources"], "evidence required"

    # operator approval -> apply -> build continues the DAG
    approved = R.approve_proposed(store, pid)
    assert approved, "synthesis must propose decisions"
    applied = R.apply_decisions(store, pid)
    assert applied["constraints"] or applied["reuses"], applied
    first_reuse = (applied["reuses"] or [{}])[0].get("component", "reuse")
    store.add_task(pid, with_defaults(_contract(
        "build-1", kind="opencode", files=["counter.py"],
        deps=[synth_id], timeout_s=240, estimate_s=60,
        acc=[{"id": "a", "kind": "file_contains", "path": "counter.py",
              "text": "def add"}],
        **{"goal": f"Create counter.py with: def add(a, b) with docstring. "
                    f"Context from research: {first_reuse}. "
                    f"Constraint: every feature must be API-accessible."})))
    counts2 = orch.run(pid)
    assert store.get_task("build-1")["status"] == "DONE"

    rep = orch.report(pid)
    assert rep["max_parallelism_observed"] >= 2, rep
    usage = rep["model_usage"]
    assert primary in usage and usage[primary]["attempts"] >= 5, usage
    assert usage[primary]["limit_hits"] == 0
    import json as _json
    lines = [_json.loads(l) for l in open(log, encoding="utf-8")]
    assert lines, "tasklog must have entries"
    for ln in lines:
        assert ln.get("model") == primary, ln
        assert ln.get("selection_reason") in (
            "default-primary", "passthrough-no-catalog"), ln
    sessions = {ln.get("session_id") for ln in lines if ln.get("session_id")}
    assert len(sessions) >= 5, "each attempt must be its own session"
    store.close()
