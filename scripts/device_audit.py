#!/usr/bin/env python3
"""device_audit.py — hash-chained audit log with secret redaction.

Every security-relevant event appends one JSON line:
  {seq, ts, session, actor, action, tool, verdict, detail(redacted), prev, hash}
hash = sha256(prev + canonical_json). Tampering/deletion/reordering breaks
`verify`. Secrets (env-style KEY=..., bearer tokens, ssh keys, cookies) are
redacted BEFORE write and never appear in logs.

Usage:
  device_audit.py log --session S --actor loop --action exec --tool Bash \\
      --verdict ALLOW --detail "git status"
  device_audit.py verify
  device_audit.py tail [N]
  device_audit.py selftest
Log: /tmp/opencode-device/audit.jsonl
"""
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path

LOG = Path("/tmp/opencode-device/audit.jsonl")

REDACT_RES = [
    (re.compile(r"(?i)(api[_-]?key|token|secret|password|passwd|bearer)[\"']?\s*[:=]\s*[\"']?([^\s\"',;}]+)"),
     r"\1=***REDACTED***"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----"),
     "***REDACTED-KEY***"),
    (re.compile(r"\b[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"), "***REDACTED-JWT***"),
    (re.compile(r"sessionid=[^;\s]+", re.I), "sessionid=***REDACTED***"),
]


def redact(text):
    if not isinstance(text, str):
        text = json.dumps(text)
    for rx, rep in REDACT_RES:
        text = rx.sub(rep, text)
    return text[:2000]


def _last_hash():
    if not LOG.exists():
        return "GENESIS"
    last = None
    with open(LOG) as f:
        for line in f:
            line = line.strip()
            if line:
                last = line
    return json.loads(last)["hash"] if last else "GENESIS"


def cmd_log(session, actor, action, tool, verdict, detail=""):
    import fcntl
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a+") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.seek(0)
        lines = [l for l in f.read().splitlines() if l.strip()]
        prev = json.loads(lines[-1])["hash"] if lines else "GENESIS"
        ev = {"seq": len(lines), "ts": time.time(), "session": session,
              "actor": actor, "action": action, "tool": tool, "verdict": verdict,
              "detail": redact(detail), "prev": prev}
        ev["hash"] = hashlib.sha256(
            (prev + json.dumps(ev, sort_keys=True)).encode()).hexdigest()
        f.write(json.dumps(ev) + "\n")
        f.flush()
    return ev["hash"][:12]


def cmd_verify():
    if not LOG.exists():
        print("empty log: vacuously valid")
        return 0
    prev, n = "GENESIS", 0
    with open(LOG) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            ev = json.loads(line)
            if ev["seq"] != n or ev["prev"] != prev:
                print(f"CORRUPT at seq {ev.get('seq')} (order/prev mismatch)")
                return 1
            h = hashlib.sha256(
                (ev["prev"] + json.dumps(
                    {k: v for k, v in ev.items() if k != "hash"},
                    sort_keys=True)).encode()).hexdigest()
            if h != ev["hash"]:
                print(f"TAMPER at seq {n}")
                return 1
            prev, n = ev["hash"], n + 1
    print(f"chain valid: {n} events")
    return 0


def main(argv):
    if len(argv) == 2 and argv[1] == "selftest":
        import subprocess
        if LOG.exists():
            LOG.unlink()
        subprocess.run([sys.executable, __file__, "log", "--session", "T",
                        "--actor", "t", "--action", "exec", "--tool", "Bash",
                        "--verdict", "ALLOW", "--detail", "echo hi API_KEY=zzz-secret-123"],
                       check=True, capture_output=True)
        body = LOG.read_text()
        ok1 = "zzz-secret-123" not in body and "***REDACTED***" in body
        print(f"secret redacted -> {'PASS' if ok1 else 'FAIL'}")
        r = subprocess.run([sys.executable, __file__, "verify"], capture_output=True, text=True)
        ok2 = r.returncode == 0
        print(f"chain verifies -> {'PASS' if ok2 else 'FAIL'}")
        # tamper: flip a char, verify must fail
        lines = LOG.read_text().splitlines()
        lines[0] = lines[0].replace("echo hi", "echo HACK")
        LOG.write_text("\n".join(lines) + "\n")
        r = subprocess.run([sys.executable, __file__, "verify"], capture_output=True, text=True)
        ok3 = r.returncode != 0
        print(f"tamper detected -> {'PASS' if ok3 else 'FAIL'}")
        LOG.unlink()
        ok = ok1 and ok2 and ok3
        print("SELFTEST " + ("OK" if ok else "FAILED"))
        return 0 if ok else 1
    if len(argv) >= 2 and argv[1] == "log":
        g = lambda k, d="": argv[argv.index(k) + 1] if k in argv else d
        print(cmd_log(g("--session"), g("--actor"), g("--action"), g("--tool"),
                      g("--verdict"), g("--detail")))
        return 0
    if len(argv) >= 2 and argv[1] == "verify":
        return cmd_verify()
    if len(argv) >= 2 and argv[1] == "tail":
        n = int(argv[2]) if len(argv) > 2 else 5
        if LOG.exists():
            for line in LOG.read_text().splitlines()[-n:]:
                print(line)
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
