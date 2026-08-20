---
name: concrete-mathematics-recurrences
description: Applies the recurrence methods of Graham, Knuth and Patashnik's Concrete Mathematics to solve recurrences exactly: the repertoire method, guess-and-verify with induction, summation factors, and turning recurrences into closed forms via generating functions. Covers the standard recurrence families and the discipline of checking a claimed closed form against small cases before trusting it. Use when the user says 'solve this recurrence', 'repertoire method', 'closed form', 'summation factor', 'divide and conquer recurrence', 'master theorem', 'guess and verify', 'Concrete Mathematics', 'GKP', or when a recurrence must be solved exactly rather than approximated.
---

# Concrete Mathematics: Recurrences

Recurrences are how discrete structures reveal their size and shape. Graham, Knuth and Patashnik's Concrete Mathematics builds a toolbox for solving them exactly — and, just as important, for checking the answer. This skill encodes that toolbox so a recurrence is solved, not eyeballed.

## The Repertoire Method
- For linear recurrences, guess the closed form as a linear combination of known solution shapes and solve for the unknown coefficients.
- Plug simple base cases into the candidate form to pin down the coefficients one by one.
- The method turns "clever guessing" into a repeatable algebra routine.
- Apply it when the recurrence is linear with constant coefficients and small base cases.

## Summation Factors and First-Order Recurrences
- Rewrite a first-order recurrence so the recursive term telescopes, then solve by summing a simple expression.
- The summation factor is chosen so the recursion coefficient cancels, converting the recurrence into a pure sum.
- Recognize the pattern that many recurrences reduce to a sum, and that sums are easier to bound and to evaluate exactly.
- Use this route when the recurrence is first-order even if the coefficients vary with the index.

## Divide-and-Conquer Recurrences
- For recurrences of the form T(n) = a T(n/b) + f(n), identify the recursion tree shape and sum the work across levels.
- Compare the work per level against the branching factor to read off the dominant term — this is the essence of the master-theorem style analysis.
- Handle ceilings and floors with care; boundary effects can shift the answer by a constant, not just by a rounding term.
- Prefer the recursion-tree argument for intuition and a rigorous induction for the proof.

## Verification Discipline
- Always evaluate the proposed closed form on the first few small cases before trusting it.
- Cross-check the closed form against an independent method: iterate the recurrence mechanically for n up to a hand-computable size.
- If two methods disagree, treat the difference as a boundary or off-by-one clue, not a rounding artifact.
- State the range where the closed form is proven, since base-case conditions often differ from the general step.

## Pairs with
concrete-mathematics, algorithmic-math-reasoner, clrs-algorithm-mastery, formal-math-logic-verification-engine, mathematics-for-computer-science
