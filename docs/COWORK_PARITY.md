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
| GUI observe-act-verify | GREEN | T6/T7 + LinkedIn navigation proof |
| Screenshots safety | GREEN | /tmp only, no secrets asserted, gitignored state |
| Monitor | GREEN | start/poll/stop/deadline/kill; T9 |
| Cron | GREEN | add/due/ack/del, gated, caps; T25 |
| LSP | YELLOW | LSP-lite honest (no import resolution); real LSP via `occ` future |
| MCP results as untrusted | GREEN | T15; transport-trust documented limitation |
| Subagents constrained | YELLOW | same engine reused; cross-process child policy = parent policy by construction; dedicated malicious-child test = limitation (documented) |
| Worktrees/isolation | GREEN | pre-existing using-git-worktrees + sandbox |
| Sessions/resume/cancel | GREEN | T10/T19 + cross-process proof |
| Recovery/chaos | GREEN | T5/T7/T8/T9 + R6/R8 |
| Prompt-injection resistance | GREEN | T14 + R1-R7 (10/10 redteam) |
| Secret protection | GREEN | T16 + denies + redaction |
| Exfiltration protection | GREEN | T17 gate; full flow-tracking = limitation |
| Observability/audit | GREEN | hash chain + verify + T21 |
| Concurrency | GREEN | T18 (5 parallel, no corruption) |
| Resource governance | GREEN | caps everywhere; T23 |
| Backup/restore | GREEN | T20 |
| Human approval (meaningful) | GREEN | tokens show session/step/command; approve/deny/timeout paths |
| E2E mixed workflow | GREEN | T22 + T25 |
| Real workloads | GREEN | T1 (build+test+commit), T25 |
| Performance baselines | YELLOW | R10 (5MB<5s) + caps; no full latency table (limitation) |
| Reproducibility | GREEN | venv + pinned stdlib-only device scripts (no new deps) |

RED: none. YELLOW (4): browser-write autonomy, full LSP, malicious-child
adversarial test, latency baselines. No marketing claims: see reports.
