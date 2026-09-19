---
name: graham-istqb-foundations
description: "Dorothy Graham ISTQB foundations distilled. Use when planning test levels, test types, static vs dynamic testing, test design techniques, defect lifecycle, entry and exit criteria."
---

# ISTQB Foundations (Graham)

## Purpose

Apply the durable ISTQB core per Dorothy Graham: 7 testing principles, test levels/types, static testing, black/white/experience-based design, defect management, entry/exit criteria.

## When to use

Use when the user says 'ISTQB', 'test levels', 'test plan', 'entry criteria', 'exit criteria', 'defect lifecycle', 'static testing', 'test design technique'.

## Steps

1. State the 7 principles (exhaustive testing impossible, defect clustering, pesticide paradox, context dependence).
2. Map levels: component -> integration -> system -> acceptance, each with its test basis and objectives.
3. Pick design techniques: black-box (EP, BVA, decision tables, state transition), white-box (statement/branch), experience-based (error guessing, exploratory).
4. Add static testing: reviews and static analysis before execution.
5. Define entry/exit criteria and defect severity/priority workflow.

## Anti-patterns

- Treating ISTQB as a script instead of a context-dependent toolkit.
- No traceability from requirement to test to defect.
- Exit by date only with no quality criteria.
- Logging defects without steps, expected vs actual, severity vs priority split.

## Example

Python EP + BVA table for age 18-65:

```python
@pytest.mark.parametrize("age,valid", [(17, False), (18, True), (65, True), (66, False)])
def test_age_boundary(age, valid):
    assert is_eligible(age) is valid
```

## Verification

Coverage per technique listed, entry/exit checklist signed, defect report reproducible with expected/actual.

## Pairs-with

beizer-domain-testing, copeland-pairwise-testing, black-risk-based-testing, kaner-lessons-testing.
