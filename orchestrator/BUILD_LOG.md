# Orchestrator MVP — Build Log (issues found + fixed)

## 2026-09-16 — Phase 0 + parallel core + recovery
- **BUG-1 (real, found by test_worktree_isolation_and_merge):** every worktree
  task failed with `INTEGRATION_CONFLICT: 'NoneType' object is not
  subscriptable`. Root cause: `scheduler._merge_workdir` called the provider
  as `("merge", project, task, wt)` — 4 positionals — so the `wt` dict landed
  in the `work_dir` slot and `wt=None`. Fix: pass 5 args
  `("merge", project, task, work_dir, wt)`. Verified: 16/16 green after.
- **Design note:** `test_context_overflow` forces oversize dependency outputs
  through `details.outputs`; worker refuses with CONTEXT_OVERFLOW and the
  project continues — overflow is a task failure, never a stall.
- **Honest scope:** workers in MVP are local Python callables (mock agents).
  Real LLM workers, Temporal/LangGraph runtime, and the full dashboard UI are
  Phase 1+. Nothing here claims production readiness.

## 2026-09-16 — Phase 1: real opencode workers + gates QA + tasklog
- **Probe:** `opencode run --dir X -m <model> --format json "prompt"` spawns a
  fresh disposable session per invocation (verified live: smoke session
  ses_f56be90a wrote hello.txt, RC=0, cost 0). No --continue => no history.
- **FALSE ASSUMPTION (mine, corrected by live evidence):** bare `subprocess`
  in a .py and even `sk-...` + metadata-IP in a .txt are gates-READY; the
  security gate is workflow-shape-oriented. A small n8n workflow JSON with an
  unauthenticated webhook + bare $json IS rejected (REJECTED_SECURITY_RISK) —
  adopted as the reject-fixture (BAD_WORKFLOW in tests).
- **BUG-2:** Phase-1 scheduler edit broke MVP parallel test (gates QA added
  seconds per task). Fix: MVP helper defaults gates=False; gates covered in
  Phase-1 tests. Suite green again.
- **Side effects (by design, contained):** each gates run writes one audit
  JSON to memory/audits; tests delete the ones they create. No pattern/
  attempt/complaint writes (all disabled via flags).
- **Live runs (5 sessions, all titled orch-<task>):** la/lb parallel DONE
  (13-14s each, distinct sessions); lf QA_FAIL->retry (new session)->
  QA_FAIL->ESCALATED; lr DONE 16s after lease-expiry recovery. Tasklogs kept
  under /tmp/pytest-of-ezzeldin/pytest-21 (evidence above).

## 2026-09-16 — Research capability (permanent stage)
- **BUG-3 (real, found by live demo):** generate_report crashed when the
  research/ dir didn't exist (FileNotFoundError). Fix: makedirs in the
  generator. Locked by test_report_creates_missing_dirs.
- **Discipline check passed:** YOURLS-dated-UI (1 qualifying source) and
  Kutt-slowdown (single opinion) were correctly NOT promoted to repeated;
  only Shlink-analytics x2 qualified. Dub AGPL reuse correctly REVIEW-blocked.

## 2026-09-16 — E2E gap closure: research->synthesis->build on real workers
- **BUG-4 (test design, caught live):** "impossible" trap used a forbidden
  STRING visible in the worker prompt (acceptance text is shown to workers by
  design) — the agent smartly wrote it and passed. Fixed trap to structural
  impossibility (acceptance demands a file outside allowed_files).
- **BUG-5 (mine, router):** capability-fallback to primary didn't set
  fallback_used when primary headed the candidate list. Fixed with
  limited_skipped tracking.
- **BUG-6 (mine, router):** model_type() disagreed with select() in
  passthrough mode (limited vs unlimited) -> global limited cap serialized
  everything. Fixed: passthrough reports unlimited consistently.
- **BUG-7 (test naming):** order tracker keyed by worker name but asserted by
  task id (KeyError). Fixed to record task ids.
- **BUG-8 (mine, real):** two syntax errors from fast edits (scheduler
  paren, state.py merged lines). Fixed, suite green.
- **Live finding:** primary resolved BY RULE to muse-spark-1.2-
  contributor-free (not 1.3) — zero-cost + toolcall + largest context. All 6
  live attempts default-primary, 0 fallbacks, 0 limit-hits. Rule-based
  discovery vindicated (no hardcoded name would have picked this).

## 2026-09-16 — Safe-Split Optimizer + gap closures (timeout/kill/KB)
- **BUG-9 (mine):** apply_split emitted float estimate_s (round(x,1)) but
  schema requires int -> live submit crashed. Fixed: int(round()).
- **Test-scenario fix (mine):** makespan-gain test put the split task OFF the
  critical path (gain math correctly 0). Fixed scenario: big task ON the
  critical path (gain 120s in fixture).
- **KB improvement:** naive tokens missed plurals ("shorteners" vs
  "shortener", Jaccard 0.2). Added len>4 trailing-s stemming (0.4, over
  0.35 threshold); far topics still None.
- **Runner refactor:** subprocess.run -> Popen + spawn_hook operability hook;
  new WORKER_KILLED reason (rc<0) and SPAWN_FAILED; execute_ maps through.
  Existing crash test updated to the sharper reason (improvement, not regress).
