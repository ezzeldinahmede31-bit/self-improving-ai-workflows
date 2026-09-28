"""Hardened local sandbox for running untrusted code.

Two tiers, same result contract:
  - "docker" (strong boundary, when a docker binary is present): read-only
    root fs, no network, capped memory/CPUs, strict timeout, output cap.
  - "local" (hardened fallback, always available): fresh tmp jail as cwd,
    scrubbed environment (allow-list only — secrets never inherited),
    RLIMIT caps on POSIX (address space, CPU seconds, open files, file
    size), wall-clock timeout, truncated output, shell never used.

Honest boundary statement: the local tier raises the bar (timeouts,
memory/CPU ceilings, clean env, output caps) but is NOT a security
boundary against a determined escaper — no namespaces are available to
a plain subprocess. Treat "local" as crash/accident containment and
"docker" as the adversarial boundary. The result always names its tier.

Only stdlib is used. No network access is performed by this module.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass

SAFE_ENV_KEYS = ("PATH", "LANG", "LC_ALL", "TZ", "PYTHONIOENCODING",
                 "PYTHONHASHSEED", "HOME")
DEFAULT_TIMEOUT_S = 20
DEFAULT_MEMORY_MB = 256
DEFAULT_MAX_OUTPUT = 65536


@dataclass
class SandboxResult:
    ok: bool
    tier: str
    returncode: int | None
    stdout: str
    stderr: str
    timed_out: bool = False
    reason: str = ""


def _scrubbed_env(extra: dict | None = None) -> dict:
    env = {k: os.environ[k] for k in SAFE_ENV_KEYS if k in os.environ}
    env.setdefault("PATH", "/usr/bin:/bin")
    for key in ("PYTHONPATH",):
        env.pop(key, None)
    if extra:
        for key, val in extra.items():
            if key.upper() in SAFE_ENV_KEYS:
                env[key] = str(val)
    return env


def _posix_limits(memory_mb: int, cpu_s: int):
    try:
        import resource
    except ImportError:  # pragma: no cover - non-POSIX
        return None

    def _apply() -> None:
        try:
            mem_b = int(memory_mb) * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (mem_b, mem_b))
            resource.setrlimit(resource.RLIMIT_CPU, (int(cpu_s), int(cpu_s)))
            resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))
            resource.setrlimit(resource.RLIMIT_FSIZE, (16 * 1024 * 1024,) * 2)
        except (ValueError, OSError):
            pass

    return _apply


def _has_docker() -> bool:
    return shutil.which("docker") is not None


def run_python(code: str, *, timeout_s: int = DEFAULT_TIMEOUT_S,
               memory_mb: int = DEFAULT_MEMORY_MB,
               max_output: int = DEFAULT_MAX_OUTPUT,
               prefer_docker: bool = True) -> SandboxResult:
    """Execute a Python snippet under the strongest available tier."""
    if not isinstance(code, str) or not code.strip():
        return SandboxResult(False, "none", None, "", "",
                             False, "empty code refused")
    if prefer_docker and _has_docker():
        return _run_python_docker(code, timeout_s, memory_mb, max_output)
    return _run_python_local(code, timeout_s, memory_mb, max_output)


def _run_python_local(code: str, timeout_s: int, memory_mb: int,
                      max_output: int) -> SandboxResult:
    jail = tempfile.mkdtemp(prefix="agent_sbx_")
    try:
        proc = subprocess.run(
            [sys.executable, "-I", "-c", code],
            capture_output=True, text=True, timeout=timeout_s,
            cwd=jail, env=_scrubbed_env(),
            preexec_fn=_posix_limits(memory_mb, max(1, timeout_s + 5)),
        )
        out = proc.stdout[-max_output:]
        err = proc.stderr[-max_output:]
        return SandboxResult(proc.returncode == 0, "local",
                             proc.returncode, out, err)
    except subprocess.TimeoutExpired as exc:
        out = (exc.stdout or b"")[-max_output:] if isinstance(
            exc.stdout, (bytes, str)) else ""
        return SandboxResult(False, "local", None, str(out), "",
                             True, "wall-clock timeout")
    finally:
        shutil.rmtree(jail, ignore_errors=True)


def _run_python_docker(code: str, timeout_s: int, memory_mb: int,
                       max_output: int) -> SandboxResult:
    jail = tempfile.mkdtemp(prefix="agent_sbx_")
    script = os.path.join(jail, "main.py")
    try:
        with open(script, "w", encoding="utf-8") as fh:
            fh.write(code)
        proc = subprocess.run(
            ["docker", "run", "--rm", "--network", "none",
             "--read-only", "--pids-limit", "64",
             "--memory", f"{int(memory_mb)}m",
             "--cpus", "0.5",
             "-v", f"{script}:/tmp/main.py:ro",
             "python:3.11-slim", "python", "/tmp/main.py"],
            capture_output=True, text=True, timeout=timeout_s,
            env=_scrubbed_env(),
        )
        return SandboxResult(proc.returncode == 0, "docker",
                             proc.returncode,
                             proc.stdout[-max_output:],
                             proc.stderr[-max_output:])
    except subprocess.TimeoutExpired:
        return SandboxResult(False, "docker", None, "", "",
                             True, "wall-clock timeout")
    except OSError as exc:
        return SandboxResult(False, "docker", None, "", "",
                             False, f"docker unavailable: {exc}")
    finally:
        shutil.rmtree(jail, ignore_errors=True)


def run_command(argv: list[str], *, timeout_s: int = DEFAULT_TIMEOUT_S,
                memory_mb: int = DEFAULT_MEMORY_MB,
                max_output: int = DEFAULT_MAX_OUTPUT) -> SandboxResult:
    """Run an argv binary under local hardening (shell never used)."""
    if not argv or not all(isinstance(a, str) and a for a in argv):
        return SandboxResult(False, "none", None, "", "",
                             False, "argv must be non-empty strings")
    jail = tempfile.mkdtemp(prefix="agent_sbx_")
    try:
        proc = subprocess.run(
            list(argv), capture_output=True, text=True,
            timeout=timeout_s, cwd=jail, env=_scrubbed_env(),
            shell=False,
            preexec_fn=_posix_limits(memory_mb, max(1, timeout_s + 5)),
        )
        return SandboxResult(proc.returncode == 0, "local",
                             proc.returncode,
                             proc.stdout[-max_output:],
                             proc.stderr[-max_output:])
    except subprocess.TimeoutExpired:
        return SandboxResult(False, "local", None, "", "",
                             True, "wall-clock timeout")
    finally:
        shutil.rmtree(jail, ignore_errors=True)
