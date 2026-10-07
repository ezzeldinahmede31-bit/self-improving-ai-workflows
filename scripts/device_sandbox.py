#!/usr/bin/env python3
"""device_sandbox.py — run untrusted commands inside bubblewrap (bwrap).

Proven bind set on this box (bubblewrap 0.9.0, unprivileged userns=1):
  --ro-bind /usr /usr --ro-bind /lib /lib --ro-bind /lib64 /lib64
  --ro-bind /etc/ld.so.cache ... --tmpfs /tmp --proc /proc --dev /dev
  --unshare-net   (no network egress at all)
  --bind <workdir> <workdir>  (only dir the command may write)

Usage:
  device_sandbox.py -- sbatch-command...            # net ON, workdir rw
  device_sandbox.py --no-net -- <cmd>...           # net OFF
  device_sandbox.py --ro -- <cmd>...               # whole fs read-only + tmpfs
  device_sandbox.py selftest
Exit code = the command's exit code. Refuses when bwrap is missing.
"""
import shutil
import subprocess
import sys
from pathlib import Path

BASE_BINDS = [
    "--ro-bind", "/usr", "/usr",
    "--ro-bind", "/lib", "/lib",
    "--ro-bind", "/lib64", "/lib64",
    "--ro-bind", "/etc/ld.so.cache", "/etc/ld.so.cache",
    "--tmpfs", "/tmp",
    "--proc", "/proc",
    "--dev", "/dev",
]


def run(cmd, workdir=".", no_net=False, read_only=False, timeout=120):
    if not shutil.which("bwrap"):
        print("DENIED: bwrap not installed", file=sys.stderr)
        return 127
    workdir = str(Path(workdir).resolve())
    args = ["bwrap"] + BASE_BINDS
    if no_net:
        args += ["--unshare-net"]
    if read_only:
        args += ["--remount-ro", "/"]
    args += ["--bind", workdir, workdir, "--chdir", workdir, "--"] + cmd
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        print(f"TIMEOUT after {timeout}s: {' '.join(cmd)}", file=sys.stderr)
        return 124
    sys.stdout.write(p.stdout)
    sys.stderr.write(p.stderr)
    return p.returncode


def main(argv):
    if len(argv) == 2 and argv[1] == "selftest":
        rc1 = run(["/usr/bin/echo", "SANDBOX_ECHO_OK"], timeout=15)
        r = subprocess.run(
            ["venv/bin/python", "scripts/device_sandbox.py", "--no-net",
             "--", "/usr/bin/python3", "-c",
             "import socket;socket.create_connection(('8.8.8.8',53),timeout=5)"],
            capture_output=True, text=True, timeout=30,
        )
        net_blocked = r.returncode != 0
        print(f"net-isolated(no-net python egress blocked) = {net_blocked}")
        ok = rc1 == 0 and net_blocked
        print("SELFTEST " + ("OK" if ok else "FAILED"))
        return 0 if ok else 1
    no_net = "--no-net" in argv
    read_only = "--ro" in argv
    argv = [a for a in argv[1:] if a not in ("--no-net", "--ro")]
    if argv and argv[0] == "--":
        argv = argv[1:]
    if not argv:
        print(__doc__)
        return 2
    return run(argv, no_net=no_net, read_only=read_only)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
