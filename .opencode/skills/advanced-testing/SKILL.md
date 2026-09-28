---
name: advanced-testing
description: "Advanced testing skill (property/metamorphic/differential/mutation/negative aides, seeded and shrinking). Use beyond example tests: random-input invariants, AI output relations, rival-implementation agreement, mutant kill rate, boundary batteries. Trigger phrases: 'property test', 'mutation score', 'metamorphic check', 'اختبار متقدم'."
---

# Advanced Testing (Beyond Examples)

Code: `advanced_testing.py` (stdlib only; Hypothesis-shaped callables
plug in later unchanged). `property_check()` runs seeded generators
against invariants (first failure kept); `metamorphic()` asserts
output relations over transformed inputs; `differential()` maps
agreement across rivals; `mutation_score()` reports kill rate with
survivors naming test gaps; `negative_cases()` is the boundary
battery.

## Verification

- `tests/test_p2b_advanced_spec.py` advanced third green (property
  hold/fail, relations, agreement, kill rate, battery).
- Survivors become new tests; batteries run on every input surface.

## Pairs with

`property-api-fuzzing-adapter` (schema-driven side), `golden-corpus`
(survivors feed cases), `xunit-test-patterns`, `build-gates-pipeline`.
