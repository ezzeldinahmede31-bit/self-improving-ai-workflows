---
name: chain-integrity-checker
description: "Cumulative per-step consistency verification for multi-step plans/DAGs produced by weak models. AFTER each DAG step is added, make a SEPARATE narrow call (same cheap model) that reviews ONLY the completed steps + the new step and answers a mandatory JSON contract: {contradicts_previous, contradiction_details, skipped_dependency, confidence}. If contradicts/skipped → return to the planner, do NOT continue. Preserves correctness under long context where small models otherwise forget or self-contradict. Use while building n8n workflows, plans, or any chain of dependent steps."
---

# CHAIN INTEGRITY CHECKER PROTOCOL

## DIRECTIVE

A small model does not err because it is "dumb" — it errs because long context
makes it forget or contradict itself. Fix: SEPARATE execution from review. Each
new step gets a dedicated, narrow verification call — accumulated along the way,
not only at the end.

## PER-STEP CONTRACT

After ANY node/step is added to the DAG, run a separate call that sees ONLY:

```
completed_steps (so far): [...]
new_step: {...}
```

and replies with ONLY this JSON:

```json
{
  "contradicts_previous": false,
  "contradiction_details": "",
  "skipped_dependency": false,
  "confidence": 0.9
}
```

## HARD RULES

- If `contradicts_previous = true` → return to the planner, do NOT keep building.
- If `skipped_dependency = true` → return to the planner, do NOT keep building.
- Verification happens CUMULATIVELY: every step, never only at the end.
- Contradictions to flag: conflicts in resource, credential, ordering, or
  service contract with any prior step.
- Skipped dependency: the new step logically needs a step that is absent.

## DETERMINISTIC SUB-CHECK (never overridable by the model)

Run in parallel and hard-fail regardless of the model verdict:

- orphan dependency: `new_step.deps` references a step not yet produced
- duplicate step id
- self-dependency
- missing transitive dependency closure

## WHY THIS WORKS

Each invocation is a narrow task ("is THIS step consistent with THOSE past
steps?") — a task even a small model does well — instead of the impossible
"hold the whole plan in working memory while also creating the next part".

## INTEGRATION

Insert as a hook after every DAG node in the planner
(`dual_process_planner.py`), alongside:
`ambiguity-resolver` (gates entry) and `confidence-calibrator` (decides whether
escalation is actually needed).