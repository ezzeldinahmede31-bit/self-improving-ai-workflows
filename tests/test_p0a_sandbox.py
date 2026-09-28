"""Tests for agent_sandbox.py (hardened local execution)."""

import os

import agent_sandbox
from agent_sandbox import run_command, run_python


def test_hello_world_local():
    r = run_python("print('hi')", prefer_docker=False)
    assert r.ok and r.tier == "local" and r.stdout.strip() == "hi"


def test_nonzero_exit_reported():
    r = run_python("raise SystemExit(3)", prefer_docker=False)
    assert not r.ok and r.returncode == 3


def test_timeout_kills_runaway():
    r = run_python("while True: pass", timeout_s=2, prefer_docker=False)
    assert not r.ok and r.timed_out


def test_empty_code_refused():
    r = run_python("   ", prefer_docker=False)
    assert not r.ok and r.tier == "none"


def test_secrets_not_inherited():
    os.environ["AGENT_SBX_PROBE_SECRET"] = "s3cr3t-probe"
    try:
        r = run_python("import os; print(os.environ.get("
                       "'AGENT_SBX_PROBE_SECRET', 'ABSENT'))",
                       prefer_docker=False)
    finally:
        del os.environ["AGENT_SBX_PROBE_SECRET"]
    assert r.ok and r.stdout.strip() == "ABSENT"


def test_output_truncated():
    r = run_python("print('x' * 100000)", max_output=1000,
                   prefer_docker=False)
    assert r.ok and len(r.stdout) <= 1000


def test_run_command_no_shell():
    r = run_command(["echo", "ok"])
    assert r.ok and r.stdout.strip() == "ok"


def test_run_command_rejects_bad_argv():
    r = run_command([])
    assert not r.ok


def test_tier_named_in_result():
    r = run_python("print(1)", prefer_docker=True)
    assert r.tier in ("docker", "local")
