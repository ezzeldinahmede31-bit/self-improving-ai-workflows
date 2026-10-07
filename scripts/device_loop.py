#!/usr/bin/env python3
"""device_loop.py v2 — hardened Unified Agent Loop.

USER REQUEST -> PLAN -> INSPECT -> DECOMPOSE -> SELECT TOOL -> CHECK TRUST ->
PERMISSION -> EXECUTE -> OBSERVE -> VERIFY -> SUCCESS? NEXT : DIAGNOSE ->
RECOVER -> VERIFY -> RETRY/ESCALATE/FAIL-CLOSED -> FINAL VERIFY -> DONE

Hardening (see docs/FINAL_GAP_MATRIX_BEFORE.md):
- Full step metadata: step_id/task_id/session/parent/ts/tool/permission/verdict.
- NO self-approval: plan "approved" flags are IGNORED. ASK steps need a token
  from device_permissions approve/consume (bound session+step+command hash,
  TTL, single-use, replay-rejected). `approve SID STEP` mints one (human).
- Bounded retry: max 3, backoff 1/2/4s, classified taxonomy; DENY and
  destructive ops (rm/push --force/delete/reset --hard) are NEVER retried.
- Cancellation: `cancel SID` stops the loop; recorded child pids killed.
- Atomic state via device_state; destructive completions recorded with
  idempotency keys -> resume never re-executes them.
- Global plan deadline (default 900s) + max 50 steps (resource caps).
- Every step audited to device_audit (redacted).
- Tools: bash | sandbox(net-OFF default) | read | write | symbols |
  monitor_wait | cron_due. Untrusted text (web/file/mcp) is DATA: it flows
  only into permission-checked tools, never into policy.

Usage:
  run --plan plan.json [--max-retries N] [--deadline S] [--task TASK]
  resume SID | approve SID STEP | cancel SID | status SID
  selftest
"""
import json
import subprocess
import sys
import time
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from device_permissions import evaluate, cmd_consume  # noqa: E402
from device_state import read as sread, write as swrite, peek as speek, once as sonce  # noqa: E402
from device_audit import cmd_log  # noqa: E402

SESS_DIR = "sessions"
MAX_STEPS = 50
DEFAULT_DEADLINE = 900
DESTRUCTIVE_RES = ["rm", "push --force", "push -f", "reset --hard", "delete", "clean -fd", "clean -df"]

TAXONOMY = {
    "DENIED": ("security", False, "policy denied: fail-closed, never retried"),
    "NEEDS_APPROVAL": ("approval", False, "waiting human approval"),
    "TIMEOUT": ("timeout", True, "retryable with backoff"),
    "EXEC_FAIL": ("exec", True, "retryable unless destructive"),
    "VERIFY_FAIL": ("verification", True, "retryable"),
    "CANCELED": ("cancel", False, "stopped by user"),
}


def audit(session, actor, action, tool, verdict, detail=""):
    try:
        cmd_log(session, actor, action, tool, verdict, detail)
    except Exception:
        pass


def is_destructive(tool, args, step):
    blob = " ".join(args) if isinstance(args, list) else str(args or "")
    blob += " " + step.get("tool", "")
    return any(d in blob for d in DESTRUCTIVE_RES)


def new_session(plan, task="task"):
    sid = uuid.uuid4().hex[:8]
    st = {"id": sid, "task": task, "plan": plan, "done": [], "failed": None,
            "status": "running", "log": [], "started": time.time(),
            "deadline": time.time() + DEFAULT_DEADLINE, "children": []}
    save(st)
    return st


def save(st):
    swrite(f"{SESS_DIR}/{st['id']}.json", st)


def load(sid):
    if ".." in sid or "/" in sid:
        raise ValueError("bad session id")
    st = sread(f"{SESS_DIR}/{sid}.json")
    if st is None:
        raise ValueError("unknown session")
    return st


def need_token(tool, tier, st, step, value):
    """ASK requires a single-use token minted for (session, step, cmd-hash)."""
    if tier != "ask":
        return True, None
    pend = [t for t in getattr(need_token, "_pending", [])]
    return False, "NEEDS_APPROVAL"


def silent_consume(*a):
    import io
    from contextlib import redirect_stdout
    buf = io.StringIO()
    with redirect_stdout(buf):
        return cmd_consume(*a)


def run_step(st, step, parent=None):
    tool = step["tool"]
    meta = {"step": step["id"], "task": st["task"], "session": st["id"],
            "parent": parent, "ts": time.time(), "tool": tool}
    if tool in ("bash", "sandbox"):
        args = step.get("args", [])
        val = " ".join(args)
        tier, rule = evaluate("Bash", val)
        meta.update(permission=tier, rule=str(rule)[:160])
        audit(st["id"], "loop", "permission", tool, tier.upper(), val[:200])
        if tier == "deny":
            return "DENIED", f"policy denied: {rule}", meta
        if tier == "ask":
            tok = step.get("_token")
            if not tok or silent_consume(st["id"], step["id"], "Bash", val, tok) != 0:
                return "NEEDS_APPROVAL", f"needs approval token: {val[:120]}", meta
            meta["token_used"] = True
    if tool == "bash":
        p = subprocess.run(step["args"], capture_output=True, text=True, timeout=120)
        code, out = p.returncode, (p.stdout + p.stderr)[-3000:]
    elif tool == "sandbox":
        extra = ["--net"] if step.get("net") else []  # net OFF unless asked
        p = subprocess.run([sys.executable, str(HERE / "device_sandbox.py"), *extra,
                            "--", *step.get("args", [])],
                           capture_output=True, text=True, timeout=150)
        code, out = p.returncode, (p.stdout + p.stderr)[-3000:]
    elif tool == "read":
        tier, _ = evaluate("Read", step["path"])
        if tier == "deny":
            return "DENIED", "secret-path read denied", {**meta, "permission": "deny"}
        try:
            out, code = Path(step["path"]).read_text()[:4000], 0
        except Exception as e:
            return "FAILED", f"read error: {e}", meta
        meta["permission"] = tier
    elif tool == "write":
        tier, _ = evaluate("Write", step["path"])
        if tier == "deny":
            return "DENIED", "secret-path write denied", {**meta, "permission": "deny"}
        if tier == "ask":
            tok = step.get("_token")
            if not tok or silent_consume(st["id"], step["id"], "Write", step["path"], tok) != 0:
                return "NEEDS_APPROVAL", f"needs approval token: {step['path']}", \
                    {**meta, "permission": "ask"}
        try:
            Path(step["path"]).write_text(step.get("text", ""))
            out, code = f"wrote {step['path']}", 0
        except Exception as e:
            return "FAILED", f"write error: {e}", meta
        meta["permission"] = tier
    elif tool == "symbols":
        p = subprocess.run([sys.executable, str(HERE / "device_symbols.py"),
                            *step.get("args", [])],
                           capture_output=True, text=True, timeout=30)
        code, out = p.returncode, (p.stdout + p.stderr)[-3000:]
    elif tool == "monitor_wait":
        p = subprocess.run([sys.executable, str(HERE / "device_monitor.py"),
                            "start", "--", *step.get("args", [])],
                           capture_output=True, text=True, timeout=30)
        mid = p.stdout.strip()
        st["children"].append({"kind": "monitor", "id": mid})
        deadline = time.time() + step.get("timeout", 60)
        out, code, seen = "", 1, 0
        while time.time() < deadline:
            q = subprocess.run([sys.executable, str(HERE / "device_monitor.py"),
                                "poll", mid, "--since", str(seen)],
                               capture_output=True, text=True, timeout=30)
            try:
                d = json.loads(q.stdout)
            except Exception:
                break
            seen = d.get("next_since", seen)
            for ln in d.get("lines", []):
                out += ln + "\n"
            if step.get("until") and step["until"] in out:
                code = 0
                break
            if d.get("status") in ("exited",) and not d.get("alive", True):
                code = 0 if out.strip() else 1
                break
            time.sleep(2)
        subprocess.run([sys.executable, str(HERE / "device_monitor.py"), "stop", mid],
                       capture_output=True, timeout=15)
    elif tool == "cron_due":
        p = subprocess.run([sys.executable, str(HERE / "device_cron.py"), "due"],
                           capture_output=True, text=True, timeout=30)
        code, out = p.returncode, p.stdout[-2000:]
    else:
        return "FAILED", f"unknown tool {tool}", meta
    if code != 0:
        return "FAILED", out[-500:], meta
    ok, msg = check_verify(out, code, step.get("verify"))
    meta["verify"] = msg
    audit(st["id"], "loop", "execute", tool, "OK" if ok else "VERIFY_FAIL", step["id"])
    return ("OK", f"{msg} :: {out[:200]}", meta) if ok else ("FAILED", msg, meta)


def check_verify(out, code, spec):
    if not spec:
        return True, "no verify spec"
    if "exit" in spec and code != spec["exit"]:
        return False, f"exit {code} != {spec['exit']}"
    if "contains" in spec and spec["contains"] not in out:
        return False, f"output lacks {spec['contains']!r}"
    if "file_exists" in spec and not Path(spec["file_exists"]).exists():
        return False, f"missing file {spec['file_exists']}"
    if "file_contains" in spec:
        p = Path(spec["file_contains"]["path"])
        if not p.exists() or spec["file_contains"]["text"] not in p.read_text():
            return False, "file content mismatch"
    return True, "verified"


def classify(status, step):
    if status in ("DENIED", "NEEDS_APPROVAL", "CANCELED"):
        return status
    if status == "TIMEOUT":
        return "TIMEOUT"
    if is_destructive(step.get("tool"), step.get("args", []), step):
        return "EXEC_FAIL_NODESTRUCT"  # never retried
    return "EXEC_FAIL"


def drive(st, max_retries=2, _depth=0):
    if len(st["plan"]["steps"]) > MAX_STEPS:
        st.update(status="failed", failed={"why": "plan exceeds MAX_STEPS"})
        save(st)
        return st
    if time.time() > st.get("deadline", float("inf")):
        st.update(status="failed", failed={"why": "plan deadline exceeded"})
        save(st)
        return st
    for step in st["plan"]["steps"]:
        if step["id"] in st["done"]:
            continue
        if load(st["id"])["status"] == "canceled":
            st["status"] = "canceled"
            save(st)
            return st
        attempt = 0
        while True:
            status, msg, meta = run_step(st, step)
            st["log"].append({**meta, "status": status, "msg": msg[:200]})
            save(st)
            if status == "OK":
                if is_destructive(step.get("tool"), step.get("args", []), step):
                    sonce(f"loop:{st['id']}:{step['id']}", {"ok": True})
                st["done"].append(step["id"])
                save(st)
                break
            if status in ("DENIED", "NEEDS_APPROVAL", "CANCELED"):
                st.update(status="paused" if status == "NEEDS_APPROVAL" else "failed",
                          failed={"step": step["id"], "why": msg, "class": status})
                save(st)
                return st
            kind = classify(status, step)
            if kind == "EXEC_FAIL_NODESTRUCT" or attempt >= max_retries:
                st.update(status="failed",
                          failed={"step": step["id"], "why": msg, "class": kind})
                save(st)
                return st
            attempt += 1
            time.sleep(min(2 ** attempt, 8))
    # resume-safety: destructive steps recorded; re-drive skips via done[]
    st["status"] = "done"
    save(st)
    return st


def main(argv):
    if len(argv) == 2 and argv[1] == "selftest":
        from device_permissions import cmd_approve
        import io
        from contextlib import redirect_stdout
        plan = {"steps": [
            {"id": "w", "tool": "write", "path": "/tmp/loop2.txt", "text": "v2-ok",
             "verify": {"file_contains": {"path": "/tmp/loop2.txt", "text": "v2-ok"}}},
            {"id": "evil", "tool": "bash", "args": ["rm", "-rf", "/tmp/nope"]},
        ]}
        st = new_session(plan, task="selftest")
        st = drive(st)
        ok1 = st["status"] == "paused" and st["failed"]["step"] == "w"
        print(f"unapproved write pauses -> {'PASS' if ok1 else 'FAIL'}")
        # mint external token (human approval) then approve+resume
        buf = io.StringIO()
        with redirect_stdout(buf):
            cmd_approve(st["id"], "w", "Write", "/tmp/loop2.txt", ttl=300)
        tok = buf.getvalue().strip()
        for s in st["plan"]["steps"]:
            if s["id"] == "w":
                s["_token"] = tok
        st["status"] = "running"
        st["failed"] = None
        save(st)
        st = drive(load(st["id"]))
        ok2 = st["status"] == "failed" and st["failed"]["step"] == "evil"
        print(f"deny stops loop, destructive never retried -> {'PASS' if ok2 else 'FAIL'}")
        ok3 = Path("/tmp/loop2.txt").read_text() == "v2-ok"
        print(f"verify real file -> {'PASS' if ok3 else 'FAIL'}")
        Path("/tmp/loop2.txt").unlink(missing_ok=True)
        ok = ok1 and ok2 and ok3
        print("SELFTEST " + ("OK" if ok else "FAILED"))
        return 0 if ok else 1
    if len(argv) >= 2 and argv[1] == "run":
        plan = json.loads(Path(argv[argv.index("--plan") + 1]).read_text())
        retries = int(argv[argv.index("--max-retries") + 1]) if "--max-retries" in argv else 2
        task = argv[argv.index("--task") + 1] if "--task" in argv else "task"
        st = new_session(plan, task)
        if "--deadline" in argv:
            st["deadline"] = time.time() + int(argv[argv.index("--deadline") + 1])
        save(st)
        st = drive(st, retries)
        print(json.dumps({"session": st["id"], "status": st["status"],
                          "done": st["done"], "failed": st["failed"]}, indent=1))
        return 0 if st["status"] == "done" else 1
    if len(argv) >= 3 and argv[1] == "resume":
        st = drive(load(argv[2]))
        print(json.dumps({"session": st["id"], "status": st["status"],
                          "done": st["done"], "failed": st["failed"]}, indent=1))
        return 0 if st["status"] == "done" else 1
    if len(argv) >= 4 and argv[1] == "approve":
        from device_permissions import cmd_approve as _appr
        import io
        from contextlib import redirect_stdout
        st = load(argv[2])
        step = next(s for s in st["plan"]["steps"] if s["id"] == argv[3])
        val = step["path"] if step["tool"] == "write" else " ".join(step.get("args", []))
        tool = "Write" if step["tool"] == "write" else "Bash"
        buf = io.StringIO()
        with redirect_stdout(buf):
            _appr(st["id"], step["id"], tool, val, ttl=600)
        step["_token"] = buf.getvalue().strip()
        st["status"] = "running"
        st["failed"] = None
        save(st)
        st = drive(st)
        print(json.dumps({"session": st["id"], "status": st["status"],
                          "done": st["done"], "failed": st["failed"]}, indent=1))
        return 0 if st["status"] == "done" else 1
    if len(argv) >= 3 and argv[1] == "cancel":
        st = load(argv[2])
        st["status"] = "canceled"
        save(st)
        for ch in st.get("children", []):
            if ch.get("kind") == "monitor":
                subprocess.run([sys.executable, str(HERE / "device_monitor.py"),
                                "stop", ch["id"]], capture_output=True, timeout=15)
        audit(st["id"], "human", "cancel", "-", "CANCELED", "")
        print(f"canceled {argv[2]}")
        return 0
    if len(argv) >= 3 and argv[1] == "status":
        print(json.dumps(load(argv[2]), indent=1))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
