# DEVICE_ARCHITECTURE — Linux X11 Agentic Device Platform

## Loop (single, central)
`scripts/device_loop.py v2`: PLAN -> INSPECT -> DECOMPOSE -> SELECT TOOL ->
CHECK TRUST -> PERMISSION -> EXECUTE -> OBSERVE -> VERIFY -> SUCCESS? NEXT :
DIAGNOSE -> RECOVER -> VERIFY -> RETRY(max3, backoff, never-destructive) /
ESCALATE / FAIL-CLOSED -> FINAL VERIFY -> DONE.
Step metadata: step_id/task_id/session/parent/ts/tool/permission/verdict.
State: atomic via device_state, per-step persist, idempotency keys for
destructive steps. Caps: 50 steps, 900s default deadline.

## Tool routing (least-privilege order, reasoned not hardcoded)
1. Connector/native (read/glob/grep, MCP/firecrawl) — fastest, auditable.
2. Browser (Playwright MCP persistent profile; real-Chrome CDP fallback).
3. Desktop GUI (wmctrl/xdotool/screenshots) — last resort, Ask-first,
   focus restored. The loop records WHY a tier was chosen in step meta;
   GUI when connector suffices is a policy violation (ask).

## Components
- permissions: device_permissions.py (Deny>Ask>Allow, compound-split,
  normalization, scoped single-use approvals) + opencode.jsonc native block.
- sandbox: device_sandbox.py (bwrap, net OFF default, contained workdir,
  pre-launch gate, output cap, die-with-parent, 1GB prlimit).
- monitor: device_monitor.py (gated start, pgid kill, deadline kills, GC).
- cron: device_cron.py (gated add, validated, capped, atomic).
- symbols: device_symbols.py (gated 1MB reads, capped scan, honest LSP-lite).
- audit: device_audit.py (hash chain, redaction, flock).
- state: device_state.py (atomic, quarantine, idempotency, backup/restore).
- health: device_health.py (READY/DEGRADED/NOT_READY).
- redteam: device_redteam.py (10 attacks). e2e: device_e2e.py (T1-T25).

## Runtime paths
Code: scripts/*.py (venv python3.12). State: /tmp/opencode-device/
(sessions, monitors, cron via state/, approvals, audit.jsonl, reports).
Profiles/secrets: memory/.sessions (0700, gitignored) — never in state/.
