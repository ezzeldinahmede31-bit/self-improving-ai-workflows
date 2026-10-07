#!/usr/bin/env python3
"""device_cron.py v2 — hardened session-scoped scheduler.

Fixes vs v1: add() permission-gates the command; ints validated positive;
cap 100 tasks; unique ids (collision-checked); atomic state; STATE path
overridable via DEVICE_CRON_STATE (selftest no longer wipes prod); ack only
fires due tasks; del requires existing id.

Usage: add --in S|--every S -- cmd... | list | due | ack ID | del ID | selftest
"""
import json
import os
import sys
import time
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from device_permissions import evaluate  # noqa: E402
from device_state import read as sread, write as swrite  # noqa: E402

NAME = os.environ.get("DEVICE_CRON_STATE", "cron/tasks.json")
MAX_TASKS = 100


def load():
    return sread(NAME) or {"tasks": []}


def save(s):
    swrite(NAME, s)


def cmd_add(args):
    every = delay = 0
    try:
        if "--every" in args:
            every = int(args[args.index("--every") + 1])
        if "--in" in args:
            delay = int(args[args.index("--in") + 1])
    except (ValueError, IndexError):
        print("bad --every/--in value", file=sys.stderr)
        return 2
    if every < 0 or delay < 0:
        print("negative schedule rejected", file=sys.stderr)
        return 2
    if "--" not in args:
        print("need -- <command...>", file=sys.stderr)
        return 2
    cmd = args[args.index("--") + 1:]
    if not cmd:
        print("empty command", file=sys.stderr)
        return 2
    tier, rule = evaluate("Bash", " ".join(cmd))
    if tier == "deny":
        print(f"DENIED by policy: {rule}", file=sys.stderr)
        return 20
    if tier == "ask":
        print(f"ASK by policy (needs human ack to arm): {rule}", file=sys.stderr)
    s = load()
    if len(s["tasks"]) >= MAX_TASKS:
        print("task cap reached", file=sys.stderr)
        return 2
    ids = {t["id"] for t in s["tasks"]}
    tid = uuid.uuid4().hex[:8]
    while tid in ids:
        tid = uuid.uuid4().hex[:8]
    s["tasks"].append({"id": tid, "cmd": cmd,
                       "run_at": time.time() + (delay or every or 0),
                       "every_s": every, "created": time.time(),
                       "last_run": None, "runs": 0, "armed": tier})
    save(s)
    print(tid)
    return 0


def main(argv):
    if len(argv) == 2 and argv[1] == "selftest":
        import subprocess
        # isolated namespace: reset it first (never touches prod state)
        from device_state import write as _w
        _w("cron/selftest-tasks.json", {"tasks": []})
        env = dict(os.environ, DEVICE_CRON_STATE="cron/selftest-tasks.json")
        run = lambda *a: subprocess.run(
            [sys.executable, __file__, *a], capture_output=True, text=True, env=env)
        r = run("add", "--in", "-5", "--", "echo", "hi")
        ok1 = r.returncode != 0
        print(f"negative rejected -> {'PASS' if ok1 else 'FAIL'}")
        r = run("add", "--in", "0", "--", "rm", "-rf", "/tmp/x")
        ok2 = r.returncode == 20
        print(f"denied command refused -> {'PASS' if ok2 else 'FAIL'}")
        r = run("add", "--in", "0", "--", "echo", "hi")
        tid = r.stdout.strip()
        due = json.loads(run("due").stdout)
        ok3 = len(due) == 1 and due[0]["id"] == tid
        print(f"add+due -> {'PASS' if ok3 else 'FAIL'}")
        run("ack", tid)
        ok4 = json.loads(run("due").stdout) == []
        print(f"ack one-shot removes -> {'PASS' if ok4 else 'FAIL'}")
        r = run("ack", "deadbeef")
        ok5 = r.returncode != 0
        print(f"ack unknown rejected -> {'PASS' if ok5 else 'FAIL'}")
        ok = ok1 and ok2 and ok3 and ok4 and ok5
        print("SELFTEST " + ("OK" if ok else "FAILED"))
        return 0 if ok else 1
    if len(argv) >= 2 and argv[1] == "add":
        return cmd_add(argv[2:])
    if len(argv) >= 2 and argv[1] == "list":
        for t in load()["tasks"]:
            print(f"{t['id']}  every={t['every_s']}s  runs={t['runs']}  {' '.join(t['cmd'])}")
        return 0
    if len(argv) >= 2 and argv[1] == "due":
        now = time.time()
        print(json.dumps([t for t in load()["tasks"] if t["run_at"] <= now], indent=1))
        return 0
    if len(argv) >= 3 and argv[1] == "ack":
        s = load()
        for t in s["tasks"]:
            if t["id"] == argv[2]:
                if t["run_at"] > time.time():
                    print("not due yet", file=sys.stderr)
                    return 2
                t["last_run"] = time.time()
                t["runs"] += 1
                if t["every_s"]:
                    t["run_at"] = time.time() + t["every_s"]
                else:
                    s["tasks"] = [x for x in s["tasks"] if x["id"] != argv[2]]
                save(s)
                print(f"acked {argv[2]}")
                return 0
        print(f"unknown task {argv[2]}", file=sys.stderr)
        return 1
    if len(argv) >= 3 and argv[1] == "del":
        s = load()
        if argv[2] not in {t["id"] for t in s["tasks"]}:
            print(f"unknown task {argv[2]}", file=sys.stderr)
            return 1
        s["tasks"] = [t for t in s["tasks"] if t["id"] != argv[2]]
        save(s)
        print(f"deleted {argv[2]}")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
