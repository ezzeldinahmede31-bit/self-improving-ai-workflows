---
name: types-and-programming-languages
description: Applies Benjamin C. Pierce's Types and Programming Languages to design and reason about type systems and language semantics: the untyped lambda calculus, the simply typed lambda calculus, safety (progress and preservation), references, subtyping, recursive types, and polymorphism with System F. Use when the user says 'type system', 'lambda calculus', 'simply typed', 'safety', 'progress and preservation', 'subtyping', 'recursive types', 'polymorphism', 'System F', 'Pierce', 'TAPL', 'design a typed language', or when a language or DSL needs a rigorous type discipline.
---

# Types and Programming Languages (Benjamin C. Pierce)

TAPL is the standard reference for type systems and their proofs. This skill applies its method: define the semantics, then prove safety by progress and preservation.

## Calculi as the core

- The lambda calculus is the minimal model of computation; translate every language feature into it to expose the essence.
- Evaluation rules define meaning precisely; write them before implementing.
- Distinguish values from expressions and stuck terms from errors.

## Safety and soundness

- Progress: a closed, well-typed term is either a value or steps forward. Preservation: stepping preserves typing.
- These two theorems give type safety: well-typed programs do not get stuck.
- Prove them by induction on the typing derivation and the evaluation rules.

## Typing features

- Subtyping adds a subtype relation with safe upward coercion; check the subsumption rule carefully.
- References bring store typing and the type of mutable state into the system.
- Recursive types let types refer to themselves, enabling lists and trees as types.

## Polymorphism and abstraction

- System F adds universal quantification, letting one term work for all types.
- Design the type system around the guarantee you want (safety, encapsulation, rejection of ill-formed programs), then prove it.
- When a feature breaks safety, weaken it deliberately and document the change.

## Pairs with
functional-programming-scala, domain-modeling-functional, formal-math-logic-verification-engine, sicp-abstraction-and-interpretation, dragon-book-compilers
