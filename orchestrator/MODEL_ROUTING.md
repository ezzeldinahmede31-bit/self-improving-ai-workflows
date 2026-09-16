# Amendment A — Model Routing & Quota Policy (Phase 1, REQUIRED)

Status: DESIGN APPROVED-PENDING (implementation paused until user confirms).
Parent doc: Architecture §15 (Model/Provider Abstraction) — this amendment
replaces its "cheap vs strong" heuristic with a quota-aware router.

## A.0 Environment facts (verified live 2026-09-16, not assumed)
- `opencode models --verbose` returns a machine-parseable catalog: 69 entries,
  each `opencode/<id>` + JSON `{status, cost{input,output,cache}, limit{context},
  capabilities{...}}`. This is the discovery source — no model names or
  counts are hardcoded anywhere.
- `opencode/muse-spark-1.3-contributor-free`: cost 0/0/0, ctx 1M, toolcall
  capable → the Unlimited Primary in this environment (identified by RULE,
  not by name: cheapest active toolcall-capable model with zero cost).
- `opencode stats --models` reports usage AFTER the fact (tokens/cost per
  model). There is NO quota/remaining-quota API.
- Therefore: quotas are USER-CONFIGURED, catalog/capabilities are DISCOVERED
  live, and limit-hits are RUNTIME-DETECTED (429 / rate-limit / quota /
  payment patterns in worker stderr) → mark model unavailable → fallback.

## A.1 Chain of command
`Scheduler → Model Router → Worker → OpenCode/Subagent`
The Scheduler never picks a model; the Worker never picks a model. Only the
Router decides, per task attempt, and records why.

## A.2 Model registry (`models.json`, user-owned config, no hardcoding)
```json
{
  "primary_rule": "cheapest active toolcall-capable model with zero cost",
  "primary_override": null,
  "models": {
    "<id from live catalog>": {
      "type": "unlimited | limited",
      "max_parallel": 4,
      "capabilities": ["toolcall", "reasoning", "vision"],
      "allow_without_capability_need": false
    }
  },
  "policies": {"defer_when_primary_unsuitable": true}
}
```
- Unknown models default to `limited, max_parallel=1,
  allow_without_capability_need=false` (fail-closed: never burn unknown quota).
- `primary_override` lets the user pin the primary by name; otherwise the
  `primary_rule` resolves it from the live catalog at startup (and re-checks
  on catalog refresh).

## A.3 Per-task selection (per-task, never global)
Contract gains: `model_policy: "auto" | "primary-only" | "capability:<name>"`.
1. `primary-only` (DEFAULT) → Primary, reason=`default-primary`.
2. `capability:<name>` → cheapest ACTIVE model with that capability AND
   (`type=unlimited` OR explicit per-task allowance). A limited model is used
   ONLY here. reason=`capability-need:<name>`.
3. If the chosen limited model is in cooldown (recent limit-hit) or its
   in-flight count == max_parallel → try next eligible; none left →
   - if Primary can serve (capability subset check passes) → Primary with
     `fallback_used=true`, reason=`limited-unavailable-fallback`;
   - else → task goes DEFERRED (new status; scheduler skips; explicit
     `release_deferred()` re-queues). Never busy-loop on quota.

## A.4 Quota protection (parallelism cannot burn quota randomly)
- Per-model in-flight semaphore (`max_parallel`); acquire BEFORE spawn,
  release after attempt ends (even on crash/timeout — finally-block).
- Usage ledger in StateStore (`model_usage`: model/date/attempts/fallbacks/
  limit_hits) + cooldown map (in-memory + persisted `cooldown_until`).
- Limit-hit patterns matched on worker stderr
  (`429|rate.?limit|quota|limit.?exceed|payment|billing|unavailable`):
  mark cooldown (default 15 min, configurable), force fallback for the
  in-flight attempt's retry, record `limit_hit` event.
- Effective dispatch cap per tick =
  `min(ready_tasks, max_workers, Σ eligible_model_headroom)`.

## A.5 State recording (per attempt, in store + tasklog)
`task_id, model, model_type, attempt, selection_reason, quota_status
(ok|cooldown|fallback|deferred), fallback_used (bool)`.
Stored in: task `details.attempts_log[]`, `task_model_selected` /
`task_model_fallback` / `task_deferred` events, and the tasklog JSONL line.

## A.6 Statuses
Add `DEFERRED` (terminal-ish but releasable): scheduler ignores it;
`release_deferred(project_id, reason)` → PENDING. Dashboard shows deferred
count + blocking model. Quota refresh is manual or cooldown-expiry driven —
never polled against a nonexistent API.

## A.7 Parallelism rule (answers the fixed-number question)
Worker count is ALWAYS `min(len(ready), max_workers_cap, model_headroom)`.
`max_workers_cap` is an operator safety ceiling (default = CPU-ish small
number, configurable), NOT a target. No fixed "10 agents" anywhere.

## A.8 Implementation plan (when resumed)
1. `orchestrator/models.py`: catalog parser (`opencode models --verbose`),
   registry loader/validator, Router.select() + semaphores + cooldowns.
2. `state.py`: `model_usage` table, DEFERRED status, attempts_log in details,
   release_deferred().
3. `schema.py`: `model_policy` field + validation.
4. `scheduler.py`: route through Router; DEFERRED skip; record A.5 fields.
5. `tasklog.py`: model fields in every line.
6. Tests (local): router selection matrix (fake catalogs), semaphore caps,
   cooldown→fallback, defer→release, unknown-model fail-closed, prompt still
   task-only. Tests (live, `-m live`): 1 limited-model capability task IF the
   user explicitly allows (else skipped by policy — documented, not mocked);
   limit-hit fallback via forced-bad-model config (proves the PATH without
   burning real quota); primary default on normal tasks (already proven).
7. Docs: `models.json.example` + dashboard model/quota panel fields.
