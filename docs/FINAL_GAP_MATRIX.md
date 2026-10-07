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

## Hardening round 2026-10-07 (this mission) — deltas
| Gap | Status | Proof |
|---|---|---|
| Volatile /tmp state | CLOSED | persistent root (XDG_STATE_HOME or ~/.local/state), atomic tmp+fsync+rename, fcntl locks, checksums, schema v1 + migrations, 0700/0600 enforced; tests/test_device_state_durable.py 10/10 |
| Backup/restore naive | CLOSED | deterministic scrubbed backups + manifest, verify_backup, atomic restore w/ rollback, 5 generations; roundtrip/corruption/atomic/no-raw-secrets tests |
| once() duplicate grant race | CLOSED (bug found by bench) | single-LOCK_EX read-modify-write; concurrent-once test: exactly 1 grant |
| _repair_perms O(tree) per write | CLOSED (bug found by bench) | throttled to 1/hour; p50 load-100 back to ~2.3s parallel |
| Malicious-child test | CLOSED | tests/adversarial/test_hostile_child_agent.py: 25 real vectors, 0 FAIL_OPEN; hostile_child_report.json |
| Browser-write autonomy | CLOSED (safe scope) | tests/e2e/test_browser_write_safe.py on isolated fixture app (disposable profile/account): 19/19 PASS/BLOCKED; production T4 autonomy boundary UNCHANGED (still BLOCKED by user scope) |
| Latency baselines | CLOSED | benchmarks/device_latency.py + latency_report.json (permission/state/audit/sandbox/browser/screenshot) |
| Concurrency to 100 | CLOSED | benchmarks/device_concurrency.py: 80 rows (5 modes x 6 loads x reps), 0 errors/lost/corrupt/dup/deadlock; concurrency_report.json |
| MCP trust = TLS only | CLOSED | scripts/mcp_trust.py + allowlist policy: unknown DENY, new ASK, trusted ALLOW-in-grant, cap widening needs re-auth; pin/hostname/expiry/revocation; tests/security/test_mcp_trust.py 11/11; mcp_trust_report.json |
| bwrap depth | CLOSED (honest scope) | sanitized env, NEVER_WORKDIRS, prlimit AS+CPU (NPROC omitted: breaks userns here, documented), close_fds; escape suite 10/10; "isolation, NOT MAC" stated |
| Secrets in state/backups/audit | CLOSED | backup scrub->references, audit redaction, sweep test; test_secret_protection.py |
| Full LSP | OPTIONAL / NOT REQUIRED | device_symbols.py (AST defs/info/refs) serves every current workflow (T22, bench mixed mode); no workflow needs rename/workspace-symbols/type-info; no full LSP built (scope discipline) |

Residual YELLOW (1, documented): full LSP (optional, not required by current
workload). No RED. No known undocumented bypasses.
