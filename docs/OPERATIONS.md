# OPERATIONS — run/maintain the platform

## Daily
- `venv/bin/python scripts/device_health.py` -> expect READY (10/10).
- `device_audit.py verify` -> chain valid (also inside health).

## Run a task
- Write plan JSON (tools: bash|soundbox|sandbox|read|write|symbols|monitor_wait|cron_due; every step needs `verify`, destructive needs human).
- `device_loop.py run --plan p.json --task NAME` -> paused (ASK) or done.
- `device_loop.py approve SID STEP` (human) -> continues. `cancel SID` stops.
- `device_loop.py status SID` inspects. Sessions live under the PERSISTENT
  state root (`device_state.py where`; was /tmp before 2026-10-07).

## Schedule / watch
- `device_cron.py add --in/--every -- cmd...` (gated) -> `due` -> execute -> `ack`.
- `device_monitor.py start -- cmd` -> `poll ID --since N` -> `stop ID`.

## Backup (RPO = last backup, RTO = seconds; backups scrubbed of raw secrets)
- `device_state.py backup` -> `verify-backup <dir>` -> `restore <dir>`
  (atomic promote w/ rollback; invalid backups refused before touching live).
  `list-backups` (5 generations). State root: see `where` (persistent).
- Override for tests ONLY: `DEVICE_STATE_ROOT=<tmpdir>` (isolated fixtures;
  never production creds/profiles in tests).

## Benchmarks
- `device_e2e.py` (T1-T25, needs DISPLAY + net) -> e2e_report.json.
- `device_redteam.py` -> redteam_report.json.
- `pytest tests/test_device_platform.py` (selftests+redteam+health gate).
- Hardening round: `benchmarks/device_latency.py` -> latency_report.json;
  `benchmarks/device_concurrency.py` (1..100 x 5 modes) -> concurrency_report.json;
  `pytest tests/adversarial/test_hostile_child_agent.py` -> hostile_child_report.json;
  `pytest tests/e2e/test_browser_write_safe.py` (fixture app only) ->
  browser_write_report.json; `pytest tests/security/` (mcp trust, sandbox
  escape, secret sweep).

## Degraded mode
Health NOT_READY on critical (permissions/sandbox/storage/audit) -> stop
autonomous runs, fix, re-verify. DEGRADED (browser/gui/mcp down) -> run with
safe substitutes only if policy allows; never claim success for skipped tiers.
