"""Demo project: diamond DAG (schema -> api -> {frontend, integration} -> e2e).

Run: venv/bin/python -m orchestrator.demo
Uses mock workers (plain functions). Proves: DAG levels, parallel fan-out,
lease/retry path (one flaky task), QA gates, summaries, dashboard render.
"""
from __future__ import annotations
import os
import tempfile
import time

from .dashboard import render_text, snapshot
from .scheduler import Orchestrator
from .state import StateStore

CALLS: dict[str, int] = {}


def _write(work_dir: str, name: str, content: str) -> None:
    with open(os.path.join(work_dir, name), "w") as fh:
        fh.write(content)


def fn_schema(ctx, work_dir):
    _write(work_dir, "schema.sql", "CREATE TABLE patients(id INT PRIMARY KEY);")
    return {"notes": "schema v1", "outputs": {"tables": ["patients"]}}


def fn_api(ctx, work_dir):
    assert ctx["inputs"]["db"]["tables"] == ["patients"]
    _write(work_dir, "api.py", "# patients API\nTABLES=['patients']\n")
    return {"notes": "api wired to schema", "outputs": {"routes": ["/patients"]}}


def fn_frontend(ctx, work_dir):
    _write(work_dir, "ui.html", "<html>patients</html>")
    return {"notes": "ui draft", "outputs": {}}


def fn_integration(ctx, work_dir):
    _write(work_dir, "contract.json", '{"routes": ["/patients"]}')
    return {"notes": "contract pinned", "outputs": {}}


def fn_flaky(ctx, work_dir):
    n = CALLS.get("flaky", 0)
    CALLS["flaky"] = n + 1
    if n == 0:
        raise RuntimeError("simulated first-attempt failure")
    _write(work_dir, "e2e.txt", "e2e PASS")
    return {"notes": "e2e green on retry", "outputs": {}}


def contract(tid, kind, role, files, deps, acceptance, **kw):
    c = {"task_id": tid, "kind": kind, "role": role, "goal": f"demo {tid}",
         "outputs": [], "allowed_files": files, "dependencies": deps,
         "acceptance": acceptance}
    c.update(kw)
    return c


def main() -> None:
    tmp = tempfile.mkdtemp(prefix="orch_demo_")
    store = StateStore(os.path.join(tmp, "state.db"))
    orch = Orchestrator(store, os.path.join(tmp, "work"),
                        {"schema": fn_schema, "api": fn_api,
                         "frontend": fn_frontend, "integration": fn_integration,
                         "flaky": fn_flaky},
                        max_workers=3)
    t0 = time.time()
    pid = orch.submit_project("demo-clinic", [
        contract("db", "schema", "Database Agent", ["schema.sql"], [],
                 [{"id": "a1", "kind": "file_contains", "path": "schema.sql",
                   "text": "CREATE TABLE"}]),
        contract("api", "api", "Backend Agent", ["api.py"], ["db"],
                 [{"id": "a1", "kind": "file_contains", "path": "api.py",
                   "text": "patients"}]),
        contract("fe", "frontend", "Frontend Agent", ["ui.html"], ["api"],
                 [{"id": "a1", "kind": "file_exists", "path": "ui.html"}]),
        contract("integ", "integration", "API Agent", ["contract.json"], ["api"],
                 [{"id": "a1", "kind": "file_contains", "path": "contract.json",
                   "text": "/patients"}]),
        contract("e2e", "flaky", "QA Agent", ["e2e.txt"], ["fe", "integ"],
                 [{"id": "a1", "kind": "file_contains", "path": "e2e.txt",
                   "text": "PASS"}]),
    ])
    counts = orch.run(pid)
    print(render_text(snapshot(store, pid)))
    print(f"wall={time.time()-t0:.2f}s counts={counts} tmp={tmp}")
    store.close()


if __name__ == "__main__":
    main()
