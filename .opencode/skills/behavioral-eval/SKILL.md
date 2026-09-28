---
name: behavioral-eval
description: "Behavioral eval skill (intent/tool/grounding/fact scoring per scenario, weighted totals). Use when an agent change must prove correct behavior, when hallucinated availability is the risk, or when a booking flow needs a worked rubric. Trigger phrases: 'agent behavior score', 'intent check', 'booking rubric', 'سلوك الوكيل'."
---

# Behavioral Eval (Did It Behave Right?)

Code: `behavioral_eval.py` (stdlib only). Scenarios pair context with
weighted checks (`intent_is`, `tools_used` with forbid list,
`response_holds`, `facts_match`); `run()` scores one agent fn across
all or one scenario. Crashing checks fail closed.

## Verification

- `tests/test_p1a_regression_behavior.py` behavioral half green
  (perfect score + sloppy-agent failure naming intent/facts).
- Agent promotions cite scenario scores, not demos.

## Pairs with

`business-invariants` (domain truth), `agent-readiness-verifier-adapter`
(fixtures), `promotion-pipeline` (promotion gate), `build-gates-pipeline`.
