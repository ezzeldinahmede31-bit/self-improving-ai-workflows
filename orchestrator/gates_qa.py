"""Build-gates QA hook: every task's changed files must be READY_FOR_DEPLOYMENT.

Runs the project's own gates pipeline non-interactively
(--no-hitl --no-autofix --no-complaints --no-resolve --no-patterns
--no-attempt-guard --json) once per changed file. All files must be READY;
any other verdict blocks the merge. Verdicts are recorded in task details.
"""
from __future__ import annotations
import json
import os
import subprocess
import sys

GATES_BIN = [sys.executable, os.path.join("scripts", "build_gates_pipeline.py")]
GATES_FLAGS = ["--no-hitl", "--no-autofix", "--no-complaints", "--no-resolve",
               "--no-patterns", "--no-attempt-guard", "--json"]
GATE_TIMEOUT_S = 180


def _parse_verdict(raw: str) -> tuple[str, str]:
    try:
        doc = json.loads(raw[raw.index("{"):])
        return str(doc.get("verdict", "UNKNOWN")), str(doc.get("reason_code", ""))
    except (ValueError, AttributeError):
        return "UNKNOWN", (raw or "")[-500:]


def run_gates_on_file(path: str, repo_root: str,
                      timeout_s: int = GATE_TIMEOUT_S) -> dict:
    try:
        proc = subprocess.run([*GATES_BIN, *GATES_FLAGS, path], cwd=repo_root,
                              capture_output=True, text=True, timeout=timeout_s)
    except subprocess.TimeoutExpired:
        return {"path": path, "verdict": "GATE_TIMEOUT",
                "reason": f"gates exceeded {timeout_s}s"}
    out = (proc.stdout or "") + (proc.stderr or "")
    verdict, reason = _parse_verdict(out)
    return {"path": path, "verdict": verdict, "reason": reason,
            "rc": proc.returncode}


def gate_changed_files(work_dir: str, changed: list[str], repo_root: str,
                       timeout_s: int = GATE_TIMEOUT_S) -> dict:
    """Gate every changed file. Returns {passed, verdicts}."""
    verdicts = [run_gates_on_file(os.path.join(work_dir, rel), repo_root,
                                  timeout_s) for rel in changed]
    bad = [v for v in verdicts if v["verdict"] != "READY_FOR_DEPLOYMENT"]
    return {"passed": not bad, "verdicts": verdicts, "failed": bad}
