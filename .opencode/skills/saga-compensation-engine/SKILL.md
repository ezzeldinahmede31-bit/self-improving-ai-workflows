---
name: saga-compensation-engine
description: "Saga compensation skill (forward steps with reverse undo, honest compensation errors, JSONL journal). Use for multi-system transactions where a mid-chain failure must restore prior steps. Trigger phrases: 'saga transaction', 'compensate failure', 'undo chain', 'معاملة تعويضية'."
---

# Saga Compensation Engine (Undo on Failure)

Code: `saga.py` (stdlib only). Steps pair action + compensate;
forward runs until first failure, then compensations run in reverse
for completed steps. Missing/failing undos are reported (never
swallowed); every transition journals.

## Verification

- `tests/test_p1b_adversarial_saga.py` saga half green (happy path,
  reverse compensation, missing-undo report).
- Every production chain names its undo per step or records why none
  exists.

## Pairs with

`idempotency-store` (safe retries inside steps), `tool-result-verifier`
(confirm before next step), `immutable-audit-log` (journal mirror),
`build-gates-pipeline`.
