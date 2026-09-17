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


def _extra_flags(skills_manifest: str | None,
                 schema_cache: str | None) -> list[str]:
    """Skill + schema evidence flags. Paths that do not exist are skipped so
    a missing manifest/cache degrades to the legacy verdict-only run instead
    of a hard CLI error."""
    extra: list[str] = []
    if skills_manifest and os.path.isfile(skills_manifest):
        extra += ["--skills-loaded", skills_manifest]
    if schema_cache and os.path.isfile(schema_cache):
        extra += ["--schema-cache", schema_cache]
    return extra


def run_gates_on_file(path: str, repo_root: str,
                      timeout_s: int = GATE_TIMEOUT_S,
                      skills_manifest: str | None = None,
                      schema_cache: str | None = None) -> dict:
    try:
        proc = subprocess.run(
            [*GATES_BIN, *GATES_FLAGS,
             *_extra_flags(skills_manifest, schema_cache), path],
            cwd=repo_root, capture_output=True, text=True,
            timeout=timeout_s)
    except subprocess.TimeoutExpired:
        return {"path": path, "verdict": "GATE_TIMEOUT",
                "reason": f"gates exceeded {timeout_s}s"}
    out = (proc.stdout or "") + (proc.stderr or "")
    verdict, reason = _parse_verdict(out)
    return {"path": path, "verdict": verdict, "reason": reason,
            "rc": proc.returncode}


def gate_changed_files(work_dir: str, changed: list[str], repo_root: str,
                       timeout_s: int = GATE_TIMEOUT_S,
                       skills_manifest: str | None = None,
                       schema_cache: str | None = None) -> dict:
    """Gate every changed file. Returns {passed, verdicts}."""
    verdicts = [run_gates_on_file(os.path.join(work_dir, rel), repo_root,
                                  timeout_s, skills_manifest, schema_cache)
                for rel in changed]
    bad = [v for v in verdicts if v["verdict"] != "READY_FOR_DEPLOYMENT"]
    return {"passed": not bad, "verdicts": verdicts, "failed": bad}
