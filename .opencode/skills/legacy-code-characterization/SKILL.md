---
name: legacy-code-characterization
description: "Applies Michael Feathers' Working Effectively with Legacy Code to tame unreadable, untested code: the SEAM (a place where you can alter behavior without editing it), characterization tests that lock in current behavior before refactoring, the Golden Master technique, and the sprout method / wrap method for adding new behavior without breaking old behavior. Safe-refactoring rules so you never refactor blind. Use when the user says 'legacy code', 'untested code', 'seam', 'characterization test', 'golden master', 'sprout method', 'wrap method', 'dependency breaking', 'Feathers', 'refactor old code', 'how do I test this monster', or when touching code with no test safety net. Pairs with: code-smell-detector, tdd-sandbox-proof-engine, xunit-test-patterns, code-execution-guided-swemaster."
---
# Legacy Code Characterization (Working Effectively with Legacy Code - Feathers)

Feathers' definition: legacy code is code WITHOUT TESTS. The entire method: make the code testable via SEAMS, then lock behavior in with characterization tests, then refactor with a safety net. Never refactor blind.

## Core Concepts

### The SEAM
A place where you can alter behavior in your tests WITHOUT editing the source. Options: function parameters, dependency injection, subclass-and-override, preprocessor hooks, interface extraction.
- Rule: find a seam before you try to test. No seam, no test, no safe refactor.

### Characterization Tests
Tests that DESCRIBE current behavior, not intended behavior. You do not know what is correct - you record what the code does today, then refactor to keep that behavior.
- Golden Master: feed a real input, capture the output, assert output never changes as you refactor.

### Sprout Method (add new behavior safely)
- Write new code in a NEW method; the old method calls it. The old code is untouched; the new code is immediately testable.
- Sprout Class: if the new behavior needs its own state, a new class.

### Wrap Method (modify behavior safely)
- Keep the old method, rename its body to `originalMethod_`, write a new method that runs the old logic plus the change. Old callers still work; new behavior is isolated.

## Safe Refactoring Rules

1. Never refactor a method that has no characterization test covering its inputs.
2. Change one small behavior at a time; run the tests after each step.
3. If you cannot find a seam, extract the behavior into a testable unit FIRST (still behavior-preserving), then characterize, then refactor.
4. Use mechanical refactorings (rename, extract) before semantic ones (algorithm changes).
5. Golden Master before structural change; structural change before behavior change.

## Anti-patterns (severity)

- **A1 - Refactor blind** (HIGH): Changing logic with no tests. Fix: characterize first, always.
- **A2 - Big-bang rewrite** (HIGH): Rewriting the legacy system all at once. Fix: characterize, sprout, then refactor incrementally (strangler).
- **A3 - No seam found, no seam made** (HIGH): 'It can't be tested'. Fix: extract a seam; it is always possible.
- **A4 - Characterization over-reach** (MEDIUM): Tests that capture incidental output (timestamps, hashes) and break on any change. Fix: normalize the golden master inputs/outputs.
- **A5 - Sprouting into the same method** (MEDIUM): Adding new logic inline because it is shorter. Fix: sprout a method - testability first.

## Checklist

- [ ] A seam exists before testing
- [ ] Characterization/Golden Master tests lock in current behavior
- [ ] New behavior sprouts into a new method/class
- [ ] Each refactor step keeps the characterization tests green
- [ ] Behavior change only after structural change is proven green

## Verification

Run the characterization suite before AND after each refactor; both must pass with identical outputs. Run the build gates on the refactored artifact and require READY_FOR_DEPLOYMENT.
