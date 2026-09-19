---
name: khorikov-unit-testing
description: "Writes unit tests worth keeping: the four pillars and London vs Detroit. Use when the user says 'unit testing principles', 'valuable tests', 'London vs Detroit', 'mockist vs classicist', 'Khorikov', 'test-induced damage', or when mocks couple tests to implementation."
---

# Khorikov Unit Testing

Distilled from Vladimir Khorikov *Unit Testing Principles, Practices, and
Patterns*: a valuable test scores on four pillars — and most suites fail
pillar two (resistance to refactoring), which is why developers hate their
own tests.

## Purpose

Write tests that protect against regressions AND survive refactoring: high
value, low maintenance, honest about what they verify.

## The four pillars (grade every test on all four)

1. **Protection against regressions.** How much production code executes,
   how likely it breaks, how critical the feature. Trivial code needs few
   tests; critical algorithms need many. Coverage follows risk, not vanity.
2. **Resistance to refactoring (the neglected pillar).** Tests must fail on
   broken behavior and PASS on refactored-correct code. Coupling to
   implementation details (private methods, call sequences, mock interactions)
   fails refactors that users would never notice — the #1 suite killer.
   Couple to OBSERVABLE behavior only.
3. **Fast feedback.** Seconds, not minutes, for the unit suite (parallelize,
   no I/O in unit tests — anything touching disk/network/clock is
   integration by definition). Slow suites get skipped; skipped suites rot.
4. **Maintainability.** Small, intention-revealing, DRY in helpers but DAMP
   (descriptive, explicit) in test bodies. A test whose failure needs
   archaeology to understand is a liability.

## Schools: London vs Detroit (choose per seam)

- **Detroit/classicist (default):** real collaborators except shared
  dependencies (DB/filesystem/external services — replaced with fakes);
  verify end STATE. Fewer mocks, resilient tests.
- **London/mockist:** mock ALL out-of-class collaborators, verify
  INTERACTIONS. Justified only where the interaction is the contract
  (protocols, notifications) — elsewhere it welds tests to implementation.
- Rule: mock across architectural boundaries (anti-corruption), never
  across classes you own together.

## Verification

Per test: behavior-coupled (would survive a pure refactor? argue yes),
pillar scores stated for critical tests, suite time budget met. Tests that
lock implementation detail get rewritten, not grandfathered.

## Pairs with

- `aniche-effective-testing` (testability + doubles),
  `xunit-test-patterns` (fixture/double mechanics),
  `goos-outside-in-tdd` (mockist done right),
  `tdd-sandbox-proof-engine` (execution discipline).
