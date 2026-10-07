# COWORK_PARITY — behavior comparison (GREEN/ YELLOW/ RED, evidence-linked)

GREEN = implemented + integrated + tested. Evidence: selftest/e2e/redteam/pytest.

| Capability | Verdict | Evidence |
|---|---|---|
| Files Read/Write/Edit/Search | GREEN | loop tools + gate; T22; selftests |
| Bash + compound-shell understanding | GREEN | split+normalize; T11/T12 (12 variants) |
| Permissions Deny>Ask>Allow | GREEN | 24-case selftest + R9 + opencode.jsonc native |
| Scoped/single-use approvals | GREEN | R2-R4; T10 |
| Sandbox fs/net/process isolation | GREEN | T13 + selftest (net cut, workdir refusal) |
| Browser read + persistent login | GREEN | T2/T3 + LinkedIn feed proof (prior session) |
| Browser write flows | YELLOW | T4 BLOCKED: out of autonomous scope by user boundary |
| Browser write (safe fixture) | GREEN | tests/e2e/test_browser_write_safe.py 19/19 on isolated app + disposable profile (production autonomy boundary unchanged) |
| GUI observe-act-verify | GREEN | T6/T7 + LinkedIn navigation proof |
| Screenshots safety | GREEN | /tmp only, no secrets asserted, gitignored state |
| Monitor | GREEN | start/poll/stop/deadline/kill; T9 |
| Cron | GREEN | add/due/ack/del, gated, caps; T25 |
| LSP | YELLOW-OPTIONAL | LSP-lite honest (no import resolution); full LSP NOT REQUIRED by current workload (no workflow needs rename/workspace-symbols/type-info) |
| MCP results as untrusted | GREEN | T15 + ResultVerifier journal; explicit server trust allowlist (mcp_trust 11/11) |
| Subagents constrained | GREEN | hostile child-agent suite 25/25 (real loop sessions, 0 FAIL_OPEN); token session-binding; fd/env sanitized |
| Worktrees/isolation | GREEN | pre-existing using-git-worktrees + sandbox |
| Sessions/resume/cancel | GREEN | T10/T19 + cross-process proof |
| Recovery/chaos | GREEN | T5/T7/T8/T9 + R6/R8 |
| Prompt-injection resistance | GREEN | T14 + R1-R7 (10/10 redteam) |
| Secret protection | GREEN | T16 + denies + redaction |
| Exfiltration protection | GREEN | T17 gate; full flow-tracking = limitation |
| Observability/audit | GREEN | hash chain + verify + T21 |
| Concurrency | GREEN | T18 (5 parallel) + full matrix to 100 tasks x 5 modes: 0 errors/lost/corrupt/dup/deadlock |
| Resource governance | GREEN | caps everywhere; T23 |
| Backup/restore | GREEN | T20 + atomic scrubbed backups w/ verify + rollback (roundtrip/corruption/atomic/no-secrets tests) |
| Persistent state | GREEN | XDG persistent root, atomic+fsync+checksums, restart/reboot/concurrency/corruption/perms tests 10/10 |
| Human approval (meaningful) | GREEN | tokens show session/step/command; approve/deny/timeout paths |
| E2E mixed workflow | GREEN | T22 + T25 |
| Real workloads | GREEN | T1 (build+test+commit), T25 |
| Performance baselines | GREEN | latency_report.json (permission/state/audit/sandbox/browser/shot) + concurrency matrix to 100; thresholds derived as 5x observed p95 (informational) |
| Reproducibility | GREEN | venv + pinned stdlib-only device scripts (no new deps) |

RED: none. YELLOW-OPTIONAL (1): full LSP (not required by current workload).
Browser-write PRODUCTION autonomy stays BLOCKED by standing user boundary
(safe-fixture proof does not widen scope). No marketing claims: see reports.
