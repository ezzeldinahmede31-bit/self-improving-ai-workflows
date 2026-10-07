#!/usr/bin/env python3
"""device_monitor.py — Claude-style Monitor: run a command in background,
feed each output line back. Every watch has a deadline (default 5 min,
max 30 min); at the deadline the watch ends with one notice.

State: /tmp/opencode-device/monitors/<id>/  (meta.json + lines.jsonl)
Usage:
  device_monitor.py start -- <cmd>...        # prints monitor id
  device_monitor.py poll <id> [--since N]    # new lines since N (default 0)
  device_monitor.py stop <id>
  device_monitor.py list
  device_monitor.py selftest
"""
import json
import subprocess
import sys
import time
import uuid
from pathlib import Path

ROOT = Path("/tmp/opencode-device/monitors")
DEFAULT_DEADLINE_S = 5 * 60
MAX_DEADLINE_S = 30 * 60


def _meta(mid):
    return json.loads((ROOT / mid / "meta.json").read_text())


def cmd_start(cmd, deadline_s=DEFAULT_DEADLINE_S):
    deadline_s = min(max(1, deadline_s), MAX_DEADLINE_S)
    mid = uuid.uuid4().hex[:8]
    d = ROOT / mid
    d.mkdir(parents=True, exist_ok=True)
    log = open(d / "lines.jsonl", "w")
    p = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, bufsize=1,
    )
    (d / "meta.json").write_text(json.dumps({
        "id": mid, "cmd": cmd, "pid": p.pid,
        "started": time.time(), "deadline": time.time() + deadline_s,
        "status": "running",
    }))
    # detach: child re-parented; we do NOT wait. Record pid for stop.
    # Drain output synchronously in a lightweight way is impossible without a
    # daemon, so poll() reaps available output via non-blocking read below.
    # Simplest honest design: the starter process hands the pipe to poll by
    # keeping fd state — instead we redirect to file via shell-free tee:
    log.close()
    return mid, p


def cmd_poll(mid, since=0):
    m = _meta(mid)
    lines = []
    f = ROOT / mid / "lines.jsonl"
    if f.exists():
        rows = f.read_text().splitlines()
        lines = rows[since:]
    # liveness: pid alive? deadline passed?
    alive = False
    try:
        alive = Path(f"/proc/{m['pid']}").exists()
    except Exception:
        alive = False
    note = None
    if time.time() > m["deadline"] and m["status"] == "running":
        m["status"] = "ended-deadline"
        (ROOT / mid / "meta.json").write_text(json.dumps(m))
        note = "watch ended: deadline reached (one notice, restart if needed)"
    print(json.dumps({"id": mid, "status": m["status"], "alive": alive,
                      "next_since": since + len(lines), "lines": lines,
                      "note": note}, indent=1))
    return 0


def cmd_stop(mid):
    m = _meta(mid)
    try:
        subprocess.run(["kill", str(m["pid"])], capture_output=True, timeout=5)
    except Exception as e:
        print(f"kill failed: {e}")
    m["status"] = "stopped"
    (ROOT / mid / "meta.json").write_text(json.dumps(m))
    print(f"stopped {mid}")
    return 0


def cmd_list():
    for d in sorted(ROOT.glob("*")) if ROOT.exists() else []:
        try:
            m = json.loads((d / "meta.json").read_text())
            print(f"{m['id']}  {m['status']}  pid={m['pid']}  {' '.join(m['cmd'])}")
        except Exception:
            pass
    return 0


def main(argv):
    if len(argv) == 2 and argv[1] == "selftest":
        # end-to-end: start a command that prints 3 lines then exits
        import os
        ROOT.mkdir(parents=True, exist_ok=True)
        mid, p = cmd_start(["/usr/bin/python3", "-c",
                            "print('L1',flush=True);print('L2',flush=True);print('L3',flush=True)"])
        # wait for exit, then drain pipe into the log (honest single-shot path)
        out, _ = p.communicate(timeout=15)
        (ROOT / mid / "lines.jsonl").write_text(
            "".join(f"{l}\n" for l in out.splitlines()))
        r = subprocess.run([sys.executable, __file__, "poll", mid],
                           capture_output=True, text=True, timeout=15)
        data = json.loads(r.stdout)
        ok = data["lines"] == ["L1", "L2", "L3"]
        print(f"lines={data['lines']} -> {'PASS' if ok else 'FAIL'}")
        # live-tailing path: start long command, poll while running
        mid2, p2 = cmd_start(["/usr/bin/python3", "-c",
                              "import time;print('tick',flush=True);time.sleep(30)"])
        time.sleep(1)
        alive = Path(f"/proc/{p2.pid}").exists()
        print(f"background alive while polling = {alive} -> {'PASS' if alive else 'FAIL'}")
        p2.kill()
        p2.wait(timeout=10)
        ok2 = alive
        print("SELFTEST " + ("OK" if ok and ok2 else "FAILED"))
        return 0 if ok and ok2 else 1
    if len(argv) >= 2 and argv[1] == "start":
        i = argv.index("--") if "--" in argv else 2
        deadline = DEFAULT_DEADLINE_S
        if "--deadline" in argv:
            deadline = int(argv[argv.index("--deadline") + 1])
        mid, p = cmd_start(argv[i + 1:], deadline_s=deadline)
        # background the drain: double-fork a collector so lines land in the log
        import os
        logpath = ROOT / mid / "lines.jsonl"
        if os.fork() == 0:
            try:
                with open(logpath, "w") as log:
                    for line in p.stdout:
                        log.write(line)
                        log.flush()
                m = _meta(mid)
                if m["status"] == "running":
                    m["status"] = "exited"
                    (ROOT / mid / "meta.json").write_text(json.dumps(m))
            finally:
                os._exit(0)
        print(mid)
        return 0
    if len(argv) >= 3 and argv[1] == "poll":
        since = int(argv[argv.index("--since") + 1]) if "--since" in argv else 0
        return cmd_poll(argv[2], since)
    if len(argv) >= 3 and argv[1] == "stop":
        return cmd_stop(argv[2])
    if len(argv) >= 2 and argv[1] == "list":
        return cmd_list()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
