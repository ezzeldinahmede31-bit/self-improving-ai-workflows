---
name: aniche-effective-testing
description: "Tests modern codebases effectively: testability design, doubles, and legacy strategy. Use when the user says 'testability', 'effective testing', 'test doubles', 'mock or stub', 'testing legacy', 'Aniche', or when tests are hard to write because the design resists them."
---

# Aniche Effective Software Testing

Distilled from Maurício Aniche *Effective Software Testing*: painful tests
signal design problems — improve testability and the tests (and the design)
get better together. Modern, pragmatic, automation-first.

## Purpose

Make any codebase testable and keep it tested: design openings for tests,
choose doubles correctly, and conquer legacy code systematically.

## The practice

1. **Design for testability.** Pain writing a test = design feedback, not a
   testing failure: untestable code has hidden dependencies, nondeterminism,
   or oversized units. Open seams (dependency injection, pure functions for
   logic, thin adapters at boundaries). If it hurts, redesign the seam —
   don't heroic-mock the world.
2. **Doubles, chosen right.** Dummy (placeholder), Fake (working shortcut:
   in-memory DB), Stub (canned answers), Mock (behavior verification), Spy
   (record + verify). Rules: prefer real collaborators for value objects;
   fake infrastructure at the boundary; mock sparingly (behavior coupling
   makes tests brittle — verify outcomes, not interactions, unless the
   interaction IS the contract).
3. **Structure that scales.** Test code is production code: AAA arrangement,
   one behavior per test, intention-revealing names (method_condition_
   expectation), shared fixtures minimized (mystery guests rot suites).
   Flaky tests quarantined same-day with owner + deadline — a flaky suite is
   an ignored suite.
4. **Legacy conquest (the loop).** Cover with characterization tests (lock
   behavior first) → extract seams (sprout/wrap smallest testable units) →
   refactor under cover → expand. Never "stop and rewrite the tests later" —
   later never ships.
5. **Coverage that means something.** Line coverage as smoke alarm (low =
   danger), mutation score as truth serum (surviving mutants = untested
   behavior), risk-weighted: critical paths demand high mutation kill rates,
   CRUD glue does not. Report the trio, never the single percentage.

## Verification

Suite review: testability pain log shrinking, double choices justified per
case, flaky list empty-or-owned, mutation score on critical paths stated.
Tests that only the author can run are personal notes, not a suite.

## Pairs with

- `xunit-test-patterns` (double taxonomy depth),
  `test-smells-catalog` (suite diseases),
  `legacy-code-characterization` (legacy loop),
  `khorikov-unit-testing` (unit-test philosophy).
