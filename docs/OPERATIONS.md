# OPERATIONS — run/maintain the platform

## Daily
- `venv/bin/python scripts/device_health.py` -> expect READY (10/10).
- `device_audit.py verify` -> chain valid (also inside health).

## Run a task
- Write plan JSON (tools: bash|soundbox|sandbox|read|write|symbols|monitor_wait|cron_due; every step needs `verify`, destructive needs human).
- `device_loop.py run --plan p.json --task NAME` -> paused (ASK) or done.
- `device_loop.py approve SID STEP` (human) -> continues. `cancel SID` stops.
- `device_loop.py status SID` inspects. Sessions: /tmp/opencode-device/state/sessions/.

## Schedule / watch
- `device_cron.py add --in/--every -- cmd...` (gated) -> `due` -> execute -> `ack`.
- `device_monitor.py start -- cmd` -> `poll ID --since N` -> `stop ID`.

## Backup (RPO = last snapshot, RTO = seconds)
- `device_state.py snapshot` -> `restore <dir>`. State root: /tmp/opencode-device/state.

## Benchmarks
- `device_e2e.py` (T1-T25, needs DISPLAY + net) -> e2e_report.json.
- `device_redteam.py` -> redteam_report.json.
- `pytest tests/test_device_platform.py` (selftests+redteam+health gate).

## Degraded mode
Health NOT_READY on critical (permissions/sandbox/storage/audit) -> stop
autonomous runs, fix, re-verify. DEGRADED (browser/gui/mcp down) -> run with
safe substitutes only if policy allows; never claim success for skipped tiers.
