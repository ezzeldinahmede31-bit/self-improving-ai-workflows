"""Validation benchmark harness (measurement tooling, not a product feature).

Builds a real multi-module project (csvtoolkit) and runs it in three modes:
  A: sequential baseline (max_workers=1)
  B: DAG without safe-split (max_workers=N)
  C: full optimized (optimize_project + max_workers=N)
Same contracts + same acceptance criteria in all modes. Worktrees provide
real integration evidence. Metrics come from store events + tasklog only.
"""
from __future__ import annotations
import json
import os
import tempfile
import time

from . import gitiso as gitiso_mod
from . import splitter as splitter_mod
from .dashboard import snapshot
from .models import ModelRouter, load_live_catalog, resolve_primary
from .scheduler import Orchestrator, git_worktree_provider
from .schema import with_defaults
from .state import StateStore
from .tasklog import TaskLog

EST = 90


def _c(tid, role, goal, files, deps, markers, **kw):
    acc = [{"id": f"a{i}", "kind": "file_contains", "path": f, "text": m}
           for i, (f, m) in enumerate(markers)]
    c = {"task_id": tid, "kind": "opencode", "role": role, "goal": goal,
         "outputs": [], "allowed_files": files, "dependencies": deps,
         "acceptance": acc, "model_policy": "primary-only", "gates": True,
         "timeout_s": 300, "max_attempts": 2, "estimate_s": EST}
    c.update(kw)
    return with_defaults(c)


def build_csvtoolkit_contracts() -> list[dict]:
    return [
        _c("scaffold", "Architect",
           "Create pyproject.toml (project name csvtoolkit, version 0.1.0), "
           "toolkit/__init__.py containing TOOLKIT_VERSION = \"0.1.0\", and "
           "README.md containing the line: csvtoolkit sample inventory",
           ["pyproject.toml", "toolkit/__init__.py", "README.md"], [],
           [("pyproject.toml", "csvtoolkit"),
            ("toolkit/__init__.py", "TOOLKIT_VERSION"),
            ("README.md", "csvtoolkit sample inventory")]),
        _c("loader", "Backend",
           "Create toolkit/loader.py with docstrings: function load_rows(path) "
           "reading a CSV file into a list of dicts using the csv module, and "
           "function validate_rows(rows) returning True for non-empty input.",
           ["toolkit/loader.py"], ["scaffold"],
           [("toolkit/loader.py", "def load_rows"),
            ("toolkit/loader.py", "def validate_rows")]),
        _c("stats", "Backend",
           "Create toolkit/stats.py with docstrings: function word_count(rows, "
           "column) returning total word tally across rows, and function "
           "top_values(rows, column, n=5) returning the n most common values.",
           ["toolkit/stats.py"], ["scaffold"],
           [("toolkit/stats.py", "def word_count"),
            ("toolkit/stats.py", "def top_values")]),
        _c("filtermod", "Backend",
           "Create toolkit/filter.py with docstrings: function filter_rows(rows, "
           "column, value) keeping matching rows, and function drop_empty(rows) "
           "removing rows with any empty string field.",
           ["toolkit/filter.py"], ["scaffold"],
           [("toolkit/filter.py", "def filter_rows"),
            ("toolkit/filter.py", "def drop_empty")]),
        _c("reporter", "Backend",
           "Create toolkit/reporter.py with docstrings: import loader, stats, "
           "filter modules and define summarize(path, column) returning a dict "
           "with keys total, top, filtered.",
           ["toolkit/reporter.py"], ["stats", "filtermod"],
           [("toolkit/reporter.py", "def summarize")]),
        _c("cli", "Frontend",
           "Create toolkit/cli.py with docstrings: import reporter and define "
           "main(argv) printing the summary dict for a CSV path argument.",
           ["toolkit/cli.py"], ["reporter"],
           [("toolkit/cli.py", "def main")]),
        _c("tests", "QA",
           "Create tests/test_core.py with real asserts importing loader, "
           "stats, filter (small inline sample rows, no external files) "
           "containing the line: def test_core, and tests/test_report.py "
           "importing reporter and cli containing the line: def test_report.",
           ["tests/test_core.py", "tests/test_report.py"], ["cli"],
           [("tests/test_core.py", "def test_core"),
            ("tests/test_report.py", "def test_report")],
           splittable=True, split_by="files",
           file_groups=[["tests/test_core.py"], ["tests/test_report.py"]]),
    ]


def make_orch(tmp: str, max_workers: int, catalog, primary: str,
              registry_extra: dict | None = None):
    repo = os.path.join(tmp, "repo")
    gitiso_mod.init_repo(repo)
    store = StateStore(os.path.join(tmp, "state.db"))
    work = os.path.join(tmp, "work")
    wt_root = os.path.join(tmp, "wt")
    router = ModelRouter(
        {"models": {primary: {"type": "unlimited", "max_parallel": 8}}},
        catalog, store)
    orch = Orchestrator(store, work, registry_extra or {}, max_workers=max_workers,
                        worktree_provider=git_worktree_provider(repo, wt_root),
                        repo_root=os.path.normpath(os.path.join(
                            os.path.dirname(os.path.abspath(__file__)), "..")),
                        tasklog_path=os.path.join(tmp, "tasklog.jsonl"),
                        router=router)
    return orch, store, repo, tmp


def waiting_times(store: StateStore, project_id: str) -> dict:
    evs = store.project_events(project_id)
    done_at: dict[str, float] = {}
    wait: dict[str, float] = {}
    for e in evs:
        p, k = e["payload"], e["kind"]
        if k == "task_done":
            done_at[p.get("task_id")] = e["ts"]
        elif k == "task_started" and p.get("task_id") not in wait:
            deps = [t for t in store.list_tasks(project_id)
                    if t["task_id"] == p.get("task_id")]
            dep_ts = [done_at.get(d, 0) for t in deps
                      for d in t["contract"].get("dependencies", [])]
            wait[p.get("task_id")] = round(
                max(0.0, e["ts"] - max(dep_ts or [0])), 2)
    return wait


def collect(orch: Orchestrator, store: StateStore, project_id: str,
            tmp: str, split_report: dict | None = None) -> dict:
    rep = orch.report(project_id)
    log = TaskLog(os.path.join(tmp, "tasklog.jsonl")).read_all()
    qa_total = round(sum(float(l.get("qa_s") or 0) for l in log), 2)
    merge_total = round(sum(float(l.get("merge_s") or 0) for l in log), 2)
    sessions = sorted({l.get("session_id") for l in log if l.get("session_id")})
    retries = sum(1 for e in store.project_events(project_id)
                  if e["kind"] == "task_retry")
    conflicts = sum(1 for e in store.project_events(project_id)
                    if e["kind"] == "task_escalated" and
                    "CONFLICT" in str(e["payload"].get("reason", "")))
    rep.update({"qa_total_s": qa_total, "merge_total_s": merge_total,
                "sessions": sessions, "session_count": len(sessions),
                "retries": retries, "merge_conflicts": conflicts,
                "waiting_s": waiting_times(store, project_id),
                "attempts": log, "split_report": split_report})
    return rep


def run_mode(mode: str, max_workers: int, out_dir: str) -> dict:
    catalog = load_live_catalog()
    primary = resolve_primary(catalog)
    assert primary, "no primary resolved"
    tmp = tempfile.mkdtemp(prefix=f"bench_{mode}_")
    orch, store, repo, _ = make_orch(tmp, max_workers, catalog, primary)
    contracts = build_csvtoolkit_contracts()
    split_report = None
    if mode == "C":
        contracts, split_report = splitter_mod.optimize_project(contracts)
    pid = orch.submit_project(f"csvtoolkit-{mode}", contracts)
    t0 = time.time()
    counts = orch.run(pid)
    wall = round(time.time() - t0, 2)
    rep = collect(orch, store, pid, tmp)
    rep.update({"mode": mode, "max_workers": max_workers, "wall_s": wall,
                "primary": primary, "repo": repo, "tmp": tmp,
                "tasks_submitted": len(contracts)})
    path = os.path.join(out_dir, f"bench_{mode}.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(rep, fh, ensure_ascii=False, indent=1)
    store.close()
    return rep


def main(out_dir: str = "/tmp/opencode/bench_out", modes=("A", "B", "C")):
    os.makedirs(out_dir, exist_ok=True)
    workers = {"A": 1, "B": 4, "C": 4}
    for m in modes:
        print(f"=== MODE {m} ===", flush=True)
        rep = run_mode(m, workers[m], out_dir)
        print(f"mode={m} wall={rep['wall_s']}s counts={rep['counts']} "
              f"peak={rep['max_parallelism_observed']} "
              f"speedup_vs_est={rep['actual_speedup_vs_estimate']}", flush=True)
    return out_dir


if __name__ == "__main__":
    main()
