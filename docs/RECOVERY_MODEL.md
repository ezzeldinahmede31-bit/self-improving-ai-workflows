# RECOVERY_MODEL — detect/persist/recover/verify for every failure class

| Failure | Detect | Persist | Recover | Verify | Test |
|---|---|---|---|---|---|
| Command fail | exit code | step log | bounded retry w/ backoff (non-destructive) | verify spec | T1 |
| Browser nav fail | exception/timeout | e2e log | retry known-good | content assert | T5 |
| GUI focus fail | wmctrl rc | screenshot | refocus known window | fresh shot | T7 |
| Network cut | socket error | step log | retry outside sandbox | content assert | T8 |
| Process crash | poll exited+!alive | monitor meta | restart, re-poll | lines present | T9 |
| Session crash/kill | state file status | atomic session | resume SID in new proc | done[] + artifacts | T10 |
| Deadline | poll timestamp | meta ended-deadline | kill pgid, report | status | monitor selftest |
| Cancel | status flag | canceled state | kill children, release | status query | T19 |
| Corrupt state | JSON parse fail | quarantine file | restore from backup | roundtrip read | T20/state selftest |
| Destructive risk | gate DENY | audit event | NO retry, fail-closed | attempts==1 | T24 |

Rules: destructive ops never retried; resume never re-executes completed
destructive steps (idempotency); recovery never performs a destructive op
twice (R6). Cancel stops children (pgid) and persists canceled status.

## Durable state + backup (hardening round 2026-10-07)
- Authoritative root: `$DEVICE_STATE_ROOT`, else `$XDG_STATE_HOME/opencode-device`,
  else `~/.local/state/opencode-device` (persistent, 0700; files 0600).
  Legacy /tmp state migrated once; /tmp is NOT authoritative (transient only).
- Write path: tmp + fsync + atomic rename + dir fsync, fcntl per-file locks,
  .sha256 sidecars, schema envelope v1; failures quarantine + fail closed.
- Backup: `device_state.py backup` -> deterministic dir (scrubbed state +
  manifest.json w/ checksums + schema). `verify-backup <dir>`, `list-backups`
  (keeps 5 generations). Restore: candidate -> full validate -> promote with
  rollback park; invalid backup NEVER touches live state.
- Reboot proof: process A writes -> dies -> process B loads+continues
  (test_state_survives_process_restart / _simulated_reboot); restart-safe
  resume via idempotency keys (exactly-once grants under concurrency).
