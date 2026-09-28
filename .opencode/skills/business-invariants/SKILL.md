---
name: business-invariants
description: "Business invariant skill (domain predicates per delivery, fail-closed crashes, equals/one-of factories). Use when a delivery must prove domain rules (right doctor, current price, ops zone), when 'technically green but wrong' is the risk, or when a predicate crashes mid-check. Trigger phrases: 'business rules check', 'invariant gate', 'right-doctor wrong-doctor', 'قواعد العمل'."
---

# Business Invariants (Is It RIGHT, Not Just Green)

Code: `business_invariants.py` (stdlib only). Security asks "safe?",
QA asks "runs?", this asks "correct?". Register predicates per domain
(`equals` / `one_of` factories + dotted-path helper); `evaluate()`
runs them all — a crashing predicate reports failed (fail-closed),
never skipped. One failed invariant blocks its delivery.

## When to use

- Every production delivery carrying domain meaning (booking, price,
  scheduling, access): declare the invariants, evaluate the payload.
- Triage: "all tests green but the outcome is wrong" → missing
  invariant, add it as a regression predicate.

## Verification

- `tests/test_p0c_invariants.py` green (all-pass, wrong-doctor block,
  crash-closed, empty domain, dotted helper).
- No delivery evidence table closes with open invariant failures.

## Pairs with

`traceability-links` (acceptance source), `n8n-delivery-verification-gate`
(evidence table), `promptfoo-eval-redteam-adapter` (behavioral side),
`build-gates-pipeline`.
