---
name: hutton-haskell
description: "Programs functionally with types as the design tool: pure functions, recursion, and monadic effects. Use when the user says 'Haskell', 'monad', 'functor', 'pure function', 'pattern matching', 'lazy evaluation', 'typeclass', 'Maybe', 'Either', 'Hutton', 'functional design', or when effects, errors, or state need taming by types."
---

# Hutton Programming in Haskell

Distilled from Graham Hutton's *Programming in Haskell*: types first, effects
as values, and equational reasoning — programs you can PROVE things about.

## Purpose

Model problems as data types + total functions, push effects to the edges,
and let the compiler reject whole bug classes before runtime.

## The method (in order)

1. **Types are the design.** Write the data types before the functions; make
   illegal states unrepresentable (sum types for alternatives, precise
   constructors, `newtype` for unit safety). If a bad state compiles, the
   types are unfinished.
2. **Total pure core.** Functions terminate on all inputs and touch no
   outside world — recursion with an explicit base case, pattern matching
   that the compiler confirms exhaustive. Test the core with pure inputs.
3. **Effects as values.** IO/ref-state/exceptions live in types (`IO`,
   `Maybe`/`Either`, `State`, `Reader`): sequence with `do`, combine with
   `<*>`/`<$>`, fail with typed errors — never exceptions-as-control-flow.
4. **Abstraction ladder:** Functor (map over a context) -> Applicative
   (combine contexts) -> Monad (sequence dependent effects). Reach for the
   WEAKEST that works; monads are for dependency, not habit.
5. **Laziness deliberately.** Infinite structures and on-demand computation
   via non-strict evaluation; but strictness annotations (`!`, `seq`) where
   space leaks hide (folds over big data: `foldl'`).
6. **Prove by equation.** Substitute definitions and simplify — the
   substitution model IS the debugger. Property tests (QuickCheck) encode the
   equations as machine-checked specs.

## Error-handling discipline

- Expected absence/failure: `Maybe`/`Either` with informative `Left` values.
- Invariants: `smart constructors` returning `Maybe`; illegal input never
  builds the type.
- `undefined`/`error` only for impossible-by-construction cases, each with a
  comment proving impossibility.

## Verification

New code ships with: the type signatures (read as documentation), totality
argument (why recursion terminates), effect inventory (which monads and why),
and one property test per law claimed (functor/monad/round-trip).

## Pairs with

- `functional-programming-scala` (FP on the JVM),
  `domain-modeling-functional` (types-as-requirements),
  `sicp-abstraction-and-interpretation` (abstraction layers),
  `tdd-sandbox-proof-engine` (property tests as proof).
