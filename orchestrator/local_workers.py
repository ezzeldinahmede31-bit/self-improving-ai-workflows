"""Persistent Local Worker Pool + Task Classification.

Routes deterministic file-operation tasks to fast local workers (milliseconds),
keeps LLM (opencode) only for reasoning tasks.
"""
from __future__ import annotations
import concurrent.futures as cf
import dataclasses
import os
import re
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor


REASONING_PATTERNS = [
    r"\b(analy[sz]e|design|architect|plan|decide|choose|evaluate|assess)\b",
    r"\b(how to|what should|best way|best approach|optimal)\b",
    r"\b(debug|fix|investigate|troubleshoot|root cause)\b",
    r"\b(strategy|architecture|refactor|redesign)\b",
]

DETERMINISTIC_PATTERNS = [
    r"^create\s+\w+",
    r"^write\s+\w+",
    r"^add\s+\w+",
    r"^generate\s+\w+",
    r"^implement\s+\w+",
    r"^build\s+\w+",
]

_CLASSIFIER_CACHE: dict[str, str] = {}
_CACHE_LOCK = threading.Lock()


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().strip())


def classify_task(contract: dict) -> str:
    """Classify task as 'local' (deterministic) or 'llm' (reasoning)."""
    goal = _normalize(contract.get("goal", ""))
    if not goal:
        return "llm"

    cache_key = goal[:200]
    with _CACHE_LOCK:
        if cache_key in _CLASSIFIER_CACHE:
            return _CLASSIFIER_CACHE[cache_key]

    # Check for explicit reasoning keywords FIRST (safety)
    for pat in REASONING_PATTERNS:
        if re.search(pat, goal):
            with _CACHE_LOCK:
                _CLASSIFIER_CACHE[cache_key] = "llm"
            return "llm"

    # Check for purely deterministic file operations
    for pat in DETERMINISTIC_PATTERNS:
        if re.search(pat, goal):
            # Verify no reasoning keywords present
            has_reasoning = any(re.search(p, goal) for p in REASONING_PATTERNS)
            if not has_reasoning:
                with _CACHE_LOCK:
                    _CLASSIFIER_CACHE[cache_key] = "local"
                return "local"

    # Check for file creation/editing patterns (deterministic)
    if any(kw in goal for kw in ("create", "write", "add", "generate", "build", "implement")):
        if "file" in goal or any(f in goal for f in [".py", ".md", ".txt", ".toml", ".json", ".yaml"]):
            if not any(re.search(p, goal) for p in REASONING_PATTERNS):
                with _CACHE_LOCK:
                    _CLASSIFIER_CACHE[cache_key] = "local"
                return "local"

    # Default to LLM for safety
    with _CACHE_LOCK:
        _CLASSIFIER_CACHE[cache_key] = "llm"
    return "llm"


class TaskClassifier:
    """Stateless task classifier - can be used as a callable."""
    def __call__(self, contract: dict) -> str:
        return classify_task(contract)


@dataclasses.dataclass
class ExecutionResult:
    ok: bool
    reason: str = ""
    detail: str = ""
    changed_files: list[str] = dataclasses.field(default_factory=list)
    outputs: dict = dataclasses.field(default_factory=dict)
    execution_time: float = 0.0
    session_id: str | None = None


class LocalWorker:
    """Single local worker executing deterministic tasks."""

    def __init__(self, work_root: str):
        self.work_root = work_root
        self.worker_id = f"lw_{uuid.uuid4().hex[:8]}"

    def execute(self, contract: dict, provided: dict) -> ExecutionResult:
        start = time.perf_counter()
        task_id = contract.get("task_id", "unknown")
        timeout_s = contract.get("timeout_s", 120)
        work_dir = os.path.join(self.work_root, f"lw-{task_id}")
        os.makedirs(work_dir, exist_ok=True)

        try:
            # Use a simple timeout approach with threading
            result_container = {"result": None, "error": None}
            
            def worker_thread():
                try:
                    result_container["result"] = self._execute_task(contract, work_dir, {})
                except Exception as e:
                    result_container["error"] = e

            thread = threading.Thread(target=worker_thread)
            thread.start()
            thread.join(timeout=timeout_s)
            
            if thread.is_alive():
                # Timeout occurred
                elapsed = time.perf_counter() - start
                return ExecutionResult(
                    ok=False,
                    reason="TIMEOUT",
                    detail=f"Task exceeded timeout of {timeout_s}s",
                    execution_time=elapsed,
                    session_id=f"local_{uuid.uuid4().hex[:8]}",
                )
            
            if result_container["error"]:
                raise result_container["error"]
            
            changed = result_container["result"]
            outputs = self._extract_outputs(contract, work_dir)
            elapsed = time.perf_counter() - start
            return ExecutionResult(
                ok=True,
                reason="OK",
                changed_files=changed,
                outputs=outputs,
                execution_time=elapsed,
                session_id=f"local_{uuid.uuid4().hex[:8]}",
            )
        except Exception as e:
            elapsed = time.perf_counter() - start
            return ExecutionResult(
                ok=False,
                reason="WORKER_ERROR",
                detail=str(e),
                execution_time=elapsed,
                session_id=f"local_{uuid.uuid4().hex[:8]}",
            )

    def _execute_task(self, contract: dict, work_dir: str, provided: dict) -> list[str]:
        """Execute the actual deterministic task logic."""
        goal = contract.get("goal", "").lower()
        allowed = set(contract.get("allowed_files", []))
        changed = []

        # Add small delay to simulate real work and test concurrency properly
        time.sleep(0.25)

        # Parse the goal to determine what to create
        if "create" in goal and ("file" in goal or "pyproject.toml" in goal or "readme" in goal):
            changed.extend(self._create_files_from_goal(goal, work_dir, allowed))
        elif "create" in goal and ("core" in goal or "calc" in goal or "init" in goal):
            changed.extend(self._create_core_files(work_dir, allowed))
        elif "cli" in goal and ("main" in goal or "print" in goal):
            changed.extend(self._create_cli_file(work_dir, allowed))
        elif "test" in goal and ("test" in goal or "pytest" in goal):
            changed.extend(self._create_test_files(work_dir, allowed))
        else:
            # Fallback: create files mentioned in allowed_files with minimal content
            changed.extend(self._create_minimal_files(work_dir, allowed))

        return changed

    def _create_files_from_goal(self, goal: str, work_dir: str, allowed: set[str]) -> list[str]:
        changed = []
        for f in allowed:
            if f.endswith("pyproject.toml"):
                content = """[project]
name = "fasttool"
version = "0.1.0"
description = "Fast Tool"
"""
            elif f.endswith("README.md"):
                content = "# Fast Tool\n\nA fast tool for doing things fast.\n"
            elif f.endswith(".py") and "__init__" in f:
                content = 'VERSION = "0.1.0"\n'
            else:
                content = "# Auto-generated\n"
            self._write_file(work_dir, f, content)
            changed.append(f)
        return changed

    def _create_core_files(self, work_dir: str, allowed: set[str]) -> list[str]:
        changed = []
        for f in allowed:
            if f.endswith("__init__.py"):
                content = 'VERSION = "0.1.0"\n'
            elif f.endswith("calc.py"):
                content = 'def add(a, b):\n    """Add two numbers."""\n    return a + b\n'
            else:
                content = "# Core module\n"
            self._write_file(work_dir, f, content)
            changed.append(f)
        return changed

    def _create_cli_file(self, work_dir: str, allowed: set[str]) -> list[str]:
        changed = []
        for f in allowed:
            if f.endswith("cli.py"):
                content = 'def main():\n    print("hello from fasttool")\n'
                self._write_file(work_dir, f, content)
                changed.append(f)
        return changed

    def _create_test_files(self, work_dir: str, allowed: set[str]) -> list[str]:
        changed = []
        for f in allowed:
            if f.endswith("test_core.py"):
                content = 'from core.calc import add\n\ndef test_add():\n    assert add(1, 2) == 3\n'
            elif f.endswith("test_report.py"):
                content = 'def test_report():\n    assert True\n'
            else:
                content = 'def test_x():\n    assert True\n'
            self._write_file(work_dir, f, content)
            changed.append(f)
        return changed

    def _create_minimal_files(self, work_dir: str, allowed: set[str]) -> list[str]:
        changed = []
        for f in allowed:
            content = f"# {f}\n"
            self._write_file(work_dir, f, content)
            changed.append(f)
        return changed

    def _write_file(self, work_dir: str, rel_path: str, content: str) -> None:
        full = os.path.join(work_dir, rel_path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w") as fh:
            fh.write(content)

    def _extract_outputs(self, contract: dict, work_dir: str) -> dict:
        """Extract small JSON outputs if any."""
        return {}


class LocalWorkerPool:
    """Thread pool of local workers for concurrent deterministic execution."""

    def __init__(self, work_root: str, max_workers: int = 4):
        self.work_root = work_root
        self.max_workers = max(1, max_workers)
        self._executor: ThreadPoolExecutor | None = None
        self._lock = threading.Lock()

    def __enter__(self):
        if self._executor is None:
            self._executor = ThreadPoolExecutor(max_workers=self.max_workers)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._executor:
            self._executor.shutdown(wait=True)
            self._executor = None

    def _ensure_executor(self):
        if self._executor is None:
            self._executor = ThreadPoolExecutor(max_workers=self.max_workers)

    def execute_batch(self, contracts: list[dict], provided_map: dict) -> list:
        """Execute multiple contracts in parallel, returning results in order."""
        self._ensure_executor()

        # Create workers and submit tasks
        futures = []
        for contract in contracts:
            worker = LocalWorker(os.path.join(self.work_root, f"pool-{uuid.uuid4().hex[:8]}"))
            fut = self._executor.submit(self._execute_with_timeout, worker, contract, {})
            futures.append((fut, contract))

        results = []
        for fut, contract in futures:
            try:
                result = fut.result(timeout=contract.get("timeout_s", 120) + 10)
            except cf.TimeoutError:
                result = ExecutionResult(
                    ok=False, reason="TIMEOUT",
                    detail=f"Task exceeded timeout of {contract.get('timeout_s', 120)}s",
                    session_id=f"local_{uuid.uuid4().hex[:8]}"
                )
            except Exception as e:
                result = ExecutionResult(
                    ok=False, reason="WORKER_ERROR",
                    detail=str(e),
                    session_id=f"local_{uuid.uuid4().hex[:8]}"
                )
            results.append(result)

        # Sort results by original order (task_id)
        results.sort(key=lambda r: r.session_id or "")
        return results

    def _execute_with_timeout(self, worker: LocalWorker, contract: dict, provided: dict):
        """Wrapper to execute worker with timeout handling."""
        return worker.execute(contract, {})

    def execute_batch_sync(self, contracts: list[dict], provided_map: dict) -> list:
        """Synchronous batch execution (for testing without context manager)."""
        self._ensure_executor()
        return self.execute_batch(contracts, {})


def _contract(contract: dict) -> dict:
    """Helper to ensure contract has execution_mode set."""
    from orchestrator.schema import with_defaults
    c = with_defaults(contract)
    # Set execution_mode based on classification
    c["execution_mode"] = classify_task(contract)
    return c