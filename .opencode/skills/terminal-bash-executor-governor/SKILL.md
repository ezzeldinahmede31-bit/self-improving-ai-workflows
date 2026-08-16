---
name: terminal-bash-executor-governor
description: "Executes CLI commands, inspects exit codes, manages tailing log output, and enforces safety gates for destructive terminal operations. Use for any terminal run: tests, builds, git ops, package installs. Trigger phrases: 'run the tests', 'run this command', 'check git', 'install', tailing logs, destructive ops."
---

# TERMINAL BASH EXECUTOR GOVERNOR SKILL

## DIRECTIVE
Drive the terminal dynamically to run tests, build tools, inspect git status,
and install packages. Ensure output log truncation and enforce human
confirmation for high-risk operations.

## CLI EXECUTION LAWS
1. **Output Truncation:** Tail long outputs to the last 50 lines. Do NOT flood
   the context window with raw long logs.
2. **Exit Code Validation:** Always check command return codes. If
   `exit code != 0`, immediately extract the core error trace and pass to
   root-cause analyzer.
3. **Safety Gate (Human Confirmation Required):**
   Pauses and asks explicitly BEFORE running destructive actions: `rm -rf`,
   `git push --force`, `drop database`, `sudo systemctl stop`, or external
   network deployments.

## Local adaptation
Use the `bash` tool with the `workdir` parameter instead of `cd && command`
chains. Prefer the dedicated tools over shelling out: `glob`/`grep`/`read`/
`write`/`edit` for files, git via `bash` for VCS. This workspace already treats
`venv/bin/python -m pytest` (269 passing) as the canonical test command and
`git` is optional (project is currently NOT a git repo). Never expose secrets
in command lines — pull credentials via `{file:...}` interpolation or env vars,
never inline. Long outputs: rely on the tool's built-in truncation to a file and
search the tail with `Read`/`Grep` rather than re-running.