---
name: code-coverage-mastery
description: "Code coverage mastery distilled. Use when measuring line branch function coverage, honest reporting, coverage gates, uncovered risk review."
---

# Code Coverage Mastery

## Purpose

Use coverage honestly: measure line, branch, and function coverage; gate regressions; review uncovered code for risk, not vanity targets.

## When to use

Use when the user says 'code coverage', 'branch coverage', 'coverage gate', 'uncovered code', 'coverage report', 'istanbul', 'coverage.py'.

## Steps

1. Measure line plus branch plus function coverage per change.
2. Gate against drops, not absolute vanity thresholds.
3. Review uncovered lines: deliberate exclusion or missing test.
4. Exclude generated code explicitly with reason.
5. Pair coverage with mutation signals where risk is high.

## Anti-patterns

- Chasing a percentage with assertion-free tests.
- Coverage measured but never gated or reviewed.
- Generated code inflating denominators silently.
- Tests written to cover lines instead of behaviors.

## Example

```bash
pytest --cov=src --cov-branch --cov-fail-under=80
```

## Verification

Branch coverage tracked, drop-gate enforced, exclusions reasoned, high-risk areas mutation-checked.

## Pairs-with

mutation-testing-pit, mutation-score-gates, xunit-test-patterns, quality-metrics-dashboard.
