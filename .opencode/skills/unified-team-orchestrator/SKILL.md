---
name: unified-team-orchestrator
description: "Single run-order that makes all installed skills work as one team with accuracy first. Use when a task spans several skills, when parallel lanes help, when speed must come from parallelism and caching instead of skipped checks, or when the user says 'كلهم يشتغلوا مع بعض'."
---

# Unified Team Orchestrator

## Purpose
One fixed run-order for every substantial task so the whole library
(1000+ skills), the parallel agents, and the gate pipeline act as one
team. Accuracy is never traded for speed: speed comes from parallel
lanes, caching, fail-fast ordering, and lossless context — never from
skipping a gate or a verification.

## When to use
Multi-skill tasks, multi-file builds, research-plus-build tasks, any
task where two or more lanes can run in parallel. Triggers: 'كلهم
يشتغلوا مع بعض', 'best accuracy quality speed', 'unified run',
'orchestrate all skills', 'parallel lanes'.

## The fixed run-order (never reorder, never skip)
1. **Reason** — one decomposition ladder (Problem, Constraints, Steps,
   Verify, Output) before anything else.
2. **Clarify contract** — search first, then one compact question round
   with defaults, then a 3-5 line Goal/Deliverable/Audience/Constraints/
   Done-when contract. No building before the contract.
3. **Triage fast** — state one line: primary skill + up to 2 supports.
   Library-first: scan the index, open full bodies ONLY for the chosen
   skills (manifest-first, lazy load). Never dump the whole library
   into context.
4. **Audience brief** — one PURPOSE/AUDIENCE line plus the psychological
   drivers that change the output. Technical tasks get the light pass
   (end user, trust, error clarity); user-facing tasks get the full pass.
5. **Best-practice baseline** — internal library first, then one bounded
   external pass (templates, repos, docs) when the domain is external.
   Adopt the strongest fit as the cited baseline, diff the user changes
   on top. From-memory design is forbidden when a lookup can find better.
6. **Plan + auto-split** — write the lane plan first. Split automatically
   into 2-4 independent lanes when subtasks share no files and no
   ordering. Design stays single-pass (one coherent design); only
   execution splits. One writer per file; worktree isolation when lanes
   touch overlapping areas.
7. **Execute lanes** — each lane gets only its files, signatures, and
   acceptance check. Surgical diffs only, per-lane validation before
   merge, integration check after merge, full suite on repo-touching work.
8. **Full gates, mandatory** — run `scripts/build_gates_pipeline.py`
   on every artifact. Exit 0 (READY_FOR_DEPLOYMENT) is the only pass.
   No skips, no grade-downs by severity or size.
9. **Delivery proof** — real execution with item counts and the agreed
   output, plus a REQ-to-evidence table. Validation green alone is never
   a delivery.
10. **Consolidate** — on substantial work: append principles, facts with
    evidence, failures with root cause, and recipes to memory, then
    re-encode and verify the match.

## Accuracy rules (hard)
- Gates run on everything, every time. A gate rejection is feedback,
  never worked around by reshaping the artifact.
- Security rejections are never auto-fixed; they route to the human.
- Counting answers need independent verification (second method or
  brute-force in a different representation); disagree-by-one means a
  boundary bug until proven otherwise.
- Dry-run evidence is required before any approval or deploy.
- Workflow stability means consecutive real runs with exact output match.
- Verdicts are PROVEN, HEURISTIC, or DISAGREEMENT — never 'I think'.

## Speed rules (accuracy-safe only)
- Fail-fast stage order: cheapest fatal checks (security, integrity,
  schema preflight) run before expensive ones.
- Schema cache preflight before generation; pinned data ready before
  dry-run; avoid-list from rejection history loaded before design.
- Attempt guard: stop repeated same-reason loops early and escalate
  instead of burning cycles.
- Parallel lanes for independent execution; sequential only for design
  and for dependent steps.
- Lossless context budget: drop chatter only, never identifiers,
  decisions, security notes, or requirements; rehydrate exact regions
  on demand.

## Auto-parallel protocol
- **Split when**: subtasks touch disjoint files, have no ordering, and
  each has its own acceptance check (schema plus API plus tests is the
  classic split).
- **Do NOT split**: the design itself, single-file edits, dependent
  steps, or anything needing one coherent vision.
- **Lane handoff**: file paths, function signatures, acceptance check.
  Nothing more; whole-file dumps defeat the budget.
- **Merge**: all lanes green plus integration check plus (on repo work)
  the full test suite. A lane that fails blocks the merge; fix or mark
  BLOCKED with the evidence.

## Verification (how the agent KNOWS it worked)
- Gates report exit 0 with READY_FOR_DEPLOYMENT on the artifact.
- The demo or delivery shows real execution output, not a validation
  screenshot.
- The REQ-to-evidence table has no unexplained FAIL or PARTIAL.
- Memory holds the session's durable lessons with evidence attached.

## Pairs with
compensatory-router, clarify-before-execute, omni-request-orchestrator,
best-practice-first-designer, subagent-task-delegator,
dispatching-parallel-agents, subagent-driven-development,
using-git-worktrees, zero-trust-modular-decomposer,
long-horizon-executor, single-pass-frontier-emulator,
swe-workflow, code-execution-guided-swemaster,
tdd-sandbox-proof-engine, surgical-diff-patch-editor,
autonomous-git-coworker, terminal-bash-executor-governor,
build-gates-pipeline, gate-first-pass-builder,
n8n-delivery-verification-gate, automation-known-issues-compass,
context-budget-governor, progressive-context-compressor,
evidence-over-memory, durable-experience-consolidator.
