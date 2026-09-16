# Open-Source Benchmark & Selective Integration (2026-09-16)

All facts below were verified live (GitHub API + shallow clones + targeted
code reads), not taken from marketing copy.

## Comparison table

| Project | Relevant component | Ours | Theirs | Better? | Reusable? | License | Recommendation |
|---|---|---|---|---|---|---|---|
| tctinh/agent-hive (opencode-hive) | per-agent models, sessions.json, 18 MCP tools | model router (designed), SQLite store | per-agent model config in JSON; compaction re-anchor via sessions.json; 6 TS unit tests + release tests | Ideas equal/validating; store stronger than sessions.json | NO (TS + license NOASSERTION — legally unsafe to copy) | Unclear (NOASSERTION) | Do NOT take code; per-agent routing already in Amendment A |
| nwiizo/ccswarm | NDJSON audit, --max-budget-usd, multi-provider | tasklog JSONL, timeouts, prompt caps | 301 Rust unit tests; budget caps; replayable runs | Engineering-serious but ideas overlap ours | NO (Rust ≠ our Python stdlib stack) | MIT | Ideas only; no budget flag exists in `opencode run` (documented limit) |
| gitpcl/openorchestrator | file-overlap guard, merge queue, prompt budgets, worktree cleanup | schedule-time overlap edges, immediate merge, hard prompt refusal, finally-cleanup | RUNTIME overlap check across live worktrees; merge ordering; priority-section prompts; stale-worktree reaper service; 65 test files | YES (2 spots) | YES (ideas re-implemented, not pasted) | MIT | ADOPT: stale-worktree reaper + merge-time live-overlap assert |
| rjben/swarm-git | opencode adapter (build_command/is_done) | --dir, --format json, RESULT.json, budgets, timeouts | 28-line adapter, no workdir binding, string-match done | NO — ours strictly stronger | NO | MIT | Nothing to take; 1483 lines total, thin tests |
| Nistro-dev/opencode-mad | file ownership, hard constraints, 10 roles | allowed_files enforced in code + secret scan | prompt-markdown pack, zero code tests, stale since Feb 2026 | NO (prompts, not code) | NO | MIT | Ownership idea already ours |
| Open-Document-Alliance/Agent-Review-CLI | review pipeline | gates QA | review-only, no scheduler/DAG, no tests, stale | NO | NO | MIT | Nothing |
| Untrivial-ai/agent-orchestrator | supervision platform | deterministic core | 12k★ Go monorepo (280MB) + frontend | Out of scope (stack + weight) | NO | Apache-2.0 | Ideas only |
| awslabs/cli-agent-orchestrator | tmux supervision, graph/ | ThreadPool + leases | graph/ = telemetry, not task DAG; Apache | Partial validation only | NO | Apache-2.0 | Nothing concrete |
| nekocode/agent-worktree | worktree tool | gitiso.py | Rust CLI | Covered | NO | MIT | Nothing |
| kdcokenny/opencode-background-agents | async delegation | disposable sessions | 49KB TS plugin | Unknown depth | NO | MIT | Skip (no evidence of more) |

## Adopted (implemented + tested, our architecture kept)
1. **Stale-worktree reaper** (`gitiso.reap_stale`) — crashed runs leak
   `wt/*` branches + dirs (our finally-cleanup misses kills). Reaps only
   `wt/`-prefixed branches and dirs not in the active set; never touches
   user branches. Idea from openorchestrator's cleanup service.
2. **Merge-time live-overlap assert** (`scheduler` pre-merge check) — even
   with schedule-time edges, refuses a merge when another RUNNING task's
   `allowed_files` intersect the changed set. Defense-in-depth; mirrors
   openorchestrator's runtime overlap check.

## Evaluated and REJECTED (with reason)
- Priority-drop prompts (openorchestrator): our hard prompt refusal is SAFER
  than silent truncation of load-bearing inputs. Keep refusal.
- Immediate-copy of any file: all adopted items re-implemented in our style
  + our tests; zero pasted lines (license-hygiene + fit).
- agent-hive code: NOASSERTION license = no-go regardless of quality.
