---
name: policy-engine
description: "Deterministic Policy-as-Code skill (allow/deny/approve verdicts, budget ceilings, prompt-proof denies). Use when an agent action needs a pre-execution verdict, when budgets must deny automatically, or when a prompt must never override a deny. Trigger phrases: 'policy check', 'is this action allowed', 'budget ceiling', 'سياسة التنفيذ'."
---

# Policy Engine (Deterministic Pre-Execution Verdicts)

Code: `policy_engine.py` (stdlib only). A policy is a plain dict: a
default verdict plus an ordered rule list (agent glob, action glob,
resource glob, effect allow/deny/approve). Evaluation order per
request: budget ceilings first, then first matching DENY, then first
matching APPROVE, then first matching ALLOW, else the default.

## When to use

- Before ANY agent side effect: `evaluate(agent, action, resource)`.
- Budget windows: `record_use(tokens, cost)` after metered calls;
  `remaining()` for headroom; `reset_spend()` per interval.
- APPROVE verdicts route to `hitl_gate.py`; DENY never reaches a human
  (fail-closed, no prompt can flip it — covered by test).

## Steps

1. Load the policy dict (checked at construction; bad rules raise).
2. Evaluate each proposed operation; obey the verdict literally.
3. Record spend after each metered call so ceilings stay honest.
4. Archive verdict + rule id with the delivery evidence.

## Verification

- `tests/test_p0a_policy.py` green (deny-wins, approve-routing,
  default-deny, budget trip, prompt-proof deny).
- No ALLOW path exists for an action a DENY rule names.

## Pairs with

`capability-tokens` (scoped grants inside allowed space),
`human-approval-gates` (APPROVE verdicts), `build-gates-pipeline`,
`agent-control-plane-adapter`.
