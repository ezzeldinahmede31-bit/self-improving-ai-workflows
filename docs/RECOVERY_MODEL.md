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
