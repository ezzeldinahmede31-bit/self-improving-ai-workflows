---
name: xunit-test-patterns
description: "Applies Gerard Meszaros' XUnit Test Patterns to write clean, maintainable test suites: the Four-Phase test structure, the Test Double taxonomy (dummy, stub, fake, spy, mock), a catalog of test smells and their fixes, and fixture/setup patterns that stop tests from becoming a burden. Use when the user says 'my tests are a mess', 'refactor the tests', 'test smells', 'four phase test', 'test doubles', 'dummy stub fake mock spy', 'shared fixture', 'assertion pattern', 'how to organize tests', 'test maintainability', 'fix flaky tests', or when a test suite is slow, duplicated, fragile, or hard to change. Pairs with: tdd-sandbox-proof-engine, unit-test-boundary-conditions, goos-outside-in-tdd, code-execution-guided-swemaster."
---

# XUnit Test Patterns

Meszaros is the reference for *the tests themselves* as code worth engineering:
structure, naming, and the catalog of test smells (with their fixes). A clean test
suite is a design asset; a messy one becomes the team's slowest dependency.

## When to use

- Writing, organizing, or refactoring any automated test suite.
- When tests are slow, duplicated, order-dependent, or fail for unclear reasons.
- When a change to the codebase breaks many tests at once (a smell that the tests
  are over-coupled to the implementation).

## The patterns

### 1. The Four-Phase test structure
Every test is four phases in order: **Setup** (arrange), **Exercise** (act),
**Verify** (assert), **Teardown** (cleanup). If a test cannot be read in those four
phases, restructure it.

### 2. The Test Double taxonomy (pick deliberately)
- **Dummy**: passed but never used (satisfies a parameter).
- **Stub**: returns canned responses (state you control).
- **Fake**: lightweight working implementation of a real dependency.
- **Spy**: records the calls it received, for later assertion.
- **Mock**: asserts the expected interaction up front.
Rule of thumb: prefer the real thing when it is fast and deterministic; use the
simplest double that makes the test focused (see `goos-outside-in-tdd`).

### 3. Fix the test smells (the catalog, top offenders)
- *Obscure test*: unclear purpose → name by behavior ("sends_order_confirmation")
  not by mechanic.
- *Duplicate assertion / hard-coded test data*: extract builders and shared fixtures.
- *Shared fixture* (same objects across tests): coupling → prefer fresh setup per
  test unless the shared fixture is genuinely immutable.
- *General/conditional/exception-ignoring assertions*: assert the specific outcome;
  one meaningful assertion per test beats a wall of weak ones.
- *Test code duplication*: extract helpers (the same rule as production code).
- *Fragile tests* (break when unrelated code changes): assert behavior, not
  implementation details (no asserting on internal call counts unless the
  interaction is the contract).

### 4. Naming and organization
- Name tests as sentences of behavior: `methodName_condition_expectedResult`.
- Group by behavior area, keep setup helpers local, and make a failing test report
  *what behavior is missing* from its name alone.

## Verification
- Each test reads as four phases and its name states the behavior.
- The suite runs deterministically and fast enough to run constantly.
- Changing a behavior changes a small, predictable set of tests (the coupling
  smell is gone).

## Pairs with
- `tdd-sandbox-proof-engine` — sandboxed evidence for every code change.
- `unit-test-boundary-conditions` — edge/limit cases inside the tests.
- `goos-outside-in-tdd` — growing design from tests.
- `code-execution-guided-swemaster` — measured fix verification.