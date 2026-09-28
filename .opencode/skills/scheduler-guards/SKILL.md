---
name: scheduler-guards
description: "Scheduler guard skill (wait-graph cycle detection, starvation aging, perf-memory ranking). Use when tasks may wait on each other, when a task never gets served, or when scheduler choice needs success/latency/cost evidence. Trigger phrases: 'deadlock check', 'starved task', 'best agent for', 'حراس المجدول'."
---

# Scheduler Guards (Cycles Named, Starvation Aged, Choice Ranked)

Code: `scheduler_guards.py` (stdlib only, advises — scheduler
enforces). `find_cycle()` names dependency loops; `StarvationWatch`
clocks waits and flags past-ceiling tasks oldest-first with priority
boost; `PerfMemory` keeps rolling success/latency/cost/error stats and
`best_for()` ranks within cost/success floors.

## Verification

- `tests/test_p2b_guards_golden.py` guards third green (cycle, self
  loop, aging, ranking, floors).
- No schedule ships with an unnamed cycle or an unflagged starved task.

## Pairs with

`orchestrator/scheduler` (enforcement point), `model-benchmark-harness`
(evidence), `capacity-planning` (load view), `build-gates-pipeline`.
