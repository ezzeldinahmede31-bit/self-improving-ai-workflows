"""test_sandbox_escape.py — bwrap defense-in-depth escape suite.

Real bwrap executions (no mocks). Honest scope: bwrap = isolation, NOT a
complete MAC boundary (see docs/SECURITY_MODEL.md). Each vector asserts what
the REAL boundary enforces; /proc visibility that is inherent to `--proc`
(without sensitive content) is documented, not over-claimed.
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(HERE / "scripts"))

from device_sandbox import contained, run  # noqa: E402

RESULTS = {}


def rec(name, verdict, evidence):
    RESULTS[name] = {"verdict": verdict, "evidence": evidence}
    print(f"[{verdict}] {name}: {evidence}")


def workdir():
    d = Path(tempfile.mkdtemp(prefix="sbx-esc-"))
    return d


def test_sandbox_escape():
    # 1. path traversal as workdir
    assert not contained("/tmp/../etc")
    rec("path_traversal", "DENY", "workdir /etc via .. refused")

    # 2. symlink escape: link inside /tmp pointing at /etc
    w = workdir()
    link = w / "evil-link"
    try:
        link.symlink_to("/etc")
    except Exception:
        pass
    assert not contained(str(link)), "symlink to /etc must not be contained"
    rec("symlink_escape", "DENY", "resolve() collapses link, refused")

    # 3. mount escape: write outside the bound workdir must fail/land nowhere
    w = workdir()
    outside = Path(tempfile.mkdtemp(prefix="sbx-out-")) / "escaped.txt"
    rc = run(["/bin/sh", "-c", f"echo x > {outside}"],
             workdir=str(w), timeout=30)
    assert not outside.exists(), "host file outside workdir was written!"
    rec("mount_escape", "DENY", f"rc={rc} host_outside_absent=True")

    # 4. /proc abuse: reading host init environ must not leak host secrets
    w = workdir()
    r = subprocess.run(
        [sys.executable, "scripts/device_sandbox.py", "--",
         "/bin/cat", "/proc/1/environ"],
        capture_output=True, text=True, timeout=60, cwd=str(HERE))
    leaked = "WORKFLOWHUB_API_KEY" in (r.stdout + r.stderr)
    assert not leaked
    rec("proc_abuse", "DENY" if r.returncode != 0 else "BLOCKED",
        f"rc={r.returncode} host_secret_absent=True")

    # 5. /dev abuse: no device creation inside sandbox
    w = workdir()
    rc = run(["/bin/mknod", str(w / "null2"), "c", "1", "3"],
             workdir=str(w), timeout=30)
    assert rc != 0 and not (w / "null2").exists()
    rec("dev_abuse", "DENY", f"mknod rc={rc}")

    # 6. environment injection: parent secrets + LD_PRELOAD must not pass
    w = workdir()
    os.environ["TBW_CANARY_SECRET"] = "canary-12345"
    os.environ["LD_PRELOAD"] = "/tmp/evil.so"
    try:
        r = subprocess.run(
            [sys.executable, "scripts/device_sandbox.py", "--",
             "/usr/bin/python3", "-c",
             "import os;print('CANARY' if 'TBW_CANARY_SECRET' in os.environ "
             "else 'CLEAN');print('PRELOAD' if 'LD_PRELOAD' in os.environ "
             "else 'NOPRELOAD')"],
            capture_output=True, text=True, timeout=60, cwd=str(HERE))
        assert "CLEAN" in r.stdout and "NOPRELOAD" in r.stdout, r.stdout
        rec("env_injection", "DENY", "sanitized env: no secret, no LD_PRELOAD")
    finally:
        del os.environ["TBW_CANARY_SECRET"]
        del os.environ["LD_PRELOAD"]

    # 7. fd inheritance at sandbox layer
    w = workdir()
    secret = w / "s.txt"
    secret.write_text("x")
    fd = os.open(str(secret), os.O_RDONLY)
    try:
        assert not os.get_inheritable(fd)
        rc = run(["/bin/cat", f"/proc/self/fd/{fd}"], workdir=str(w),
                 timeout=30)
        assert rc != 0
        rec("fd_inheritance", "DENY", f"cat fd rc={rc}")
    finally:
        os.close(fd)

    # 8. subprocess escape (nsenter/setns to host ns)
    w = workdir()
    rc = run(["/usr/bin/python3", "-c",
              "import os;os.setns(open('/proc/1/ns/mnt').fileno(),0)"],
             workdir=str(w), timeout=30)
    assert rc != 0
    rec("subprocess_ns_escape", "DENY", f"setns rc={rc}")

    # 9. network escape
    w = workdir()
    rc = run(["/usr/bin/python3", "-c",
              "import socket;socket.create_connection(('8.8.8.8',53),timeout=4)"],
             workdir=str(w), no_net=True, timeout=30)
    assert rc != 0
    rec("network_escape", "DENY", f"egress rc={rc}")

    # 10. privileged escalation attempt
    w = workdir()
    rc = run(["/usr/bin/sudo", "-n", "true"], workdir=str(w), timeout=30)
    assert rc != 0
    rec("privesc", "DENY", f"sudo rc={rc}")

    fails = [k for k, v in RESULTS.items() if v["verdict"] not in
             ("DENY", "BLOCKED")]
    assert not fails, f"escape FAILs: {fails}"
