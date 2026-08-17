---
name: goos-outside-in-tdd
description: "Applies Freeman & Pryce's Growing Object-Oriented Software, Guided by Tests (GOOS): build systems outside-in with a walking skeleton, write a failing integration test for the visible behavior first, drive object design from the tests, and use test doubles (stubs, fakes, mocks) with clear intent at the boundaries. Use when the user says 'outside-in TDD', 'walking skeleton', 'write the test first from the outside', 'mockist or classicist', 'test doubles', 'grow the system from tests', 'integration test first', 'design objects from tests', or when starting a new system or feature and the tests should shape the structure. Pairs with: test-driven-development, tdd-sandbox-proof-engine, xunit-test-patterns, code-execution-guided-swemaster."
---

# GOOS — Growing OO Software Guided by Tests

Freeman & Pryce's insight: tests are not just verification — they are the *driver of
design*. You grow the system from the outside in, letting each failing test expose
the next piece of structure you need, so the code stays minimal and every dependency
is visible.

## When to use

- Starting a new system or feature where the shape is uncertain.
- When a feature's outer behavior is clear but the internal object design is not.
- When a codebase has tests bolted on after implementation and you want them to
  guide structure instead.

## The method

### 1. Start with the walking skeleton
- Build the thinnest possible end-to-end slice: a test that exercises the real outer
  boundary (HTTP request → real service → real persistence) and make it pass.
- The skeleton proves the wiring, then you grow features inside it. This is where
  the n8n world overlaps: a live end-to-end run is the walking skeleton for a
  workflow (see `n8n-e2e-test-runner`).

### 2. Outside-in: one failing test at a time
- Write a failing test that expresses the next visible behavior from the user's
  perspective.
- Run it, see it fail for the right reason (behavior missing), then make it pass
  with the simplest production code.
- Let the test's needs drive what collaborators exist — when a test needs a fake
  boundary, that boundary is a seam you are declaring.

### 3. Test doubles at the boundaries, with intent
- Use doubles only where a real dependency is slow, external, or non-deterministic
  (network, clock, persistence).
- Stubs return canned answers; fakes are lightweight working implementations; mocks
  assert the interaction. Choose by what you are testing: state (stub/fake) vs
  behavior/interaction (mock).
- Never mock what you own and is cheap to run for real — prefer the real thing.

### 4. Let the tests shape the object design
- A hard-to-test design is a design smell: extract the seam, name the dependency,
  and let the object graph stay small and explicit.
- Grow the object model one behavior at a time; do not pre-build layers the tests
  have not asked for.

## Verification
- The walking skeleton test runs green end to end.
- Each feature has a failing-first test that passes after the minimal production
  change (the RED→GREEN evidence, see `tdd-sandbox-proof-engine`).
- Doubles appear only at external boundaries; the suite runs fast and deterministically.

## Pairs with
- `test-driven-development` — the RED-GREEN-REFACTOR core.
- `tdd-sandbox-proof-engine` — evidence that tests pass in a clean sandbox.
- `xunit-test-patterns` — naming and organizing the test code itself.
- `code-execution-guided-swemaster` — execution evidence for the changes.