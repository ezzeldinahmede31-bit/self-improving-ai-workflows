# Amendment B — Maximum Safe Parallelism (Phase 1, REQUIRED)

Status: DESIGN (implements alongside Amendment A; no artificial targets —
the system discovers per-project safe parallelism and measures it).

## B.0 Principle (user rule, verbatim intent)
More agents is NEVER the fix for unparallelizable tasks. The optimizer may
only expose parallelism that already exists safely; quality gates,
dependencies, file isolation, and controlled integration are inviolable.

## B.1 Safe-split analysis (post-decomposition, pre-scheduling)
A task is splittable ONLY when ALL hold (checked in code, not by LLM):
1. `splittable: true` AND `split_by: "files"` declared on the contract.
2. `file_groups`: disjoint lists whose union == `allowed_files`.
3. Every acceptance item references files inside ONE group only
   (items with no path or cross-group paths → UNSAFE → refuse split).
4. No `outputs` key is produced from more than one group (outputs are
   namespaced per sub-task; cross-group outputs → refuse).
Refusal is silent-safe: the task runs whole. Two tests lock both directions.

## B.2 Optimized DAG + metrics (`parallelism.py`)
- `optimize(contracts)` → rewrites splittable tasks into `<id>#1..n`
  sub-tasks (role/kind/policy inherited), rewires dependents to ALL sub-ids,
  returns `(new_contracts, splits_report)`.
- `project_metrics(contracts)` from explicit per-task `estimate_s`
  (default 60, always labeled ESTIMATE):
  `total_work=Σest`, `critical_path` (longest path by est),
  `critical_path_length`, `max_safe_parallelism` (widest Kahn level AFTER
  file-overlap edges), `theoretical_min_runtime=critical_path_length`.
- Edges ALWAYS include file-overlap serialization (dag.build_edges) — the
  scheduler enforces effective deps, not just declared ones.

## B.3 Concurrency caps (all three, no fixed agent counts)
- `max_concurrency` (global ceiling; constructor `max_workers` kept as alias).
- `max_concurrency_per_model` (per-model `max_parallel` in models.json).
- `max_concurrency_for_limited_models` (global ceiling across ALL limited).
- Dispatch per tick: `min(ready, global_cap, Σ per-model headroom)`,
  limited-models total additionally capped. Dynamic every tick.

## B.4 Primary-model saturation (within Amendment A, unchanged)
Unlimited Primary takes everything unless a task carries an explicit
`capability:` policy + allowance. Parallel fan-out does NOT route to limited
models to "go faster" — speed comes from safe structure, not quota burn.

## B.5 Measured speedup (`Orchestrator.report()`)
From store events (timestamps, honest MEASURED) + contract estimates
(labeled ESTIMATE):
- `baseline_sequential_estimate_s`, `critical_path{ids,length_s}`,
  `wall_clock_s` (project_created → project_finished),
  `actual_speedup = baseline_estimate / wall` (labeled estimate-based),
  `agent_utilization = Σ task_busy / (wall × distinct_workers)`,
  `model_usage` (attempts/fallbacks/limit_hits per model).
Dashboard snapshot includes counts + deferred + models.

## B.6 Test locks (all required by user)
safe-split runs parallel / unsafe-split refused / critical path numbers /
scheduler exploits all safe parallelism (overlap-timing proof) / N agents no
races (distinct files + worktrees, state consistent) / file-conflict pair
serializes (event-order proof) / QA fail blocks merge (already locked) /
routing+primary policy holds during parallel run (tasklog model assertions).
