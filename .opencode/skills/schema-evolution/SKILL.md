---
name: schema-evolution
description: "Schema evolution skill (ordered migrations, additive-only audit, dual-read windows). Use when a workflow schema must grow without breaking live clients, when a migration chain has gaps, or when two shapes must serve at once. Trigger phrases: 'migrate schema', 'additive check', 'dual read', 'تطور السكيما'."
---

# Schema Evolution (Grow Without Breaking)

Code: `schema_evolve.py` (stdlib only). Ordered single-step
migrations (no jumps, downgrades refused); `audit_additive()` fails
dropped keys and narrowed types (widenings listed); `dual_read()`
serves both shapes with the loser kept under `_legacy`.

## Verification

- `tests/test_p2a_contract_schema.py` schema half green (additive
  pass/fail, chain walk, dual-read, missing-step error).
- Breaking edits require a new major + client migration plan, never a
  silent push.

## Pairs with

`contract-testing` (shape pins), `n8n-subworkflow-modularizer`
(version seams), `deploy-signoff-governance`, `build-gates-pipeline`.
