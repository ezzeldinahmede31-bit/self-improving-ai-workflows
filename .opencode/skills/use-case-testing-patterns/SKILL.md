---
name: use-case-testing-patterns
description: "Use case testing distilled. Use when testing end-to-end user goals, main and alternate flows, preconditions, postconditions."
---

# Use Case Testing Patterns

## Purpose

Test whole user goals through main flows plus alternate and exception flows, with explicit preconditions and postconditions.

## When to use

Use when the user says 'use case testing', 'user flow', 'main flow', 'alternate flow', 'end-to-end scenario'.

## Steps

1. Write the goal, actor, preconditions, and success postcondition.
2. Script the main flow step by step with observable outcomes.
3. Add alternate flows (options the user may take) and exception flows (errors).
4. Automate the stable main flows; keep volatile alternates exploratory.
5. Verify postconditions in state, not just screen text.

## Anti-patterns

- Only the sunny-day path automated.
- Postconditions asserted via UI labels instead of real state.
- Preconditions built by clicking through setup instead of fixtures.
- Use cases that duplicate unit coverage with no added flow risk.

## Example

```gherkin
Scenario: Transfer funds
  Given accounts A (100) and B (0)
  When A transfers 40 to B
  Then A holds 60 and B holds 40
```

## Verification

Main plus alternate and exception flows listed, postconditions checked in state, fixtures build preconditions.

## Pairs-with

adzic-specification-by-example, end-to-end-workflow-testing, state-transition-testing, decision-table-testing.
