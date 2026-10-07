# FINAL_GAP_MATRIX (AFTER) — every BEFORE gap closed or explicitly bounded

| BEFORE gap | Status | Proof |
|---|---|---|
| Compound-command evasion | CLOSED | split+worst-wins; T12 (9 variants DENY) |
| sudo/push-f/reset/chmod/IFS/abs-rm | CLOSED | normalization DENY; selftest 24/24 |
| Glob/Grep secret bypass | CLOSED | shared denies; selftest |
| Edit/Write no-deny paths | CLOSED | policy-file + ssh denies |
| Policy corrupt/rewritable | CLOSED | fail-closed load; atomic; policy self-deny |
| Self-approval | CLOSED | plan flags ignored; external tokens; R2-R4 |
| Sandbox net-ON/workdir open | CLOSED | net OFF default; containment; T13 |
| Sandbox no output cap/mem | CLOSED | 100KB cap; 1GB prlimit; die-with-parent |
| Monitor ungated/unkillable | CLOSED | gate; pgid+SIGKILL; deadline kills; GC |
| Monitor log unbounded | CLOSED | 1MB cap; 20-monitor cap |
| Cron ungated/races | CLOSED | gate; validation; caps; atomic; unique ids |
| Symbols ungated reads | CLOSED | Read-gate; 1MB cap; clean failures |
| Loop no metadata/cancel | CLOSED | full meta; cancel+pgid; taxonomy; audit |
| Loop unbounded retry | CLOSED | max3 backoff; destructive never retried |
| Resume trusts done[] | BOUNDED | idempotency keys for destructive; limitation noted |
| Advertised-but-absent tools | CLOSED | monitor_wait + cron_due implemented |
| No audit log | CLOSED | hash chain + redaction + flock; T21 |
| No atomic state/backup | CLOSED | device_state; T20 |
| Browser/GUI scripted loop | BOUNDED | non-intrusive closed-loop tests T5-T7; write-flows BLOCKED by boundary |
| MCP result trust | BOUNDED | content-gated; transport = limitation |
| No health/degraded | CLOSED | device_health READY 10/10 |
| No chaos/concurrency | CLOSED | R6/R8/T18/T19 |
| E2E only T1-T5 | CLOSED | T1-T25 (24 pass / 0 fail / 1 blocked) |
| No redteam | CLOSED | 10/10 |
| Docs/parity | CLOSED | 7 docs + this matrix |

Residual YELLOW (4, all documented): browser-write autonomy, full LSP,
malicious-child adversarial test, latency baselines.
