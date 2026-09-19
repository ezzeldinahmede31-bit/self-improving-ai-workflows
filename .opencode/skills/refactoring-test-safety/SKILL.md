---
name: refactoring-test-safety
description: "Refactoring under test safety distilled. Use when restructuring code with tests as a net, characterization pinning, small reversible steps."
---

# Refactoring Test Safety

## Purpose

Restructure code without fear: pin behavior with tests first, then refactor in tiny reversible steps with the suite green throughout.

## When to use

Use when the user says 'refactor safely', 'restructure code', 'characterization test', 'golden master', 'safe cleanup'.

## Steps

1. Pin current behavior with characterization tests before touching structure.
2. Refactor in small steps; run the suite after each step.
3. Separate behavior change from restructuring into distinct commits.
4. Delete dead code only with suite approval plus review.
5. Stop when the goal shape is reached; avoid opportunistic rewrites nearby.

## Anti-patterns

- Refactor plus feature change in one commit.
- Big-bang rewrites justified as cleanup.
- Skipping pinning because the code looks simple.
- Leaving the suite red while continuing to restructure.

## Example

Python:

```python
def test_legacy_total_pinned():
    assert legacy_total(ORDER_FIXTURE) == 142.5  # pin before refactor
```

## Verification

Pinned tests predate restructuring, commits split behavior versus structure, suite green per step.

## Pairs-with

legacy-test-characterization, legacy-code-characterization, refactoring-improving-design, xunit-test-patterns.
