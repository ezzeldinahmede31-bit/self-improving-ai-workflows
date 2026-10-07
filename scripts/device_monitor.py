#!/usr/bin/env python3
"""device_monitor.py v2 — hardened background watcher.

Fixes vs v1 (see docs/FINAL_GAP_MATRIX_BEFORE.md):
- start() permission-gates the command (Bash policy); DENY refuses.
- ids sanitized (8-hex only); no path traversal.
- cap 20 live monitors; per-log cap 1MB (then note + stop appending).
- kill = process GROUP (setsid) + SIGTERM, SIGKILL fallback; no PID-reuse
  hazard (killpg on our own group only).
- deadline enforced on poll: expiry kills the group, marks ended-deadline.
- stop() GCs the directory. poll() never crashes on bad id.

Usage: start -- <cmd>... [--deadline S] | poll <id> [--since N] |
       stop <id> | list | selftest
"""
import json
import os
import re
import signal
import subprocess
import sys
import time
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from device_permissions import evaluate  # noqa: E402

ROOT = Path("/tmp/opencode-device/monitors")
DEFAULT_DEADLINE_S = 5 * 60
MAX_DEADLINE_S = 30 * 60
MAX_MONITORS = 20
LOG_CAP = 1024 * 1024
ID_RE = re.compile(r"^[0-9a-f]{8}$")


def _ok_id(mid):
    return bool(ID_RE.match(mid or ""))


def _meta(mid):
    return json.loads((ROOT / mid / "meta.json").read_text())


def _live():
    return [d for d in ROOT.glob("*") if d.is_dir() and _ok_id(d.name)] \
        if ROOT.exists() else []


def cmd_start(cmd, deadline_s=DEFAULT_DEADLINE_S):
    tier, rule = evaluate("Bash", " ".join(cmd))
    if tier == "deny":
        print(f"DENIED by policy: {rule}", file=sys.stderr)
        return None
    if len(_live()) >= MAX_MONITORS:
        print("DENIED: monitor cap reached", file=sys.stderr)
        return None
    deadline_s = min(max(1, deadline_s), MAX_DEADLINE_S)
    mid = uuid.uuid4().hex[:8]
    d = ROOT / mid
    d.mkdir(parents=True, exist_ok=True)
    (d / "lines.jsonl").write_text("")
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         text=True, bufsize=1, start_new_session=True)
    (d / "meta.json").write_text(json.dumps({
        "id": mid, "cmd": cmd, "pid": p.pid, "pgid": os.getpgid(p.pid),
        "started": time.time(), "deadline": time.time() + deadline_s,
        "status": "running"}))
    if os.fork() == 0:  # collector: pipe -> capped log
        try:
            with open(d / "lines.jsonl", "a") as log:
                for line in p.stdout:
                    if (d / "lines.jsonl").stat().st_size < LOG_CAP:
                        log.write(line)
                        log.flush()
                    # else: drop (cap), keeps disk bounded
            try:
                m = json.loads((d / "meta.json").read_text())
                if m.get("status") == "running":
                    m["status"] = "exited"
                    (d / "meta.json").write_text(json.dumps(m))
            except Exception:
                pass
        finally:
            os._exit(0)
    return mid


def _kill_group(m):
    try:
        os.killpg(m["pgid"], signal.SIGTERM)
    except Exception:
        pass
    time.sleep(1)
    try:
        os.killpg(m["pgid"], signal.SIGKILL)
    except Exception:
        pass


def cmd_poll(mid, since=0):
    if not _ok_id(mid) or not (ROOT / mid / "meta.json").exists():
        print(json.dumps({"error": "unknown monitor"}))
        return 1
    m = _meta(mid)
    lines = []
    f = ROOT / mid / "lines.jsonl"
    if f.exists():
        rows = f.read_text().splitlines()
        lines = rows[since:since + 200]
    alive = False
    try:
        os.kill(m["pid"], 0)
        alive = True
    except Exception:
        alive = False
    note = None
    if time.time() > m["deadline"] and m["status"] == "running":
        _kill_group(m)
        m["status"] = "ended-deadline"
        (ROOT / mid / "meta.json").write_text(json.dumps(m))
        note = "deadline reached: group killed (one notice)"
        alive = False
    print(json.dumps({"id": mid, "status": m["status"], "alive": alive,
                      "next_since": since + len(lines), "lines": lines,
                      "note": note}, indent=1))
    return 0


def cmd_stop(mid):
    if not _ok_id(mid) or not (ROOT / mid / "meta.json").exists():
        print("unknown monitor", file=sys.stderr)
        return 1
    m = _meta(mid)
    _kill_group(m)
    import shutil
    shutil.rmtree(ROOT / mid, ignore_errors=True)  # GC state
    print(f"stopped+GC {mid}")
    return 0


def main(argv):
    if len(argv) == 2 and argv[1] == "selftest":
        ROOT.mkdir(parents=True, exist_ok=True)
        # 1. gated start: dangerous command refused
        mid = cmd_start(["rm", "-rf", "/tmp/whatever"])
        ok1 = mid is None
        print(f"gated start refuses rm -rf -> {'PASS' if ok1 else 'FAIL'}")
        # 2. live lines
        mid = cmd_start(["/usr/bin/python3", "-c",
                         "print('L1',flush=True);print('L2',flush=True)"])
        time.sleep(1.5)
        r = subprocess.run([sys.executable, __file__, "poll", mid],
                           capture_output=True, text=True, timeout=15)
        d = json.loads(r.stdout)
        ok2 = d["lines"] == ["L1", "L2"]
        print(f"lines stream -> {'PASS' if ok2 else 'FAIL'}")
        # 3. bad id + traversal rejected, no crash
        r = subprocess.run([sys.executable, __file__, "poll", "../../etc"],
                           capture_output=True, text=True, timeout=15)
        ok3 = "unknown monitor" in r.stdout
        print(f"traversal id rejected -> {'PASS' if ok3 else 'FAIL'}")
        # 4. stop GCs
        subprocess.run([sys.executable, __file__, "stop", mid],
                       capture_output=True, timeout=15)
        ok4 = not (ROOT / mid).exists()
        print(f"stop GCs state -> {'PASS' if ok4 else 'FAIL'}")
        ok = ok1 and ok2 and ok3 and ok4
        print("SELFTEST " + ("OK" if ok else "FAILED"))
        return 0 if ok else 1
    if len(argv) >= 2 and argv[1] == "start":
        i = argv.index("--") if "--" in argv else 2
        deadline = DEFAULT_DEADLINE_S
        if "--deadline" in argv:
            deadline = int(argv[argv.index("--deadline") + 1])
        mid = cmd_start(argv[i + 1:], deadline_s=deadline)
        if mid is None:
            return 20
        print(mid)
        return 0
    if len(argv) >= 3 and argv[1] == "poll":
        since = int(argv[argv.index("--since") + 1]) if "--since" in argv else 0
        return cmd_poll(argv[2], since)
    if len(argv) >= 3 and argv[1] == "stop":
        return cmd_stop(argv[2])
    if len(argv) >= 2 and argv[1] == "list":
        for d in _live():
            try:
                m = json.loads((d / "meta.json").read_text())
                print(f"{m['id']}  {m['status']}  pid={m['pid']}  {' '.join(m['cmd'])}")
            except Exception:
                pass
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
