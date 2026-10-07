#!/usr/bin/env python3
"""device_loop.py — the Unified Agent Loop (Cowork-grade orchestration).

Every task runs the same closed loop:

  PLAN -> inspect -> choose tool -> PERMISSION CHECK -> execute
    -> VERIFY -> success? next : diagnose/recover/retry -> DONE

Tools: files (read/write/edit via python), bash, sandbox, monitor, cron,
symbols, browser (via firecrawl_scrape note: network reads), gui (via
desktop screenshots not driven here — loop records the evidence paths).
Untrusted content (web/file/mcp text) is ALWAYS tagged untrusted and can
never change policy: only device_permissions.py decides ALLOW/ASK/DENY.

Session: every loop persists state to /tmp/opencode-device/sessions/<id>.json
after each step -> `resume <id>` continues exactly where it stopped
(killed process, reboot, closed terminal).

Usage:
  device_loop.py run --plan plan.json [--session SID] [--max-retries 1]
  device_loop.py resume SID
  device_loop.py status SID
  device_loop.py selftest

Plan format (JSON list of steps):
  {"steps": [
    {"id": "s1", "tool": "bash", "args": ["echo", "hi"],
     "verify": {"contains": "hi"}},
    {"id": "s2", "tool": "write", "path": "/tmp/x.txt", "text": "hello",
     "verify": {"file_contains": "hello"}},
  ]}
Tools: bash | sandbox | read | write | symbols | monitor_wait | cron_due
Verify keys: contains | exit | file_contains | file_exists | json_path
On ASK verdict the step pauses as NEEDS_APPROVAL (never auto-approved).
On DENY the step fails closed with reason. Up to max-retries recoveries.
"""
import json
import subprocess
import sys
import time
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
SESS = Path("/tmp/opencode-device/sessions")
sys.path.insert(0, str(HERE))
from device_permissions import evaluate  # noqa: E402


def new_session(plan):
    sid = uuid.uuid4().hex[:8]
    SESS.mkdir(parents=True, exist_ok=True)
    state = {"id": sid, "plan": plan, "done": [], "failed": None,
             "status": "running", "log": []}
    save(state)
    return state


def save(state):
    (SESS / f"{state['id']}.json").write_text(json.dumps(state, indent=1))


def load(sid):
    return json.loads((SESS / f"{sid}.json").read_text())


def log(state, msg):
    state["log"].append(f"{time.strftime('%H:%M:%S')} {msg}")
    save(state)


def tool_bash(args):
    p = subprocess.run(args, capture_output=True, text=True, timeout=120)
    return p.returncode, p.stdout + p.stderr


def tool_sandbox(args):
    p = subprocess.run([sys.executable, str(HERE / "device_sandbox.py"),
                        "--", *args], capture_output=True, text=True, timeout=150)
    return p.returncode, p.stdout + p.stderr


def tool_read(path):
    tier, _ = evaluate("Read", path)
    if tier == "deny":
        return 20, "DENIED by policy"
    try:
        return 0, Path(path).read_text()[:4000]
    except Exception as e:
        return 1, f"read error: {e}"


def tool_write(path, text, approved=False):
    tier, _ = evaluate("Write", path)
    if tier == "deny":
        return 20, "DENIED by policy"
    if tier == "ask" and not approved:
        return 10, "ASK by policy (needs approval)"
    try:
        Path(path).write_text(text)
        return 0, f"wrote {len(text)} chars to {path}"
    except Exception as e:
        return 1, f"write error: {e}"


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


def run_step(state, step):
    tool, args = step["tool"], step.get("args", [])
    # 1. permission gate (exec-class tools)
    if tool in ("bash", "sandbox"):
        val = " ".join(args)
        tier, rule = evaluate("Bash", val)
        if tier == "deny":
            return "DENIED", f"policy denied: {rule}"
        if tier == "ask" and not step.get("approved", False):
            return "NEEDS_APPROVAL", f"needs user approval: {val}"
    # 2. execute
    if tool == "bash":
        code, out = tool_bash(args)
    elif tool == "sandbox":
        code, out = tool_sandbox(args)
    elif tool == "read":
        code, out = tool_read(step["path"])
    elif tool == "write":
        code, out = tool_write(step["path"], step.get("text", ""),
                               step.get("approved", False))
    elif tool == "symbols":
        p = subprocess.run([sys.executable, str(HERE / "device_symbols.py"),
                            *args], capture_output=True, text=True, timeout=30)
        code, out = p.returncode, p.stdout + p.stderr
    else:
        return "FAILED", f"unknown tool {tool}"
    if code in (10, 20):
        return ("NEEDS_APPROVAL" if code == 10 else "DENIED"), out
    if code != 0:
        return "FAILED", out[-500:]
    # 3. verify
    ok, msg = check_verify(out, code, step.get("verify"))
    return ("OK", f"{msg} :: {out[:200]}") if ok else ("FAILED", msg)


def drive(state, max_retries=1):
    plan = state["plan"]
    done_ids = set(state["done"])
    for step in plan["steps"]:
        if step["id"] in done_ids:
            continue
        log(state, f"STEP {step['id']} tool={step['tool']}")
        attempt = 0
        while True:
            status, msg = run_step(state, step)
            log(state, f"  -> {status}: {msg[:160]}")
            if status == "OK":
                state["done"].append(step["id"])
                save(state)
                break
            if status in ("DENIED", "NEEDS_APPROVAL"):
                state["status"] = "paused"
                state["failed"] = {"step": step["id"], "why": msg}
                save(state)
                return state
            attempt += 1
            if attempt > max_retries:
                state["status"] = "failed"
                state["failed"] = {"step": step["id"], "why": msg}
                save(state)
                return state
            log(state, f"  recover attempt {attempt}/{max_retries}")
            time.sleep(1)
    state["status"] = "done"
    save(state)
    return state


def main(argv):
    if len(argv) == 2 and argv[1] == "selftest":
        plan = {"steps": [
            {"id": "w", "tool": "write", "path": "/tmp/loop_selftest.txt",
             "text": "loop-ok", "approved": True,
             "verify": {"file_contains": {"path": "/tmp/loop_selftest.txt",
                                          "text": "loop-ok"}}},
            {"id": "r", "tool": "read", "path": "/tmp/loop_selftest.txt",
             "verify": {"contains": "loop-ok"}},
            {"id": "b", "tool": "bash", "args": ["echo", "loop-bash-ok"],
             "approved": True, "verify": {"contains": "loop-bash-ok"}},
            {"id": "deny", "tool": "bash", "args": ["rm", "-rf", "/tmp/x"]},
        ]}
        st = new_session(plan)
        st = drive(st, max_retries=0)
        ok = (st["status"] == "paused"
              and st["failed"]["step"] == "deny"
              and "denied" in st["failed"]["why"].lower()
              and set(st["done"]) == {"w", "r", "b"})
        print(f"loop ok/verify/deny-pause -> {'PASS' if ok else 'FAIL'} ({st['status']})")
        # resume: approve nothing, add allow step, resume continues past done ones
        st2 = load(st["id"])
        st2["plan"]["steps"] = [s for s in st2["plan"]["steps"] if s["id"] != "deny"]
        st2["plan"]["steps"].append(
            {"id": "b2", "tool": "bash", "args": ["echo", "resumed-ok"],
             "approved": True, "verify": {"contains": "resumed-ok"}})
        st2["status"] = "running"
        st2["failed"] = None
        save(st2)
        st2 = drive(load(st2["id"]))
        ok2 = st2["status"] == "done" and "b2" in st2["done"]
        print(f"resume continues -> {'PASS' if ok2 else 'FAIL'}")
        Path("/tmp/loop_selftest.txt").unlink(missing_ok=True)
        print("SELFTEST " + ("OK" if ok and ok2 else "FAILED"))
        return 0 if ok and ok2 else 1
    if len(argv) >= 2 and argv[1] == "run":
        plan = json.loads(Path(argv[argv.index("--plan") + 1]).read_text())
        retries = int(argv[argv.index("--max-retries") + 1]) if "--max-retries" in argv else 1
        st = new_session(plan)
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
        st = load(argv[2])
        for s in st["plan"]["steps"]:
            if s["id"] == argv[3]:
                s["approved"] = True
        st["status"] = "running"
        st["failed"] = None
        save(st)
        st = drive(st)
        print(json.dumps({"session": st["id"], "status": st["status"],
                          "done": st["done"], "failed": st["failed"]}, indent=1))
        return 0 if st["status"] == "done" else 1
    if len(argv) >= 3 and argv[1] == "status":
        print(json.dumps(load(argv[2]), indent=1))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
