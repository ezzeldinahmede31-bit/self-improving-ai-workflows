---
name: test-smells-catalog
description: Applies the test-smell catalog half of Gerard Meszaros' XUnit Test Patterns to find and fix the problems that make test suites slow, brittle, and unmaintainable: assertion-free tests, mystery guests, eager tests, fragile fixtures, slow tests, conditional test logic, and the refactorings that cure them. Use when the user says 'my tests are a mess', 'flaky test', 'test smells', 'why are my tests slow', 'fix the test suite', 'test maintainability', 'fragile test', 'obscure test', 'test pollution', 'smell catalog', or when a suite must be refactored safely. Pairs with: xunit-test-patterns, tdd-sandbox-proof-engine, unit-test-boundary-conditions, code-execution-guided-swemaster.
---

# Test Smells Catalog

Transfers Meszaros' catalog of test smells to any suite that is slowing the team down: name the smell, understand the root cause, and apply the refactoring that restores clarity and speed.

## When to use
- Tests fail intermittently or for unrelated reasons.
- A suite takes so long it stops being run.
- Tests pass but nobody can say what they verify.

## Smells that hide intent
- Assertion-free tests: the test exercises code but never asserts, so it can never fail for the right reason.
- Mystery guest: behavior depends on state created outside the test, so the failure point is invisible.
- Eager test: one test verifies several behaviors, so a single fault hides the rest.
- Obscure test: the intent of a test is hidden behind setup noise and clever names.

## Smells that break isolation
- Fragile fixtures: shared setup couples tests; a change in one test pollutes another.
- Test pollution: state leaks from one test into the next, causing order-dependent failures.
- Conditional test logic: branches inside the test make the pass/fail meaning unknowable.

## Smells that cost time
- Slow tests: unnecessary sleeps, real network calls, or full-system setup inside unit tests.
- Large tests: a test that exercises too much code forces a full debug cycle for any failure.
- Duplicated assertion logic: the same expectations written many times drift apart.

## Refactorings that cure the smells
- One assertion theme per test; split eager tests into focused tests.
- Build fixtures explicitly per test or via clear factory helpers; never mutate shared state.
- Replace real dependencies with test doubles at the boundary; keep the fast path in-memory.
- Extract helper assertions and naming that reads like a specification.

## Verification discipline
- Run the suite with randomized order and repeated runs; order-dependent or flaky tests fail loudly.
- Measure suite time per run; a shrinking suite is a healthy suite.

## Pairs with
xunit-test-patterns, tdd-sandbox-proof-engine, unit-test-boundary-conditions, code-execution-guided-swemaster.