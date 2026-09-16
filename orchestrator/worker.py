"""Worker execution: small context in, summary out.

The worker NEVER sees project history. It receives:
  - its Task Contract (goal, role, allowed files, acceptance)
  - explicit small inputs from dependencies (capped)
  - a working directory (worktree or plain dir)

Enforced: context byte budget, allowed-files subset, secret scan,
truncated summary. Anything oversized is refused, not silently trimmed.
"""
from __future__ import annotations
import hashlib
import json
import os
import re

SECRET_RE = re.compile(
    r"sk-[A-Za-z0-9]{8,}|xox[bap]-|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{8,}")
MAX_SUMMARY_CHARS = 2000


class ContextOverflow(Exception):
    pass


class OutputTooLarge(Exception):
    pass


def build_worker_context(contract: dict, provided: dict) -> tuple[dict, int]:
    ctx = {
        "task_id": contract["task_id"],
        "role": contract["role"],
        "goal": contract["goal"],
        "inputs": provided,
        "outputs": contract.get("outputs", []),
        "acceptance": contract.get("acceptance", []),
    }
    size = len(json.dumps(ctx).encode())
    limit = int(contract.get("context_limit_bytes", 8192))
    if size > limit:
        raise ContextOverflow(
            f"context {size}B exceeds limit {limit}B for {contract['task_id']}")
    return ctx, size


# Regenerable interpreter/test artifacts: never source, never violations.
IGNORED_DIRS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
IGNORED_SUFFIXES = (".pyc", ".pyo")


def snapshot_files(root: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for base, dirs, files in os.walk(root):
        if ".git" in dirs:
            dirs.remove(".git")
        for ign in list(dirs):
            if ign in IGNORED_DIRS:
                dirs.remove(ign)
        for f in files:
            if f.endswith(IGNORED_SUFFIXES):
                continue
            p = os.path.join(base, f)
            rel = os.path.relpath(p, root)
            try:
                with open(p, "rb") as fh:
                    out[rel] = hashlib.sha1(fh.read()).hexdigest()
            except OSError:
                continue
    return out


def scan_secrets(root: str, rel_paths: list[str]) -> list[str]:
    hits: list[str] = []
    for rel in rel_paths:
        p = os.path.join(root, rel)
        try:
            if os.path.getsize(p) > 1_000_000:
                continue
            with open(p, "r", errors="ignore") as fh:
                if SECRET_RE.search(fh.read()):
                    hits.append(rel)
        except OSError:
            continue
    return hits


def execute_task(contract: dict, work_dir: str, provided: dict,
                 task_fn) -> dict:
    """Run one task function under the contract. Returns a result dict."""
    tid = contract["task_id"]
    try:
        ctx, ctx_size = build_worker_context(contract, provided)
    except ContextOverflow as e:
        return {"ok": False, "reason": "CONTEXT_OVERFLOW", "detail": str(e),
                "task_id": tid}
    before = snapshot_files(work_dir)
    try:
        produced = task_fn(ctx, work_dir) or {}
    except Exception as e:  # noqa: BLE001 - worker errors are task failures
        return {"ok": False, "reason": "WORKER_ERROR",
                "detail": f"{type(e).__name__}: {e}", "task_id": tid}
    outputs = produced.get("outputs", {}) if isinstance(produced, dict) else {}
    notes = str(produced.get("notes", "")) if isinstance(produced, dict) else ""
    try:
        blob = json.dumps(outputs)
    except (TypeError, ValueError):
        return {"ok": False, "reason": "OUTPUT_NOT_JSON", "task_id": tid,
                "detail": "outputs must be JSON-serializable"}
    if len(blob.encode()) > int(contract.get("max_output_bytes", 4096)):
        return {"ok": False, "reason": "OUTPUT_TOO_LARGE", "task_id": tid,
                "detail": "pass bulk data via files in allowed_files, not outputs"}
    after = snapshot_files(work_dir)
    changed = sorted(r for r, h in after.items()
                     if before.get(r) != h)
    allowed = set(contract.get("allowed_files", []))
    violations = [r for r in changed if r not in allowed]
    if violations:
        return {"ok": False, "reason": "FILE_VIOLATION", "task_id": tid,
                "detail": f"wrote outside allowed_files: {violations}",
                "changed": changed}
    secret_hits = scan_secrets(work_dir, changed)
    if secret_hits:
        return {"ok": False, "reason": "SECRET_LEAK", "task_id": tid,
                "detail": f"possible secret in: {secret_hits}", "changed": changed}
    summary = {"task_id": tid, "role": contract.get("role"),
               "changed": changed, "outputs": outputs,
               "notes": notes[:MAX_SUMMARY_CHARS],
               "context_bytes": ctx_size}
    return {"ok": True, "task_id": tid, "summary": summary,
            "changed": changed, "outputs": outputs}
