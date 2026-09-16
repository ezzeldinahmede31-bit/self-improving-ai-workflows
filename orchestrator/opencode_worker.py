"""Real worker backend: one disposable `opencode run` session per task attempt.

Anti-bloat contract (the whole point of Phase 1):
  - Every attempt spawns a FRESH session (no --continue/--session). Sessions
    are disposable; all continuity lives in the StateStore, never in chat.
  - The prompt contains ONLY the Task Contract + small explicit inputs.
    Prompt byte budget enforced BEFORE spawning (no silent trimming).
  - Hard timeout kills the child process (no hanging sessions).
  - Bulk data travels via files in allowed_files; RESULT.json carries only
    small JSON outputs. Anything oversized is a task failure, not a stall.
"""
from __future__ import annotations
import json
import os
import subprocess
import time

from . import worker as worker_mod

import shutil as _shutil


def _resolve_bin() -> str:
    env = os.environ.get("OPENCODE_BIN")
    if env:
        return env
    found = _shutil.which("opencode")
    if found:
        return found
    home = os.path.join(os.path.expanduser("~"), ".opencode", "bin", "opencode")
    return home if os.path.exists(home) else "opencode"


OPENCODE_BIN = _resolve_bin()
DEFAULT_MODEL = "opencode/muse-spark-1.3-contributor-free"
RESULT_FILE = "RESULT.json"


def build_task_prompt(contract: dict, ctx: dict, work_dir: str) -> str:
    allowed = "\n".join(f"- {f}" for f in contract.get("allowed_files", []))
    acceptance = "\n".join(
        f"- [{a.get('id')}] {a.get('kind')}: {a.get('path', '')} "
        f"{a.get('text', a.get('field', ''))}".rstrip()
        for a in contract.get("acceptance", []))
    lines = [
        f"You are the {contract.get('role')} worker for task {contract.get('task_id')}.",
        f"Working directory: {work_dir}",
        f"GOAL: {contract.get('goal')}",
        f"INPUTS (small JSON from dependencies): {json.dumps(ctx.get('inputs', {}))}",
        "FILES YOU MAY CREATE/MODIFY (nothing else):",
        allowed or "(none)",
        "ACCEPTANCE (a separate checker verifies these; meet every one):",
        acceptance or "(none)",
        f"When done, write {RESULT_FILE} in the working directory as JSON "
        '{"notes": "<short summary>", "outputs": {<small JSON>}} and reply DONE.',
        "Rules: small focused changes only; no secrets/tokens in files; "
        "do not touch any file outside the allowed list.",
    ]
    return "\n".join(lines)


def parse_run_output(raw: str) -> dict:
    """Parse `--format json` event stream. Returns session/text/tool stats."""
    session_id = None
    texts: list[str] = []
    tool_uses = 0
    errors: list[str] = []
    for line in raw.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        session_id = session_id or ev.get("sessionID")
        if ev.get("type") == "text":
            t = ((ev.get("part") or {}).get("text")) or ""
            if t:
                texts.append(t)
        elif ev.get("type") == "tool_use":
            tool_uses += 1
        elif ev.get("type") in ("error", "step_error"):
            errors.append(str(ev.get("error", ev.get("type"))))
    return {"session_id": session_id, "texts": texts,
            "tool_uses": tool_uses, "errors": errors}


def read_result_file(work_dir: str) -> dict:
    p = os.path.join(work_dir, RESULT_FILE)
    try:
        with open(p, "r", errors="ignore") as fh:
            data = json.load(fh)
        if isinstance(data, dict):
            return data
    except (OSError, ValueError):
        pass
    return {}


def run_opencode_task(contract: dict, work_dir: str, provided: dict,
                      model: str | None = None,
                      _argv_override: list[str] | None = None,
                      spawn_hook=None) -> dict:
    """Spawn one disposable opencode session for this attempt.

    Returns a process-level report; file/contract enforcement happens in
    execute_opencode_task below. spawn_hook(proc) is an operability hook
    (monitoring, tests) called right after spawn with the Popen object.
    """
    tid = contract["task_id"]
    timeout_s = int(contract.get("timeout_s", 120))
    try:
        ctx, ctx_size = worker_mod.build_worker_context(contract, provided)
    except worker_mod.ContextOverflow as e:
        return {"ok": False, "stage": "context", "task_id": tid,
                "reason": "CONTEXT_OVERFLOW", "detail": str(e)}
    prompt = build_task_prompt(contract, ctx, work_dir)
    prompt_bytes = len(prompt.encode())
    prompt_limit = int(contract.get("prompt_limit_bytes", 6144))
    if prompt_bytes > prompt_limit:
        return {"ok": False, "stage": "context", "task_id": tid,
                "reason": "CONTEXT_OVERFLOW",
                "detail": f"prompt {prompt_bytes}B > limit {prompt_limit}B"}
    title = f"orch-{tid}"
    if _argv_override is not None:
        argv = list(_argv_override)
    else:
        argv = [OPENCODE_BIN, "run", "--dir", work_dir,
                "-m", model or contract.get("model") or DEFAULT_MODEL,
                "--format", "json", "--title", title, prompt]
    t0 = time.time()
    try:
        proc = subprocess.Popen(argv, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True)
        if spawn_hook is not None:
            try:
                spawn_hook(proc)
            except Exception:  # noqa: BLE001 - hook must never break runs
                pass
        try:
            out, err = proc.communicate(timeout=timeout_s)
            rc = proc.returncode
        except subprocess.TimeoutExpired:
            proc.kill()
            out, err = proc.communicate()
            parsed = parse_run_output(out or "")
            return {"ok": False, "stage": "run", "task_id": tid,
                    "reason": "WORKER_TIMEOUT",
                    "detail": f"killed after {timeout_s}s",
                    "session_id": parsed.get("session_id"),
                    "wall_s": round(time.time() - t0, 2),
                    "prompt_bytes": prompt_bytes, "context_bytes": ctx_size}
        wall = time.time() - t0
        parsed = parse_run_output(out or "")
        if rc != 0 and rc < 0:
            reason = "WORKER_KILLED"
        else:
            reason = "OK" if rc == 0 else "WORKER_NONZERO"
        return {"ok": rc == 0, "stage": "run", "task_id": tid,
                "reason": reason,
                "detail": (err or "")[-1000:],
                "session_id": parsed["session_id"], "wall_s": round(wall, 2),
                "texts": parsed["texts"][-3:], "tool_uses": parsed["tool_uses"],
                "prompt_bytes": prompt_bytes, "context_bytes": ctx_size,
                "pid": proc.pid}
    except OSError as e:
        return {"ok": False, "stage": "run", "task_id": tid,
                "reason": "SPAWN_FAILED", "detail": str(e)[:500],
                "session_id": None, "wall_s": round(time.time() - t0, 2),
                "prompt_bytes": prompt_bytes, "context_bytes": ctx_size}


def execute_opencode_task(contract: dict, work_dir: str, provided: dict,
                          model: str | None = None,
                          _argv_override: list[str] | None = None,
                          spawn_hook=None) -> dict:
    """Full attempt: spawn + enforce contract. Same result shape as MVP worker."""
    tid = contract["task_id"]
    before = worker_mod.snapshot_files(work_dir)
    # RESULT.json itself is harness-owned, not agent output: hide it from diff
    before.pop(RESULT_FILE, None)
    rep = run_opencode_task(contract, work_dir, provided, model,
                            _argv_override=_argv_override,
                            spawn_hook=spawn_hook)
    if not rep["ok"] and rep.get("stage") == "context":
        return {"ok": False, "reason": rep["reason"], "task_id": tid,
                "detail": rep.get("detail", "")}
    if not rep["ok"]:
        reason = rep.get("reason", "")
        if reason not in ("WORKER_TIMEOUT", "WORKER_KILLED"):
            reason = "WORKER_ERROR"
        return {"ok": False, "reason": reason, "task_id": tid,
                "detail": rep.get("detail", ""),
                "session_id": rep.get("session_id")}
    produced = read_result_file(work_dir)
    outputs = produced.get("outputs", {}) if isinstance(produced, dict) else {}
    notes = str(produced.get("notes", "")) if isinstance(produced, dict) else ""
    try:
        blob = json.dumps(outputs)
    except (TypeError, ValueError):
        return {"ok": False, "reason": "OUTPUT_NOT_JSON", "task_id": tid,
                "detail": "RESULT.json outputs must be JSON-serializable",
                "session_id": rep.get("session_id")}
    if len(blob.encode()) > int(contract.get("max_output_bytes", 4096)):
        return {"ok": False, "reason": "OUTPUT_TOO_LARGE", "task_id": tid,
                "detail": "pass bulk data via files, not RESULT.json outputs",
                "session_id": rep.get("session_id")}
    after = worker_mod.snapshot_files(work_dir)
    after.pop(RESULT_FILE, None)
    changed = sorted(r for r, h in after.items() if before.get(r) != h)
    allowed = set(contract.get("allowed_files", []))
    violations = [r for r in changed if r not in allowed]
    if violations:
        return {"ok": False, "reason": "FILE_VIOLATION", "task_id": tid,
                "detail": f"wrote outside allowed_files: {violations}",
                "changed": changed, "session_id": rep.get("session_id")}
    secret_hits = worker_mod.scan_secrets(work_dir, changed)
    if secret_hits:
        return {"ok": False, "reason": "SECRET_LEAK", "task_id": tid,
                "detail": f"possible secret in: {secret_hits}",
                "changed": changed, "session_id": rep.get("session_id")}
    summary = {"task_id": tid, "role": contract.get("role"),
               "changed": changed, "outputs": outputs,
               "notes": notes[:worker_mod.MAX_SUMMARY_CHARS],
               "context_bytes": rep.get("context_bytes"),
               "prompt_bytes": rep.get("prompt_bytes"),
               "session_id": rep.get("session_id"),
               "wall_s": rep.get("wall_s"),
               "tool_uses": rep.get("tool_uses")}
    return {"ok": True, "task_id": tid, "summary": summary,
            "changed": changed, "outputs": outputs,
            "session_id": rep.get("session_id")}
