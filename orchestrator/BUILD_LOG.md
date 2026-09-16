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
