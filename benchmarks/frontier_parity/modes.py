"""Four comparison modes for the frontier-parity matrix (harness v1.0.0).

A. RAW_MUSE ......... Muse Spark, task prompt only, no skills, no repair.
B. CURRENT_ROUTER .... Muse Spark + fixed router block (v1) only.
C. SUPERSYSTEM ....... Muse Spark + router block + deterministic grade/repair loop (<=2 repairs).
D. FABLE ............. Claude Fable 5.1, variant same_capability (= A's prompt) or best_practical.

Execution vehicle: disposable `opencode run -m <model> --format json` sessions
(same pattern as orchestrator/opencode_worker.py). No mocks, no fixtures that
fake model output, no silent substitution: unknown models and sealed tasks are
REFUSED. Paid model (Fable 5.1) runs only with paid_ok=True and within budget.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import random
import shutil
import subprocess
import tempfile
import time

HARNESS_VERSION = "1.0.0"

MUSE_FREE = "opencode/muse-spark-1.3-contributor-free"
FABLE_51 = "opencode/claude-fable-5-1"
ALLOWLIST = {MUSE_FREE, FABLE_51}

RESULT_FILE = "RESULT.json"

# Machine-readable result channel (E2): when the contract asks for it, the
# agent writes {"output": "<exact artifact>"} to RESULT.json in the workdir.
# Chat narration may say anything; the FILE is graded. Unavailable natively
# in `opencode run`, so this deterministic adapter provides the separation.
RESULT_CONTRACT_V1 = (
    "# Machine result channel (v1): write the file RESULT.json in the working "
    "directory containing exactly {\"output\": \"<your complete answer and nothing else>\"} "
    "as the SOLE content of that file (valid JSON object, one string field named output). "
    "Your chat reply may say anything; ONLY RESULT.json is graded. If you do not write "
    "a valid RESULT.json, your chat reply is graded instead."
)

ROUTER_BLOCK_V1 = (
    "# Router guidance (v1, fixed for reproducibility)\n"
    "- Solve the task directly and completely; do not ask clarifying questions.\n"
    "- Follow the reply-format instruction exactly (ONLY the requested artifact).\n"
    "- For code: define exactly the requested function(s); no extra I/O.\n"
    "- For plans/data: verify every constraint before replying.\n"
    "- Do not modify, create, or delete files unless the task explicitly names them.\n"
)

CRITIC_BLOCK_V1 = (
    "# Verification discipline (v1)\n"
    "- Before replying, re-check your answer against every stated requirement.\n"
    "- If execution feedback shows a failure, fix ONLY the failing behavior.\n"
)


class Refused(Exception):
    """Raised when a run must not proceed (sealed task, unknown model, budget)."""


def prompt_hash(prompt: str) -> str:
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:16]


def build_prompt(mode: str, task: dict, variant: str = "same_capability",
                 repair_note: str = "") -> str:
    if task.get("held_out") or not task.get("prompt"):
        raise Refused(f"sealed/held-out task {task.get('id')}: will not run")
    base = task["prompt"]
    if mode == "A":
        p = base
    elif mode == "B":
        p = ROUTER_BLOCK_V1 + "\n" + base
    elif mode == "C":
        p = ROUTER_BLOCK_V1 + "\n" + CRITIC_BLOCK_V1 + "\n" + base
    elif mode == "D":
        if variant not in ("same_capability", "best_practical"):
            raise Refused(f"unknown variant {variant}")
        p = base  # pilot: identical prompt; difference is the model itself
    elif mode == "R":
        # RESULT-channel mode (E2): same task prompt + machine-channel
        # contract; free-tier Muse. Narration allowed in chat; only the
        # file is graded.
        p = base + "\n\n" + RESULT_CONTRACT_V1
    else:
        raise Refused(f"unknown mode {mode}")
    if repair_note:
        p += ("\n\n# Execution feedback (your previous reply failed mechanically):\n"
              + repair_note + "\nFix ONLY the failing behavior. Reply with ONLY the corrected artifact.")
    return p


def model_for(mode: str) -> str:
    if mode in ("A", "B", "C", "R"):
        return MUSE_FREE
    if mode == "D":
        return FABLE_51
    raise Refused(f"unknown mode {mode}")


def make_t01_fixtures(workdir: str) -> int:
    """Deterministic CSV fixtures (seeded rng v1). Returns the expected total."""
    rng = random.Random(20261009)
    total = 0
    rows = {"sales_q1.csv": 12, "sales_q2.csv": 15, "sales_q3.csv": 10}
    for fname, n in rows.items():
        lines = ["id,amount"]
        for i in range(n):
            v = rng.randint(5, 500)
            total += v
            lines.append(f"{i + 1},{v}")
        with open(os.path.join(workdir, fname), "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")
    return total


def _extract_text_events(raw: str) -> tuple[list[str], int, list[str], dict, list[str]]:
    """Parse `opencode run --format json` event stream.

    Returns (texts, tool_uses, errors, usage_candidate, telemetry_keys_seen).
    usage_candidate holds any numeric token-ish fields found (else {}).
    """
    texts: list[str] = []
    tool_uses = 0
    errors: list[str] = []
    usage: dict = {}
    keys_seen: list[str] = []
    coerced = False
    if isinstance(raw, (bytes, bytearray)):
        raw = bytes(raw).decode("utf-8", "replace")
        coerced = True
    for line in raw.splitlines():
        if isinstance(line, (bytes, bytearray)):
            line = bytes(line).decode("utf-8", "replace")
            coerced = True
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if not isinstance(ev, dict):
            continue
        for k in ev.keys():
            if k not in keys_seen:
                keys_seen.append(str(k))
        t = ev.get("type")
        if t == "text":
            txt = ((ev.get("part") or {}) or {}).get("text") or ""
            if txt:
                texts.append(txt)
        elif t == "tool_use":
            tool_uses += 1
        elif t in ("error", "step_error"):
            errors.append(str(ev.get("error", t)))
        # opportunistic usage capture: any nested usage/tokens dict
        stack = [ev]
        while stack:
            cur = stack.pop()
            if isinstance(cur, dict):
                for k, v in cur.items():
                    kl = str(k).lower()
                    if isinstance(v, (int, float)) and any(
                            s in kl for s in ("inputtokens", "outputtokens", "input_tokens",
                                             "output_tokens", "cachedtokens", "cache_read",
                                             "reasoningtokens")):
                        usage[str(k)] = v
                    elif isinstance(v, (dict, list)):
                        stack.append(v)
            elif isinstance(cur, list):
                stack.extend(cur)
    if coerced and "stream_coerced_bytes" not in keys_seen:
        keys_seen.append("stream_coerced_bytes")
    return texts, tool_uses, errors, usage, keys_seen


def setup_workdir(task: dict) -> tuple[str, dict]:
    """Create isolated workdir + write deterministic fixtures.

    Returns (workdir, fixture_ctx). Supports legacy v1 T01 and v2 `fixture`
    specs ({builder, seed, ...}). Fixture files are task input, never answers.
    """
    import sys as _sys
    _sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
    workdir = tempfile.mkdtemp(prefix="fp_")
    ctx: dict = {}
    if task.get("needs_workdir_fixtures"):
        ctx["fixture_total"] = make_t01_fixtures(workdir)
    spec = task.get("fixture")
    if spec:
        from fixtures import build_fixtures as _build
        files, fctx = _build(spec)
        for name, content in files.items():
            safe = os.path.basename(name)
            with open(os.path.join(workdir, safe), "w", encoding="utf-8") as fh:
                fh.write(content)
        ctx.update(fctx)
    # task-level grader params (cases/keys/edges...) OVERWRITE fixture ctx:
    # same key in both means the task author pins the check (e.g. W-tasks
    # pin keys=[headline,...] over the fixture's default keys). Fixture-only
    # keys (expected/schedule/facts/...) survive untouched.
    if isinstance(task.get("grader"), dict):
        for k, v in task["grader"].items():
            if k != "kind":
                ctx[k] = v
    return workdir, ctx


def read_result_channel(files: dict) -> tuple[str, str]:
    """Deterministic machine-channel reader over a workdir snapshot.

    Returns (status, content):
      absent               — no RESULT.json written; grade the chat text.
      valid                — parsed object with string field `output`.
      malformed:<reason>   — present but unusable (not JSON / not an object /
                             output missing or not a string). Fail closed at
                             grade time: chat is graded instead AND the status
                             is recorded, never silently dropped.
    """
    if RESULT_FILE not in (files or {}):
        return "absent", ""
    raw = files[RESULT_FILE]
    try:
        doc = json.loads(raw)
    except ValueError as exc:
        return f"malformed:not-json:{exc}", ""
    if not isinstance(doc, dict):
        return "malformed:not-an-object", ""
    if "output" not in doc:
        return "malformed:missing-output-field", ""
    if not isinstance(doc["output"], str):
        return "malformed:output-not-a-string", ""
    return "valid", doc["output"]


def classify_outcome(rec: dict) -> str:
    """Six-way outcome taxonomy (deterministic, audit-friendly).

    PASS | VALUE_ONLY | TIMEOUT | NO_OUTPUT | VALUE_WRONG | ERROR.
    Timeouts and infra errors can never read as success: PASS requires ok.
    """
    if rec.get("ok"):
        return "PASS"
    if rec.get("rc") == 124:
        return "TIMEOUT"
    if rec.get("rc") not in (0, None):
        return "ERROR"
    if not (rec.get("raw_text") or "").strip() and rec.get("channel", "chat") == "chat":
        return "NO_OUTPUT"
    if rec.get("value_ok"):
        return "VALUE_ONLY"
    return "VALUE_WRONG"


def snapshot_workdir(workdir: str, cap_bytes: int = 20000) -> tuple[dict, bool]:
    """Capture agent-written files for file-artifact grading. Capped."""
    files: dict = {}
    total = 0
    truncated = False
    for name in sorted(os.listdir(workdir)):
        p = os.path.join(workdir, name)
        if not os.path.isfile(p):
            continue
        try:
            with open(p, encoding="utf-8", errors="replace") as fh:
                content = fh.read(40000)
        except OSError:
            continue
        total += len(content.encode("utf-8", "ignore"))
        if total > cap_bytes:
            truncated = True
            break
        files[name] = content
    return files, truncated


def _needs_code_fence(task_id: str, task: dict | None) -> bool:
    if task_id in ("FP-C01", "FP-D01"):
        return True
    return bool(task and isinstance(task.get("grader"), dict)
                and task["grader"].get("kind") == "exec")


def _needs_brackets(task_id: str, task: dict | None, kind: str) -> bool:
    if task_id in ("FP-P01",) and kind == "[":
        return True
    if task_id in ("FP-X01",) and kind == "{":
        return True
    if task and isinstance(task.get("grader"), dict):
        gk = task["grader"].get("kind")
        if kind == "[" and gk in ("order", "schedule"):
            return True
        if kind == "{" and gk == "jsonfacts":
            return True
    return False


def normalize_output(task_id: str, raw: str, task: dict | None = None) -> tuple[str, bool]:
    """Mechanical normalization applied IDENTICALLY to every mode.

    - exec/code tasks: first ``` fenced block if present
    - order/schedule tasks: first [...] span if present
    - jsonfacts tasks: first {...} span if present
    Returns (normalized, changed_flag).
    """
    text = (raw or "").strip()
    if _needs_code_fence(task_id, task) and "```" in text:
        parts = text.split("```")
        for i in range(1, len(parts), 2):
            block = parts[i]
            lines = block.splitlines()
            if lines and lines[0].strip().lower().startswith("python"):
                lines = lines[1:]
            cand = "\n".join(lines).strip()
            if cand:
                return cand, True
    if _needs_brackets(task_id, task, "["):
        s, e = text.find("["), text.rfind("]")
        if 0 <= s < e:
            return text[s:e + 1].strip(), (s != 0 or e != len(text) - 1)
    if _needs_brackets(task_id, task, "{"):
        s, e = text.find("{"), text.rfind("}")
        if 0 <= s < e:
            return text[s:e + 1].strip(), (s != 0 or e != len(text) - 1)
    return text, False


def spawn_attempt(opencode_bin: str, model: str, prompt: str, workdir: str,
                   title: str, timeout_s: int) -> dict:
    """Spawn one disposable `opencode run` session; parse its event stream."""
    argv = [opencode_bin, "run", "--dir", workdir, "-m", model,
            "--format", "json", "--title", title, prompt]
    t0 = time.time()
    try:
        proc = subprocess.run(argv, capture_output=True, text=True, timeout=timeout_s)
        wall = round(time.time() - t0, 2)
        return {"raw_out": proc.stdout or "", "rc": proc.returncode,
                "err": (proc.stderr or "")[-1000:], "wall": wall}
    except subprocess.TimeoutExpired as exc:
        return {"raw_out": exc.stdout or "", "rc": 124,
                "err": "WORKER_TIMEOUT", "wall": round(time.time() - t0, 2)}


def run_once(task: dict, mode: str, variant: str = "same_capability",
             opencode_bin: str = "opencode", paid_ok: bool = False,
             catalog_snapshot: dict | None = None) -> dict:
    """Execute ONE task/mode attempt. Returns a provenance-rich record.

    Raises Refused for sealed tasks, unknown models, or unpaid Fable runs.
    """
    model = model_for(mode)
    if model not in ALLOWLIST:
        raise Refused(f"model {model} not in allowlist (no silent substitution)")
    if model == FABLE_51 and not paid_ok:
        raise Refused("Fable 5.1 is PAID: pass paid_ok=True with budget approval")
    prompt = build_prompt(mode, task, variant)
    workdir, fixture_ctx = setup_workdir(task)
    fixture_total = fixture_ctx.get("fixture_total")
    try:
        att = spawn_attempt(opencode_bin, model, prompt, workdir,
                            f"fp-{task['id']}-{mode}", task.get("timeout_s", 180))
        raw_out, rc, err, wall = att["raw_out"], att["rc"], att["err"], att["wall"]
        texts, tool_uses, errors, usage, keys_seen = _extract_text_events(raw_out)
        raw_text = "\n".join(texts).strip()
        files, files_truncated = snapshot_workdir(workdir)
        # Machine channel: a valid RESULT.json becomes the graded candidate
        # (narration separation). Anything else -> chat text, recorded.
        # Either candidate goes through the SAME mechanical normalization.
        chan_status, chan_content = read_result_channel(files)
        if chan_status == "valid":
            cand_raw, channel = chan_content.strip(), "result_json"
        else:
            cand_raw, channel = raw_text, "chat"
        normalized, changed = normalize_output(task["id"], cand_raw, task)
        measured = bool(usage)
        return {
            "task": task["id"], "mode": mode, "variant": variant,
            "model": model, "harness": HARNESS_VERSION,
            "prompt_sha": prompt_hash(prompt),
            "prompt_chars": len(prompt),
            "raw_text": raw_text[:4000], "output": normalized[:4000],
            "chat_output": normalize_output(task["id"], raw_text, task)[0][:4000],
            "channel": channel, "result_json_status": chan_status,
            "needed_normalization": changed,
            "rc": rc, "wall_s": wall, "tool_uses": tool_uses,
            "errors": errors[:5], "stderr_tail": err,
            "tokens": usage if measured else {},
            "token_status": "MEASURED" if measured else "UNMEASURED",
            "telemetry_keys_seen": keys_seen[:20],
            "fixture_total": fixture_total,
            "fixture_ctx": fixture_ctx,
            "files": files, "files_truncated": files_truncated,
            "catalog": catalog_snapshot or {},
            "workdir": workdir,  # caller cleans up after grading extras if needed
        }
    except Exception:
        shutil.rmtree(workdir, ignore_errors=True)
        raise
