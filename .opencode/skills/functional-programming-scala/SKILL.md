---
name: functional-programming-scala
description: Applies Chiusano & Bjarnason's Functional Programming in Scala to design pure, testable programs: referential transparency, total functions, data modeling with algebraic data types, error handling with Option and Either, strict and lazy evaluation with Streams, and the functional design of parallelism, parsers, and state handling through type-driven composition. Use when the user says 'functional programming', 'referential transparency', 'pure function', 'Option Either', 'algebraic data type', 'functional design', 'monad', 'lazy evaluation', 'property-based testing', 'Scala FP', 'Chiusano', or when a program should be composed from pure functions and made easy to test.
---

# Functional Programming in Scala (Chiusano & Bjarnason)

This book teaches functional programming by building real libraries from scratch — the discipline transfers to any language. This skill applies type-driven functional design.

## Purity and referential transparency

- A pure function depends only on its inputs; replacing a call with its value changes nothing. Design for that property.
- Push side effects to the edges of the program and keep the core pure and testable.
- Use total functions: handle every input, returning Option or Either when no value exists.

## Algebraic data types

- Model each domain with a small set of constructors; illegal states become unrepresentable.
- Write functions over the type by pattern matching on constructors; the compiler checks exhaustiveness.
- Keep the types as the source of truth for what is possible.

## Composition and laziness

- Compose small functions with map, flatMap, and custom combinators instead of writing loops.
- Lazy evaluation (Streams) lets you express infinite and on-demand computation while bounding work.
- Design the combinator set before the consumer; a small, orthogonal set beats many ad-hoc helpers.

## Testing functional code

- Property-based testing states invariants over a generator of inputs and finds counterexamples automatically.
- Each pure function is independently testable without fixtures or mocks.
- Test the error paths of Option and Either explicitly: the failure case is part of the contract.

## Pairs with
domain-modeling-functional, types-and-programming-languages, sicp-abstraction-and-interpretation, ctm-concepts-techniques-models, test-driven-development
