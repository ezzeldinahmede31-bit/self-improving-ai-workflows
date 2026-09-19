---
name: programming-languages-grossman
description: "Compares language paradigms the CSE341 way: ML types, Racket macros, Ruby objects. Use when the user says 'static vs dynamic typing', 'type inference', 'pattern matching', 'closures', 'lexical scope', 'macros', 'continuations', 'multiple dispatch', 'ML', 'Racket', 'Grossman', 'which paradigm', or when choosing how a language shapes the solution."
---

# Grossman Programming Languages

Distilled from UW CSE341 (Grossman): a language is its binding, scope,
typing, and evaluation rules. Learn three paradigms deeply; every other
language becomes a mix-and-match.

## Purpose

Predict what a language makes easy, hard, or impossible — from its core
rules, not its marketing.

## The three paradigms (each with its lesson)

1. **ML: types that prove.** Datatypes + exhaustive pattern matching make
   illegal cases unrepresentable. Type inference (Hindley-Milner) gives
   safety without annotations. First-class functions + no mutation by default
   = equational reasoning. Lesson: push checks into the type system and whole
   test suites become unnecessary.
2. **Racket: languages from languages.** Homoiconicity + macros = extend the
   language toward the problem (DSLs). Delayed evaluation (streams, promises,
   laziness) separates description from execution. Interpreters demystified:
   eval/apply over environments is a weekend project. Lesson: when the
   problem needs new syntax or control, grow the language.
3. **Ruby/OOP: messages and mixins.** Everything is an object receiving
   messages; blocks/closures customize control flow; modules/mixins share
   behavior without inheritance lattices. Dynamic typing trades compile-time
   proof for flexibility + tests. Lesson:late binding maximizes extension
   points — at the price of tool-visible contracts.

## Cross-cutting judgments

- **Scope:** lexical (closures capture definition environment) vs dynamic
  (capture call environment) — know which your language uses or closures lie.
- **Typing:** static catches misuse early, dynamic defers to tests; gradual
  typing splits the difference. Soundness (well-typed never goes wrong in
  stated ways) is the property that matters, not "strong vs weak" slogans.
- **Mutation:** shared mutable state kills local reasoning; isolate it
  (functional core, imperative shell) regardless of paradigm.
- **Evaluation:** eager vs lazy changes termination AND performance; streams
  need laziness, tight loops usually want eagerness.

## Verification

For any language decision: name the paradigm forces at play, the scope/typing
rules relied upon, and what becomes untestable-or-unprovable as a result.
"Just use X" without the forces analysis is rejected.

## Pairs with

- `hutton-haskell` (typed FP depth), `sicp-abstraction-and-interpretation`
  (language building), `types-and-programming-languages` (type theory),
  `dragon-book-parsing-techniques` (syntax front-ends).
