---
name: more-programming-pearls
description: Applies Jon Bentley's More Programming Pearls to writing, verifying, and improving programs: an end-to-end case study of a real program, writing correct programs under time pressure, profiling and empirical tuning, binary search variants, and the discipline of test case selection. Use when the user says 'more programming pearls', 'Bentley case study', 'write a program under pressure', 'profiling', 'binary search variant', 'test case selection', 'code tuning', 'second column', or when a program must be written and improved empirically rather than by speculation.
---

# More Programming Pearls (Jon Bentley)

The second collection of columns sharpens the first: how to write correct programs quickly, measure them honestly, and improve them by experiment.

## Writing programs under pressure

- Under time pressure, keep the program as simple as the problem allows and rely on the design recipe, not inspiration.
- Write the tests that define success before the implementation; they keep the effort honest.
- Leave time to re-read the code once; fresh eyes catch the mistakes of the first draft.

## Empirical performance work

- Profile first: find the function that actually dominates, then improve it.
- Tune one variable at a time and measure the effect of each change.
- Keep the profiling harness so regressions are caught later.

## Test case selection

- Choose tests that cover boundary conditions, degenerate inputs, and the paths most likely to hide a bug.
- Random tests find surprises; targeted tests explain them.
- A test that never fails tells you little; vary the input domain aggressively.

## Correctness tools

- Use binary search and its variants precisely: state what the loop invariant guarantees on exit.
- Mechanical verification (assertions, invariants, model checks) supplements but never replaces thought.

## Pairs with
programming-pearls, code-execution-guided-swemaster, systematic-debugging, systems-performance-profiling, unit-test-boundary-conditions
