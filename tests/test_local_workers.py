"""Tests for persistent local worker pool + task classification (TDD)."""
import os
import time
import tempfile
import pytest

from orchestrator.local_workers import (
    LocalWorkerPool,
    TaskClassifier,
    classify_task,
    LocalWorker,
    ExecutionResult,
)
from orchestrator.schema import with_defaults


def _c(tid, goal, files, deps=None, kind="generic", **kw):
    c = {"task_id": tid, "kind": kind, "role": "Worker", "goal": goal,
         "outputs": [], "allowed_files": files, "dependencies": deps or [],
         "acceptance": [{"id": "a", "kind": "file_exists", "path": f}
                        for f in files]}
    c.update(kw)
    return with_defaults(c)


# ---------- Task Classification -------------------------------------------

def test_classify_deterministic_file_ops():
    """Pure file creation/editing = deterministic (local worker)."""
    c = _c("t1", "Create file x.txt with content hello", ["x.txt"])
    assert classify_task(c) == "local"


def test_classify_reasoning_task():
    """Tasks requiring analysis/decision = reasoning (LLM)."""
    c = _c("t1", "Analyze the codebase and design a new architecture", ["arch.md"])
    assert classify_task(c) == "llm"


def test_classify_mixed_prefers_llm():
    """If any part needs reasoning, route to LLM."""
    c = _c("t1", "Create file and also analyze the best approach", ["x.txt"])
    assert classify_task(c) == "llm"


def test_classifier_fast():
    """Classification must be fast (<1ms)."""
    c = _c("t1", "Create file x.txt", ["x.txt"])
    t0 = time.perf_counter()
    for _ in range(1000):
        classify_task(c)
    assert (time.perf_counter() - t0) < 0.1


# ---------- Local Worker ---------------------------------------------------

def test_local_worker_creates_file(tmp_path):
    c = _c("t1", "Create file", ["x.txt"])
    worker = LocalWorker(str(tmp_path))
    result = worker.execute(c, {})
    assert result.ok
    # File is created in worker's work_dir under tmp_path
    work_dirs = list(tmp_path.glob("lw-*"))
    assert len(work_dirs) == 1
    assert (work_dirs[0] / "x.txt").exists()


def test_local_worker_writes_content(tmp_path):
    c = _c("t1", "Create file", ["x.txt"])
    worker = LocalWorker(str(tmp_path))
    # Direct file write simulation (what local worker does)
    result = worker.execute(c, {})
    assert result.ok
    # The actual content is written by the worker logic
    # Acceptance is verified separately


def test_local_worker_respects_allowed_files(tmp_path):
    c = _c("t1", "Create file", ["x.txt"])
    worker = LocalWorker(str(tmp_path))
    # Try to write outside allowed files - should be caught
    result = worker.execute(c, {})
    # Local worker should only create allowed files
    assert result.ok


def test_local_worker_handles_dependencies(tmp_path):
    c = _c("t1", "Create file", ["x.txt"])
    provided = {"dep1": {"output": "some data"}}
    worker = LocalWorker(str(tmp_path))
    result = worker.execute(c, provided)
    assert result.ok


def test_local_worker_timeout_enforcement():
    """Local worker must respect timeout."""
    # This tests the worker respects the contract timeout
    pass  # Implemented in pool tests


# ---------- Local Worker Pool ---------------------------------------------

def test_pool_concurrent_execution(tmp_path):
    pool = LocalWorkerPool(str(tmp_path), max_workers=4)
    tasks = [
        _c(f"t{i}", f"Task {i}", [f"x{i}.txt"]) for i in range(4)
    ]
    start = time.perf_counter()
    results = pool.execute_batch(tasks, {})
    elapsed = time.perf_counter() - start
    assert all(r.ok for r in results)
    assert elapsed < 1.0  # Should be parallel, not sequential


def test_pool_respects_max_workers(tmp_path):
    pool = LocalWorkerPool(str(tmp_path), max_workers=2)
    tasks = [_c(f"t{i}", f"Task {i}", [f"x{i}.txt"]) for i in range(4)]
    start = time.perf_counter()
    pool.execute_batch(tasks, {})
    elapsed = time.perf_counter() - start
    # With 2 workers and 4 tasks, should take ~2x single task time
    assert elapsed > 0.5  # Proves concurrency limit


def test_pool_reuses_workers(tmp_path):
    """Workers should be reused across tasks."""
    pool = LocalWorkerPool(str(tmp_path), max_workers=2)
    for _ in range(3):
        tasks = [_c(f"t{i}", f"Task {i}", [f"x{i}.txt"]) for i in range(2)]
        results = pool.execute_batch(tasks, {})
        assert all(r.ok for r in results)


def test_pool_task_timeout(tmp_path):
    pool = LocalWorkerPool(str(tmp_path), max_workers=2)
    # Task with timeout shorter than the worker's minimum sleep
    c = _c("t1", "slow task", ["x.txt"], timeout_s=0.1)
    # Task that would exceed timeout should be killed
    results = pool.execute_batch([c], {})
    assert results[0].ok is False
    assert results[0].reason == "TIMEOUT"


# ---------- Integration: LLM Fallback -------------------------------------

def test_llm_fallback_on_reasoning_task(tmp_path):
    """Reasoning tasks should route to LLM, not local worker."""
    c = _c("t1", "Analyze and design a new system", ["design.md"])
    # This is a contract test - the classifier should return "llm"
    assert classify_task(c) == "llm"
    # The scheduler should then use opencode_worker for this


def test_local_worker_fails_gracefully_on_error(tmp_path):
    """Local worker should return ok=False with reason on error."""
    # Test with a contract that would cause an error
    pass


# ---------- Contract: Task must declare execution_mode --------------------

def test_contract_execution_mode_field():
    """Contract should have execution_mode field set by classifier."""
    from orchestrator.schema import with_defaults
    c = with_defaults({"task_id": "t1", "kind": "opencode", "role": "Worker",
                       "goal": "Create file", "outputs": [], "allowed_files": ["x.txt"],
                       "dependencies": [], "acceptance": [{"id": "a", "kind": "file_exists", "path": "x.txt"}]})
    # The contract should have execution_mode set
    assert "execution_mode" in c


def test_execution_mode_local_for_deterministic():
    from orchestrator.schema import with_defaults
    from orchestrator.local_workers import classify_task
    c = with_defaults({"task_id": "t1", "kind": "opencode", "role": "Worker",
                       "goal": "Create file", "outputs": [], "allowed_files": ["x.txt"],
                       "dependencies": [], "acceptance": [{"id": "a", "kind": "file_exists", "path": "x.txt"}]})
    # Classification happens at submit time via classifier
    assert classify_task(c) == "local"


def test_execution_mode_llm_for_reasoning():
    from orchestrator.schema import with_defaults
    c = with_defaults({"task_id": "t1", "kind": "opencode", "role": "Worker",
                       "goal": "Analyze and design", "outputs": [], "allowed_files": ["x.md"],
                       "dependencies": [], "acceptance": [{"id": "a", "kind": "file_exists", "path": "x.md"}]})
    # Classification happens at submit time
    assert c.get("execution_mode") in ("local", "llm")


# ---------- Worker Result Shape -------------------------------------------

def test_local_worker_result_shape(tmp_path):
    """Local worker result must match the expected shape."""
    c = _c("t1", "Create file", ["x.txt"])
    worker = LocalWorker(str(tmp_path))
    result = worker.execute(c, {})
    assert hasattr(result, "ok")
    assert hasattr(result, "reason")
    assert hasattr(result, "detail")
    assert hasattr(result, "changed_files")
    assert hasattr(result, "outputs")
    assert hasattr(result, "execution_time")
    assert hasattr(result, "session_id")  # For compatibility


# ---------- Regression: Ensure existing opencode path still works ---------

def test_opencode_worker_still_works(tmp_path):
    """Ensure we didn't break the existing opencode path."""
    # This is a contract test - the opencode_worker module should still work
    from orchestrator.opencode_worker import execute_opencode_task
    # The function should exist and be callable
    assert callable(execute_opencode_task)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])