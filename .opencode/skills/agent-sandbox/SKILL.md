---
name: agent-sandbox
description: "Hardened agent sandbox skill (docker-strong tier, scrubbed-env local tier, timeouts, output caps). Use when running untrusted or agent-generated code, when secrets must not leak into child processes, or when a runaway loop must die on a deadline. Trigger phrases: 'sandbox this code', 'run untrusted safely', 'timeout runaway', 'تشغيل معزول'."
---

# Agent Sandbox (Two Tiers, Honest Boundaries)

Code: `agent_sandbox.py` (stdlib only). `run_python(code, ...)` picks
the strongest tier available; `run_command(argv, ...)` runs binaries
locally hardened (shell never used).

## Tiers

- **docker** (adversarial boundary): read-only root, no network, memory
  + CPU caps, PID cap, strict timeout, output cap. Used whenever a
  docker binary exists.
- **local** (accident containment): fresh tmp jail as cwd, scrubbed env
  (allow-list keys only — agent secrets never inherited), POSIX rlimits
  (address space, CPU seconds, files, file size), wall-clock timeout,
  truncated output. NOT a boundary against a determined escaper; the
  result always names its tier so callers never assume otherwise.

## When to use

- Any agent-generated or fetched code before its output is trusted.
- Shell-outs from automation (argv form, never string form).
- Long-running helpers that must die on deadline.

## Verification

- `tests/test_p0a_sandbox.py` green (hello, exit codes, timeout kill,
  empty refusal, env scrub, truncation, no-shell).
- Every result carries its tier; local-tier outputs never treated as
  boundary-proof.

## Pairs with

`policy-engine` (who may execute), `egress-firewall` (no network in
docker tier by construction), `build-gates-pipeline`,
`code-execution-guided-swemaster`.
