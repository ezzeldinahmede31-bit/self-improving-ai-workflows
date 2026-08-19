---
name: mathematics-for-computer-science
description: Applies the MIT 6.042 course (Lehman, Leighton, Meyer) to the mathematics that underpins computing: proof methods and well-ordering, induction, number theory and modular arithmetic, sums and recurrences, asymptotics, graph theory and trees, combinatorial analysis and probability, and random variables. Use when the user says 'prove by induction', 'number theory', 'modular arithmetic', 'recurrence', 'asymptotic growth', 'graph theory', 'combinatorics', 'probability', 'random variable', '6.042', 'Leighton', or when a proof or a probability argument is required for a computer science claim.
---

# Mathematics for Computer Science (Lehman, Leighton, Meyer)

The 6.042 notes are the definitive introduction to the math used in computer science. This skill supplies the proof and modeling discipline for algorithmic and probabilistic claims.

## Proof fundamentals

- Well-ordering and induction are the workhorses: every recursive algorithm and data structure gets its correctness argument from them.
- State the induction hypothesis and show the base case, the inductive step, and why the claim follows.
- For an algorithm claim, reason about the invariant maintained across iterations.

## Number theory

- gcd, Euclid's algorithm, and modular inverses underlie correctness of hashing and modular arithmetic everywhere.
- Modular arithmetic keeps numbers bounded; choose the modulus to fit the problem, not the mood.
- Fermat-style theorems give shortcuts for powers modulo a prime; verify the modulus conditions first.

## Graphs and combinatorial structures

- Model the problem as a graph when pairwise relationships are involved: trees for hierarchical, bipartite for matching, planar for drawing.
- Degree-sum, spanning tree, and coloring results give bounds on the structure's size.
- Enumeration answers must be derived, then checked against a small case to catch factor errors.

## Probability and random variables

- Formalize the sample space before computing; expectations of sums work regardless of dependence, variances do not.
- Use the binomial distribution and its approximations for repeated independent trials, stating assumptions.
- Confirm probabilistic claims with simulation when the derivation is fragile.

## Pairs with
concrete-mathematics, clrs-algorithm-mastery, algorithmic-math-reasoner, formal-math-logic-verification-engine, off-by-one-boundary-guard
