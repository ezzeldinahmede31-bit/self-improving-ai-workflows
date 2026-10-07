#!/usr/bin/env python3
"""device_cron.py — Claude-style CronCreate/CronList/CronDelete, project-local.

Tasks are session-scoped JSON (not system cron): id, prompt/command,
run_at (epoch), every_s (0 = one-shot), created, last_run, runs.
The agent (or a loop) calls `due` to list runnable tasks, executes them,
then calls `ack <id>` to stamp last_run.

State: /tmp/opencode-device/cron.json
Usage:
  device_cron.py add --in 60 -- echo hello      # one-shot in 60s
  device_cron.py add --every 3600 -- backup.sh  # recurring hourly
  device_cron.py list
  device_cron.py due                             # tasks ready to run now (JSON)
  device_cron.py ack <id>
  device_cron.py del <id>
  device_cron.py selftest
"""
import json
import sys
import time
import uuid
from pathlib import Path

STATE = Path("/tmp/opencode-device/cron.json")


def load():
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {"tasks": []}


def save(s):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(s, indent=1))


def cmd_add(args):
    s = load()
    every = 0
    delay = 0
    if "--every" in args:
        every = int(args[args.index("--every") + 1])
    if "--in" in args:
        delay = int(args[args.index("--in") + 1])
    i = args.index("--") if "--" in args else len(args)
    cmd = args[i + 1:]
    if not cmd:
        print("need -- <command...>", file=sys.stderr)
        return 2
    t = {"id": uuid.uuid4().hex[:8], "cmd": cmd,
         "run_at": time.time() + (delay or every or 0),
         "every_s": every, "created": time.time(), "last_run": None, "runs": 0}
    s["tasks"].append(t)
    save(s)
    print(t["id"])
    return 0


def cmd_list():
    for t in load()["tasks"]:
        print(f"{t['id']}  every={t['every_s']}s  run_at={t['run_at']:.0f}  "
              f"runs={t['runs']}  {' '.join(t['cmd'])}")
    return 0


def cmd_due():
    now = time.time()
    due = [t for t in load()["tasks"] if t["run_at"] <= now]
    print(json.dumps(due, indent=1))
    return 0


def cmd_ack(tid):
    s = load()
    for t in s["tasks"]:
        if t["id"] == tid:
            t["last_run"] = time.time()
            t["runs"] += 1
            if t["every_s"]:
                t["run_at"] = time.time() + t["every_s"]
            else:
                s["tasks"] = [x for x in s["tasks"] if x["id"] != tid]
            save(s)
            print(f"acked {tid}")
            return 0
    print(f"unknown task {tid}", file=sys.stderr)
    return 1


def main(argv):
    if len(argv) == 2 and argv[1] == "selftest":
        import subprocess
        if STATE.exists():
            STATE.unlink()
        r = subprocess.run([sys.executable, __file__, "add", "--in", "0",
                            "--", "echo", "hi"], capture_output=True, text=True)
        tid = r.stdout.strip()
        r = subprocess.run([sys.executable, __file__, "due"], capture_output=True,
                           text=True)
        due = json.loads(r.stdout)
        ok1 = len(due) == 1 and due[0]["id"] == tid
        print(f"add+due -> {'PASS' if ok1 else 'FAIL'} ({due})")
        r = subprocess.run([sys.executable, __file__, "ack", tid],
                           capture_output=True, text=True)
        r = subprocess.run([sys.executable, __file__, "due"], capture_output=True,
                           text=True)
        ok2 = json.loads(r.stdout) == []
        print(f"ack one-shot removes -> {'PASS' if ok2 else 'FAIL'}")
        r = subprocess.run([sys.executable, __file__, "add", "--every", "3600",
                            "--", "echo", "hourly"], capture_output=True, text=True)
        tid2 = r.stdout.strip()
        subprocess.run([sys.executable, __file__, "ack", tid2], capture_output=True)
        left = load()["tasks"]
        ok3 = len(left) == 1 and left[0]["runs"] == 1
        print(f"ack recurring reschedules -> {'PASS' if ok3 else 'FAIL'}")
        subprocess.run([sys.executable, __file__, "del", tid2], capture_output=True)
        ok = ok1 and ok2 and ok3
        print("SELFTEST " + ("OK" if ok else "FAILED"))
        return 0 if ok else 1
    if len(argv) >= 2 and argv[1] == "add":
        return cmd_add(argv[2:])
    if len(argv) >= 2 and argv[1] == "list":
        return cmd_list()
    if len(argv) >= 2 and argv[1] == "due":
        return cmd_due()
    if len(argv) >= 3 and argv[1] == "ack":
        return cmd_ack(argv[2])
    if len(argv) >= 3 and argv[1] == "del":
        s = load()
        s["tasks"] = [t for t in s["tasks"] if t["id"] != argv[2]]
        save(s)
        print(f"deleted {argv[2]}")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
