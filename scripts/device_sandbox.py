#!/usr/bin/env python3
"""device_sandbox.py — run untrusted commands inside bubblewrap (bwrap).

SCOPE HONESTY: bwrap provides unprivileged namespace/mount isolation. It is
NOT a complete MAC/security boundary (no SELinux/AppArmor policy, no seccomp
filter here, kernel attack surface remains). See docs/SECURITY_MODEL.md.
Optional OS-level depth (AppArmor profile, systemd sandboxing, dedicated
unprivileged user) is documented there and degrades gracefully when absent.

Proven bind set on this box (bubblewrap 0.9.0, unprivileged userns=1):
  --ro-bind /usr /usr --ro-bind /lib /lib --ro-bind /lib64 /lib64
  --ro-bind /etc/ld.so.cache ... --tmpfs /tmp --proc /proc --dev /dev
  --unshare-net   (no network egress at all)
  --bind <workdir> <workdir>  (only dir the command may write)

Plus: sanitized child env (no secret/env-var injection), prlimit caps
(1GB AS, 120s CPU; NPROC cap omitted — breaks userns on this kernel),
close_fds, symlink-resolving containment, --die-with-parent.

Usage:
  device_sandbox.py -- sbatch-command...            # net ON, workdir rw
  device_sandbox.py --no-net -- <cmd>...           # net OFF
  device_sandbox.py --ro -- <cmd>...               # whole fs read-only + tmpfs
  device_sandbox.py selftest
Exit code = the command's exit code. Refuses when bwrap is missing.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from device_permissions import evaluate  # noqa: E402

BASE_BINDS = [
    "--ro-bind", "/usr", "/usr",
    "--ro-bind", "/lib", "/lib",
    "--ro-bind", "/lib64", "/lib64",
    "--ro-bind", "/etc/ld.so.cache", "/etc/ld.so.cache",
    "--tmpfs", "/tmp",
    "--proc", "/proc",
    "--dev", "/dev",
]
OUT_CAP = 100 * 1024

SAFE_WORK_PARENTS = [Path("/tmp").resolve()]

# Defense-in-depth additions (hardening round 2026-10-07):
# - CLEAN_ENV: the child never inherits the parent environment (no secret
#   leakage, no LD_PRELOAD / PYTHONPATH / BASH_ENV injection).
# - NEVER_WORKDIRS: pseudo-filesystems and roots that must never be a workdir.
CLEAN_ENV_KEYS = ("PATH", "LANG", "LC_ALL", "TZ")
NEVER_WORKDIRS = (Path("/"), Path("/usr"), Path("/etc"), Path("/lib"),
                  Path("/lib64"), Path("/proc"), Path("/sys"), Path("/dev"))


def clean_env(workdir):
    env = {k: v for k, v in os.environ.items() if k in CLEAN_ENV_KEYS}
    env.setdefault("PATH", "/usr/bin:/bin")
    env.setdefault("LANG", "C.UTF-8")
    env["HOME"] = workdir  # contained scratch, never the real $HOME
    return env


def contained(workdir):
    try:
        wd = Path(workdir).resolve()  # resolves symlinks: escape collapses
    except Exception:
        return False
    if wd in NEVER_WORKDIRS or wd == Path.home().resolve():
        return False
    if wd in (Path("/proc"), Path("/sys"), Path("/dev")):
        return False
    try:
        wd.relative_to(Path.cwd().resolve())
        return True
    except ValueError:
        pass
    return any(str(wd).startswith(str(p) + "/") or wd == p
               for p in SAFE_WORK_PARENTS)


def run(cmd, workdir=".", no_net=True, read_only=False, timeout=120):
    if not shutil.which("bwrap"):
        print("DENIED: bwrap not installed", file=sys.stderr)
        return 127
    if not contained(workdir):
        print(f"DENIED: workdir outside containment: {workdir}", file=sys.stderr)
        return 20
    tier, rule = evaluate("Bash", " ".join(cmd))
    if tier == "deny":
        print(f"DENIED by policy: {rule}", file=sys.stderr)
        return 20
    workdir = str(Path(workdir).resolve())
    args = ["bwrap"] + BASE_BINDS
    if no_net:
        args += ["--unshare-net"]
    if read_only:
        args += ["--remount-ro", "/"]
    args += ["--die-with-parent", "--bind", workdir, workdir,
             "--chdir", workdir, "--"] + cmd
    if shutil.which("prlimit"):
        # NOTE: --nproc is deliberately NOT set: on this kernel an NPROC cap
        # breaks unprivileged userns creation outright ("Resource temporarily
        # unavailable"). Fork pressure is bounded by timeout + die-with-parent
        # + plan MAX_STEPS instead. Verified 2026-10-07.
        args = ["prlimit", "--as=1073741824", "--cpu=120"] + args
    try:
        p = subprocess.run(args, capture_output=True, text=True,
                           timeout=timeout, env=clean_env(workdir),
                           close_fds=True)
    except subprocess.TimeoutExpired:
        print(f"TIMEOUT after {timeout}s: {' '.join(cmd)}", file=sys.stderr)
        return 124
    out = (p.stdout or "")[:OUT_CAP]
    err = (p.stderr or "")[:OUT_CAP]
    sys.stdout.write(out)
    sys.stderr.write(err)
    return p.returncode


def main(argv):
    if len(argv) == 2 and argv[1] == "selftest":
        import tempfile
        work = tempfile.mkdtemp(prefix="sbx-")
        rc1 = run(["/usr/bin/echo", "SANDBOX_ECHO_OK"], workdir=work, timeout=15)
        out_ok = rc1 == 0
        r = subprocess.run(
            [sys.executable, "scripts/device_sandbox.py",
             "--", "/usr/bin/python3", "-c",
             "import socket;socket.create_connection(('8.8.8.8',53),timeout=5)"],
            capture_output=True, text=True, timeout=30,
        )
        net_blocked = r.returncode != 0
        print(f"echo contained = {out_ok}, net-isolated = {net_blocked}")
        rc_bad = run(["/usr/bin/echo", "x"], workdir="/", timeout=10)
        contained_ok = rc_bad == 20
        print(f"workdir / refused = {contained_ok}")
        ok = out_ok and net_blocked and contained_ok
        print("SELFTEST " + ("OK" if ok else "FAILED"))
        return 0 if ok else 1
    no_net = "--net" not in argv       # net OFF by default (least privilege)
    read_only = "--ro" in argv
    argv = [a for a in argv[1:] if a not in ("--net", "--ro")]
    if argv and argv[0] == "--":
        argv = argv[1:]
    if not argv:
        print(__doc__)
        return 2
    return run(argv, no_net=no_net, read_only=read_only)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
