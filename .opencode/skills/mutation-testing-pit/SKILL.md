---
name: mutation-testing-pit
description: "Mutation testing with PIT distilled. Use when measuring test suite strength, mutation coverage, surviving mutants, kill ratio, test gaps."
---

# Mutation Testing (PIT)

## Purpose

Measure what coverage hides: inject small faults (mutants) into production code and check the suite kills them, per the PIT mutation testing system.

## When to use

Use when the user says 'mutation testing', 'PIT', 'surviving mutant', 'kill ratio', 'mutation coverage', 'weak tests'.

## Steps

1. Run the green suite first as a baseline.
2. Generate mutants: condition negation, return-value swap, arithmetic swap, void-call removal.
3. Run the suite per mutant; killed means a test failed, survived means a gap.
4. Triage survivors: missing assertion versus untestable equivalent mutant.
5. Gate releases on mutation score trend, not an absolute single number.

## Anti-patterns

- Chasing a perfect score by killing equivalent mutants with brittle tests.
- Running mutation on the whole monolith nightly instead of diff-scoped.
- Confusing line coverage with fault-detection strength.
- Deleting surviving-mutant tests as noise.

## Example

Python (mutmut style idea):

```python
# mutant: return total + fee  ->  return total - fee
def test_total_adds_fee():
    assert invoice_total([10, 20], fee=5) == 35  # kills the swap mutant
```

JS: Stryker mutator runs the same kill-or-survive loop on vitest suites.

## Verification

Mutation report shows kill ratio with survivors triaged as test-added or equivalent; diff-scoped runs in CI.

## Pairs-with

code-coverage-mastery, mutation-score-gates, khorikov-unit-testing, xunit-test-patterns.
