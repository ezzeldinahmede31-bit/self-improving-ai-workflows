---
name: myers-art-of-testing
description: "Designs black-box test cases that find bugs: partitioning, boundaries, and cause-effect. Use when the user says 'test case design', 'equivalence partitioning', 'boundary value', 'cause-effect graph', 'Myers', 'Art of Software Testing', or when tests exist but bugs escape."
---

# Myers Art of Software Testing

Distilled from Glenford Myers *The Art of Software Testing* (1979, still the
foundation): testing is DESTRUCTIVE — the psychology is to find errors, not
to show correctness. Test cases are designed, never improvised.

## Purpose

Design minimal test sets with maximal bug-finding power: partition the input
space, attack the boundaries, and model cause-effect logic explicitly.

## The design methods (apply in this order)

1. **Test with destructive intent.** A successful test FINDS an error; an
   unsuccessful one proves nothing. Assign testing to someone other than the
   author where possible (author blindness is measurable, not insulting).
   Never test your own certainty — test your doubt.
2. **Equivalence partitioning.** Divide each input domain into classes that
   should behave identically (valid + invalid classes each). One
   representative per class — then distrust the partition (the bug lives in
   the class you drew wrong).
3. **Boundary value analysis.** Errors cluster at edges: test ON, just
   INSIDE, and just OUTSIDE every boundary (min-1/min/min+1,
   max-1/max/max+1), for inputs AND outputs. If partitioning finds classes,
   boundaries find the bugs — always do both.
4. **Cause-effect graphing.** For complex logic combinations: map causes
   (inputs) to effects (outputs) as a Boolean graph with constraints
   (XOR-type, OR-type, one-and-only-one, requires, masks), convert to a
   decision table, derive cases covering each effect. Combinatorial logic
   tested by feel misses branches; graphed logic misses none.
5. **Error guessing (disciplined).** Experience-driven hunches (empty/null/
   zero/off-by-one/overflow) listed explicitly per feature, then executed —
   intuition inventoried beats intuition improvised.

## Debugging corollary (Myers on fixing)

- Locate by induction (specifics → general cause) or deduction (enumerate
  hypotheses, eliminate). Fix the CAUSE (error class), not the instance —
  then regression-test the class, not just the case.

## Verification

Test-design review: partition map per input, boundary triples per edge,
cause-effect graph for branching logic, error-guess list executed. A test
suite without boundary cases is decoration.

## Pairs with

- `unit-test-boundary-conditions` (boundary mechanics),
  `ammann-offutt-criteria` (coverage rigor),
  `zeller-why-programs-fail` (debugging science),
  `test-smells-catalog` (suite health).
