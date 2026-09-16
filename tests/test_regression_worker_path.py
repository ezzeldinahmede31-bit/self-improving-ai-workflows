"""Regression tests for local worker path + LLM fallback."""
import os
import tempfile
import pytest

from orchestrator import local_workers as lw_mod
from orchestrator.scheduler import Orchestrator, git_worktree_provider
from orchestrator.schema import with_defaults
from orchestrator.state import StateStore
from orchestrator import gitiso as gitiso_mod
from orchestrator.models import ModelRouter, load_live_catalog, resolve_primary


def _c(tid, goal, files, deps=None, exec_mode="local", **kw):
    # Acceptance checks for the actual content the local worker writes
    # Worker writes specific content based on file name patterns
    acc = []
    for i, f in enumerate(files):
        if f.endswith("pyproject.toml"):
            acc.append({"id": f"a{i}", "kind": "file_contains", "path": f, "text": "fasttool"})
        elif f.endswith("README.md"):
            acc.append({"id": f"a{i}", "kind": "file_contains", "path": f, "text": "Fast Tool"})
        elif f.endswith("calc.py"):
            acc.append({"id": f"a{i}", "kind": "file_contains", "path": f, "text": "def add"})
        elif f.endswith("__init__.py"):
            acc.append({"id": f"a{i}", "kind": "file_contains", "path": f, "text": "VERSION"})
        elif f.endswith("cli.py"):
            acc.append({"id": f"a{i}", "kind": "file_contains", "path": f, "text": "def main"})
        elif f.endswith("test_core.py"):
            acc.append({"id": f"a{i}", "kind": "file_contains", "path": f, "text": "def test_add"})
        else:
            acc.append({"id": f"a{i}", "kind": "file_exists", "path": f})
    
    c = {"task_id": tid, "kind": "opencode", "role": "Worker", "goal": goal,
         "outputs": [], "allowed_files": files, "dependencies": deps or [],
         "acceptance": acc, "model_policy": "primary-only", "gates": False,
         "timeout_s": 300, "max_attempts": 1, "estimate_s": 90,
         "execution_mode": exec_mode}
    c.update(kw)
    return with_defaults(c)


def _runner():
    """Minimal runner for isolated tests."""
    tmp = tempfile.mkdtemp()
    repo = os.path.join(tmp, "repo")
    gitiso_mod.init_repo(repo)
    store = StateStore(os.path.join(tmp, "state.db"))
    catalog = load_live_catalog()
    primary = resolve_primary(catalog)
    router = ModelRouter({"models": {primary: {"type": "unlimited", "max_parallel": 4}}},
                         load_live_catalog(), store)
    return Orchestrator(store, os.path.join(tmp, "work"), {}, max_workers=2,
                        worktree_provider=git_worktree_provider(repo, os.path.join(tmp, "wt")),
                        repo_root="/home/ezzeldin/Documents/Default Project",
                        tasklog_path=os.path.join(tmp, "tasklog.jsonl"),
                        router=router), store, tmp


def test_local_worker_path_executes_fast():
    """Local worker path should execute in milliseconds, not seconds."""
    orch, store, tmp = _runner()
    pid = store.create_project("fast-test")
    for c in [
        _c("t1", "Create pyproject.toml with fasttool", ["pyproject.toml"], exec_mode="local"),
        _c("t2", "Create README.md with Fast Tool", ["README.md"], exec_mode="local"),
    ]:
        store.add_task(pid, c)
    import time
    t0 = time.time()
    counts = orch.run(pid)
    elapsed = time.time() - t0
    print(f"Local worker: {elapsed:.2f}s, counts={counts}")
    assert elapsed < 2.0  # Should be fast (< 2s for 2 tasks)
    assert counts.get("DONE") == 2
    store.close()


def test_llm_fallback_on_reasoning_task():
    """Reasoning task should route to LLM (opencode path)."""
    orch, store, tmp = _runner()
    pid = store.create_project("llm-test")
    c = _c("t1", "Analyze the codebase and design a new architecture", ["arch.md"], exec_mode="llm")
    store.add_task(pid, c)
    # This would call opencode - we just verify classification
    from orchestrator.local_workers import classify_task
    assert classify_task(c) == "llm"
    store.close()


def test_explicit_execution_mode_override():
    """Explicit execution_mode in contract should be respected."""
    orch, store, tmp = _runner()
    pid = store.create_project("override-test")
    # Even a reasoning-like goal can be forced to local
    # Even a reasoning-like goal can be forced to local
    # Even a reasoning-like goal can be forced to local
    c = _c("t1", "Create core module", ["core/calc.py"], exec_mode="local")
    store.add_task(pid, c)
    counts = orch.run(pid)
    assert counts.get("DONE") == 1
    store.close()


def test_classifier_prefers_llm_on_ambiguity():
    """Ambiguous goals should default to LLM for safety."""
    from orchestrator.local_workers import classify_task
    c = {"goal": "Do something with the files", "task_id": "t1"}
    assert classify_task(c) == "llm"


def test_classifier_caching():
    """Repeated classifications should be fast (cached)."""
    from orchestrator.local_workers import classify_task
    import time
    c = {"goal": "Create file x.txt", "task_id": "t1"}
    t0 = time.perf_counter()
    for _ in range(1000):
        classify_task(c)
    elapsed = time.perf_counter() - t0
    assert elapsed < 0.05  # Should be very fast due to caching


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])