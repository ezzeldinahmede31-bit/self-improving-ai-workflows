# FINAL_GAP_MATRIX_BEFORE — architecture audit (pre-implementation)

Date: 2026-10-07. Method: independent subagent audit of all 7 device scripts
+ manual checks (auto-commit scan, MCP/browser/GUI paths, docs dir).
Rule: file/class/function existence is NOT evidence. Only E2E is.

## Capability matrix

| Capability | Existing implementation | Integration path | Test | Evidence | Gap |
|---|---|---|---|---|---|
| Permission gate (Bash) | device_permissions.py fnmatch | loop run_step, CLI | selftest 9/9 | real runs | **GAP: compound cmds (`;`,`&&`,`\|`) evade; `sudo rm`, `push -f`, `reset --hard`, `${IFS}`, `/bin/rm` variants missed; broad-ASK shadows specific-ALLOW trap** |
| Permission gate (Files) | Read denies only | loop read/write | selftest | real runs | **GAP: Glob/Grep have zero denies (`.env` readable via grep); Edit/Write no deny paths (policy file itself writable); symlink/`..` variants** |
| Policy integrity | JSON on disk, auto-created | load_policy() | none | — | **GAP: corrupt JSON crashes (DoS); attacker with Write can rewrite policy; non-atomic write** |
| Scoped approvals | none (plan `"approved":true` = self-approval) | loop | selftest uses it | — | **GAP: self-approval defeats ASK; no expiry, no replay protection, no task/session binding** |
| Sandbox fs/net isolation | device_sandbox.py bwrap | loop sandbox tool | selftest (echo + egress) | real runs | **GAP: net ON by default; workdir attacker-controlled (`/` allowed); no output cap; no die-with-parent; no mem cap; selftest vacuous offline** |
| Monitor | device_monitor.py fork collector | none (loop lists it, unimplemented) | selftest | real runs | **GAP: no permission check; PID-reuse liveness; deadline never kills; SIGTERM-only (pgid escape); id traversal; unbounded log/count; stop doesn't GC; starter/collector race truncates log** |
| Cron | device_cron.py JSON | none (loop lists it, unimplemented) | selftest | real runs | **GAP: no permission check; negative ints; no caps; non-atomic; uuid[:8] collision; selftest wipes prod state; ack stamps post-hoc** |
| Symbols/LSP-lite | device_symbols.py ast | loop symbols tool | selftest | real runs | **GAP: ungated reads (`.env`); unbounded files/hits; crashes on syntax errors; no import resolution (documented)** |
| Unified loop | device_loop.py drive() | CLI run/resume/approve | selftest | real runs | **GAP: no step metadata (task/parent/timestamps); no cancel; unbounded retries/deadline; write-redirect gaps (`> ~/.ssh/...`); sandbox net-ON default; resume trusts done[]; monitor/cron tools advertised but absent** |
| E2E benchmark | device_e2e.py T1-T5 | CLI | live 5/5 | report JSON | **GAP: only T1-T5; T5 extraction misses variants; rm-marker tautology; no T6-T25** |
| Audit log | none (immutable-audit-log is a skill doc) | — | — | — | **GAP: no hash-chained log; no secret redaction** |
| Atomic state/backup | none | — | — | — | **GAP: all state via bare write_text; no backup/restore** |
| Cancellation | monitor stop only | — | — | — | **GAP: no loop cancel; children escape (pgid)** |
| Retry policy | sleep(1) unbounded --max-retries | loop | — | — | **GAP: retries destructive too; no backoff; no classification** |
| Browser closed-loop | playwright MCP + profiles + prior LinkedIn proof | manual | screenshots | prior session | **GAP: no scripted closed-loop (observe-act-verify) module; login re-proof intrusive** |
| GUI closed-loop | desktop-gui-controller skill + prior proof | manual | screenshots | prior session | **GAP: no scripted module; stale-coordinate risk unhandled in code** |
| MCP security | none in device path | — | — | — | **GAP: MCP results treated as untrusted only by convention; no validator** |
| Subagents policy | Task tool (opencode) | — | — | — | **GAP: child-constrains-parent not enforced in code** |
| Secret protection | policy denies on Read | partial | selftest | real | **GAP: no redaction in logs/outputs; Glob/Grep bypass** |
| Exfiltration | none | — | — | — | **GAP: no data-flow tracking LOCAL->TOOL->DEST** |
| Observability/metrics | per-tool stdout | — | — | — | **GAP: no unified trace/metrics** |
| Health/degraded | none | — | — | — | **GAP: none** |
| Resource governance | timeouts only | partial | — | — | **GAP: no CPU/RAM/count caps** |
| Chaos/concurrency | none | — | — | — | **GAP: none** |
| Docs/parity matrix | claude-device-use SKILL.md | router | — | — | **GAP: no SECURITY/THREAT/RECOVERY/OPERATIONS docs** |
| Full pytest | 1123 passed | CI | real | run output | OK (1 pre-existing failure fixed last round) |

## Bypass inventory (must-fix before GREEN)

1. Chained shell (`; && || | $() >`) evades string-match gate.
2. `sudo rm`, `git push -f/--force-with-lease`, `git reset --hard`, `chmod 777`, `${IFS}`, absolute-path binaries.
3. Secret reads via Glob/Grep/Bash-cat; policy file writable.
4. Self-approval via plan JSON; approval replay across commands/sessions.
5. Sandbox net-ON default; workdir `/`; TOCTOU file swap post-approval.
6. Monitor/cron zero-gate; cron state races; monitor kill escapes pgid.
7. Session `done[]` trusted on resume; non-atomic saves; no idempotency keys.
8. Loop advertises unimplemented tools (monitor/cron/browser/gui).

## Decision

Fix all of the above in this round. Intrusive-on-user proofs (browser login
write flows, multi-app GUI) stay evidence-backed from prior session +
non-intrusive re-verification; marked BLOCKED-with-reason where live action
would hijack the user's active desktop, never fake-PASS.
