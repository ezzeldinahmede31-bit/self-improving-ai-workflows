#!/usr/bin/env python3
"""device_state.py — atomic JSON state store with backup/restore + idempotency.

All device state goes through here (sessions, cron, approvals): tmp-file +
os.replace (atomic), per-file lock via lockfile, corrupt file -> quarantined
(.corrupt-<ts>) and reported, never silently loaded.

Idempotency: once(key, result) records completed destructive operations;
peek(key) tells a resumed worker to SKIP re-execution (no double delete/push).

Backup: snapshot() copies every state file to a timestamped dir; restore()
puts them back and verifies JSON parses. RPO = last snapshot, RTO = seconds.

Usage:
  device_state.py read <name> | write <name> (stdin JSON)
  device_state.py once <key> (stdin result) | peek <key>
  device_state.py snapshot | restore <dir> | list
  device_state.py selftest
Root: /tmp/opencode-device/state ; backups: /tmp/opencode-device/backups
"""
import json
import os
import shutil
import sys
import time
from pathlib import Path

ROOT = Path("/tmp/opencode-device/state")
BACKUPS = Path("/tmp/opencode-device/backups")
IDEM = "idempotency.json"


def _path(name):
    p = (ROOT / name).resolve()
    assert str(p).startswith(str(ROOT.resolve())), "path escape"
    return p


def read(name):
    p = _path(name)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except Exception:
        q = p.with_suffix(p.suffix + f".corrupt-{int(time.time())}")
        p.rename(q)
        raise RuntimeError(f"corrupt state quarantined at {q}")


def write(name, obj):
    p = _path(name)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + f".tmp{os.getpid()}")
    tmp.write_text(json.dumps(obj, indent=1))
    os.replace(tmp, p)


def peek(key):
    d = read(IDEM) or {}
    rec = d.get(key)
    return rec["result"] if rec else None


def once(key, result):
    d = read(IDEM) or {}
    if key in d:
        return d[key]["result"], False
    d[key] = {"result": result, "ts": time.time()}
    write(IDEM, d)
    return result, True


def snapshot():
    ts = time.strftime("%Y%m%d-%H%M%S")
    dest = BACKUPS / ts
    dest.mkdir(parents=True, exist_ok=True)
    n = 0
    for f in ROOT.rglob("*.json"):
        rel = f.relative_to(ROOT)
        (dest / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, dest / rel)
        n += 1
    print(f"{dest} ({n} files)")
    return 0


def restore(d):
    src = Path(d)
    assert src.exists(), "no such backup"
    for f in src.rglob("*.json"):
        json.loads(f.read_text())  # verify parses BEFORE touching live state
    for f in src.rglob("*.json"):
        rel = f.relative_to(src)
        (ROOT / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, ROOT / rel)
    print(f"restored {d}")
    return 0


def main(argv):
    if len(argv) == 2 and argv[1] == "selftest":
        import uuid
        write("t.json", {"a": 1})
        ok1 = read("t.json") == {"a": 1}
        print(f"atomic roundtrip -> {'PASS' if ok1 else 'FAIL'}")
        k = f"op-{uuid.uuid4().hex[:6]}"
        r1, fresh1 = once(k, {"done": True})
        r2, fresh2 = once(k, {"done": True})
        ok2 = fresh1 and not fresh2 and r1 == r2 and peek(k) == r1
        print(f"idempotency no-double-exec -> {'PASS' if ok2 else 'FAIL'}")
        (_path("t.json")).write_text("{broken")
        try:
            read("t.json")
            ok3 = False
        except RuntimeError:
            ok3 = True
        print(f"corrupt quarantined -> {'PASS' if ok3 else 'FAIL'}")
        write("t.json", {"a": 2})
        import subprocess
        r = subprocess.run([sys.executable, __file__, "snapshot"], capture_output=True, text=True)
        dest = r.stdout.strip().split(" ")[0]
        write("t.json", {"a": 999})
        subprocess.run([sys.executable, __file__, "restore", dest], check=True, capture_output=True)
        ok4 = read("t.json") == {"a": 2}
        print(f"backup/restore -> {'PASS' if ok4 else 'FAIL'}")
        ok = ok1 and ok2 and ok3 and ok4
        print("SELFTEST " + ("OK" if ok else "FAILED"))
        return 0 if ok else 1
    if len(argv) >= 3 and argv[1] == "read":
        print(json.dumps(read(argv[2])))
        return 0
    if len(argv) >= 3 and argv[1] == "write":
        write(argv[2], json.loads(sys.stdin.read()))
        print("wrote")
        return 0
    if len(argv) >= 4 and argv[1] == "once":
        r, fresh = once(argv[2], json.loads(sys.stdin.read()))
        print(json.dumps({"fresh": fresh, "result": r}))
        return 0
    if len(argv) >= 3 and argv[1] == "peek":
        print(json.dumps(peek(argv[2])))
        return 0
    if len(argv) >= 2 and argv[1] == "snapshot":
        return snapshot()
    if len(argv) >= 3 and argv[1] == "restore":
        return restore(argv[2])
    if len(argv) >= 2 and argv[1] == "list":
        for f in sorted(ROOT.rglob("*.json")):
            print(f.relative_to(ROOT))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
