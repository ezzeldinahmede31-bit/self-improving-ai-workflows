---
name: acceptance-test-driven
description: "Acceptance test-driven development distilled. Use when driving development from acceptance tests, ATDD cycle, executable acceptance, demo proof."
---

# Acceptance Test-Driven Development

## Purpose

Drive delivery from acceptance: executable acceptance tests written first, development makes them pass, demos replay them live.

## When to use

Use when the user says 'ATDD', 'acceptance TDD', 'executable acceptance', 'acceptance first', 'demo acceptance'.

## Steps

1. Write acceptance tests from agreed examples before implementation.
2. Watch them fail for the right reason on current code.
3. Implement thinly to green; refactor with the net holding.
4. Keep acceptance green as the merge bar for the story.
5. Replay the same tests live at demo as proof.

## Anti-patterns

- Acceptance written after code and labeled ATDD.
- Acceptance asserting implementation instead of outcomes.
- Flaky acceptance tolerated at the merge bar.
- Demo showing slides instead of running tests.

## Example

```gherkin
Scenario: Refund issued
  Given a paid order
  When support refunds it
  Then the customer balance rises by the order total
```

## Verification

Acceptance predates code, merge barred on green, demo replays passing tests.

## Pairs-with

bdd-cucumber-deep, example-mapping-workshops, use-case-testing-patterns, scrum-qa-integration.
