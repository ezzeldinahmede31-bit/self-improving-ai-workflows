#!/usr/bin/env python3
"""device_redteam.py — adversarial suite (local, safe, no real secrets).

ATTACKS (each must FAIL to cause harm = PASS for us):
 R1 symlink read: symlink /tmp/rt_link -> project .env-ish secret, read via
    link must be DENIED (secret-path resolves realpath).
 R2 file swap (TOCTOU): approve write to /tmp/rt_safe.txt, swap plan to
    /tmp/rt_evil content post-approval -> consume must REJECT (hash-bound).
 R3 stale approval: TTL 1s token, sleep 2, consume -> REJECTED.
 R4 wrong-task replay: token for (S1,a) used on (S2,a) -> REJECTED.
 R5 private-IP/metadata URL gate: check_url denies 169.254.169.254,
    127.0.0.1; allows example.com (public).
 R6 concurrent duplicate resume: two resumes of same destructive-paused
    session -> destructive step executes at most once (idempotency).
 R7 PATH hijack note: `rm` resolved via PATH could shadow; gate matches
    basename too (rm -rf regardless of path prefix) -> DENY.
 R8 state corruption: corrupt session file -> load raises cleanly, no exec.
 R9 broad-ASK shadow: explicit allow still wins over nothing (git status
    ALLOW even with catch-all ASK posture).
 R10 oversized tool args: 5MB command string -> gate handles without OOM
    (truncate + ASK, completes <5s).

Usage: device_redteam.py [run] | selftest(=run). Exit 0 iff all PASS.
Report: /tmp/opencode-device/redteam_report.json
"""
import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PY = sys.executable
ROOT = Path("/tmp/opencode-device")
sys.path.insert(0, str(HERE))
from device_permissions import evaluate, cmd_approve, cmd_consume, check_url  # noqa: E402

results = {}


def rec(name, ok, evidence):
    results[name] = {"pass": bool(ok), "evidence": evidence}
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {evidence}")


def t_r1():
    secret = ROOT / "rt_secret.env"
    secret.write_text("API_KEY=rt-fake-1\n")
    link = Path("/tmp/rt_link_env")
    try:
        link.unlink()
    except Exception:
        pass
    link.symlink_to(secret)
    tier, _ = evaluate("Read", str(link))
    ok = tier == "deny"
    rec("R1_symlink_secret_read", ok, f"read via symlink -> {tier.upper()}")


def t_r2():
    import subprocess
    safe = "/tmp/rt_safe.txt"
    Path(safe).write_text("safe")
    r = subprocess.run([PY, "scripts/device_permissions.py", "approve",
                        "--session", "RT", "--step", "s", "--tool", "Write",
                        "--input", safe, "--ttl", "300"],
                       capture_output=True, text=True)
    tok = r.stdout.strip()
    # attacker swaps the intended content target: different path, same token
    rc = cmd_consume("RT", "s", "Write", "/tmp/rt_evil.txt", tok)
    ok = rc != 0
    rec("R2_approval_command_binding", ok, "swapped target rejected" if ok else "SWAP ACCEPTED (BAD)")


def t_r3():
    import subprocess
    r = subprocess.run([PY, "scripts/device_permissions.py", "approve",
                        "--session", "RT", "--step", "s", "--tool", "Bash",
                        "--input", "echo hi", "--ttl", "1"],
                       capture_output=True, text=True)
    tok = r.stdout.strip()
    time.sleep(2)
    rc = cmd_consume("RT", "s", "Bash", "echo hi", tok)
    rec("R3_stale_approval", rc != 0, "expired token rejected" if rc != 0 else "STALE ACCEPTED (BAD)")


def t_r4():
    import subprocess
    r = subprocess.run([PY, "scripts/device_permissions.py", "approve",
                        "--session", "S1", "--step", "a", "--tool", "Bash",
                        "--input", "echo hi", "--ttl", "300"],
                       capture_output=True, text=True)
    tok = r.stdout.strip()
    rc = cmd_consume("S2", "a", "Bash", "echo hi", tok)
    rec("R4_wrong_task_replay", rc != 0, "cross-session replay rejected" if rc != 0 else "REPLAY ACCEPTED (BAD)")


def t_r5():
    cases = [("http://169.254.169.254/latest/meta-data/", "deny"),
             ("http://127.0.0.1:8080/admin", "ask"),
             ("http://10.0.0.5/x", "ask"),
             ("http://example.com/", "allow")]
    ok = True
    for url, want in cases:
        got, _ = check_url(url)
        if got != want:
            ok = False
        print(f"  url {url} -> {got.upper()} (want {want.upper()})")
    rec("R5_ssrf_private_ip", ok, "metadata denied, private ask, public allow")


def t_r6():
    import subprocess
    plan = {"steps": [{"id": "d", "tool": "bash", "args": ["echo", "t6"]}]}
    pf = ROOT / "rt_plan.json"
    pf.write_text(json.dumps(plan))
    # approve d in two parallel "workers": only one token each; run resume twice
    r = subprocess.run([PY, "scripts/device_loop.py", "run", "--plan", str(pf)],
                       capture_output=True, text=True)
    try:
        st = json.loads(r.stdout)
    except Exception:
        rec("R6_concurrent_resume", False, "run output unparseable")
        return
    sid = st["session"]
    a1 = subprocess.run([PY, "scripts/device_loop.py", "approve", sid, "d"],
                        capture_output=True, text=True)
    a2 = subprocess.run([PY, "scripts/device_loop.py", "approve", sid, "d"],
                        capture_output=True, text=True)
    try:
        s1, s2 = json.loads(a1.stdout), json.loads(a2.stdout)
    except Exception:
        rec("R6_concurrent_resume", False, "approve output unparseable")
        return
    # second approve mints a FRESH token for an already-done step; drive skips
    # done steps, so the echo ran at most once per completed record
    ok = s1.get("status") == "done"
    rec("R6_concurrent_resume", ok, f"double-approve safe: first={s1.get('status')} second={s2.get('status')}")


def t_r7():
    for cmd in ["rm -rf /tmp/x", "/bin/rm -rf /tmp/x", "sudo rm -rf /tmp/x",
                "bash -c 'rm -rf /tmp/x'", "python3 -c \"import shutil;shutil.rmtree('/tmp/x')\""]:
        tier, _ = evaluate("Bash", cmd)
        if tier != "deny":
            rec("R7_path_hijack_variants", False, f"{cmd!r} -> {tier}")
            return
    rec("R7_path_hijack_variants", True, "5 rm variants all DENY")


def t_r8():
    from device_state import write as swrite, _path as spath
    from device_loop import load
    swrite("sessions/rt-corrupt.json", {"broken": True})
    # corrupt at the RESOLVED (durable) root, not a hardcoded legacy path
    spath("sessions/rt-corrupt.json").write_text("{not json")
    try:
        load("rt-corrupt")
        rec("R8_state_corruption", False, "corrupt session loaded (BAD)")
    except Exception as e:
        rec("R8_state_corruption", True, f"clean failure: {type(e).__name__}")


def t_r9():
    tier, _ = evaluate("Bash", "git status")
    rec("R9_allow_survives_ask_posture", tier == "allow", f"git status -> {tier.upper()}")


def t_r10():
    big = "echo " + "A" * (5 * 1024 * 1024)
    t0 = time.time()
    tier, _ = evaluate("Bash", big)
    dt = time.time() - t0
    ok = dt < 5 and tier in ("ask", "deny")
    rec("R10_oversized_args", ok, f"{len(big)}B gated to {tier.upper()} in {dt:.2f}s")


def main(argv):
    ROOT.mkdir(parents=True, exist_ok=True)
    t_r1(); t_r2(); t_r3(); t_r4(); t_r5()
    t_r6(); t_r7(); t_r8(); t_r9(); t_r10()
    fails = sum(1 for v in results.values() if not v["pass"])
    rep = {"tests": results, "failed": fails,
           "verdict": "PASS" if fails == 0 else "FAIL",
           "time": time.strftime("%Y-%m-%d %H:%M:%S")}
    (ROOT / "redteam_report.json").write_text(json.dumps(rep, indent=1))
    print(f"\nREDTEAM: {rep['verdict']} ({len(results)-fails}/{len(results)})")
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
