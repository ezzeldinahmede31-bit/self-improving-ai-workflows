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
