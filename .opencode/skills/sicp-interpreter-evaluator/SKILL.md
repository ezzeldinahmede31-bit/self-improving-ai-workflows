---
name: sicp-interpreter-evaluator
description: Applies the SICP (Structure and Interpretation of Computer Programs) evaluator chapter to building your own languages and tools: construct a metacircular evaluator — the environment model of computation, evaluation rules for expressions and procedures, applicative vs normal order, and the lazy/stream evaluator — so you can build domain-specific interpreters with confidence. Use when the user says 'build an interpreter', 'metacircular evaluator', 'environment model', 'evaluator', 'lazy evaluation', 'normal order', 'streams', 'domain-specific language', 'design my own language', 'evaluate expressions', 'closures and environments', or when the tooling for a domain would be far simpler as a small interpreter than as a stack of parsing code. Pairs with: sicp-abstraction-and-interpretation, domain-modeling-functional, clrs-algorithm-mastery, zero-trust-modular-decomposer.
---

# SICP Interpreter and Evaluator

Transfers the evaluator chapters of SICP (Structure and Interpretation of Computer Programs) to building your own languages: the environment model, the evaluation rules, and the lazy evaluator, so a domain-specific interpreter is designed with the same rigor as production software.

## When to use
- Building a DSL or a scripting surface for a domain.
- Understanding how evaluation really works (applicative vs normal order, closures, environments).
- Implementing streams, lazy lists, or delay/force semantics.

## The environment model
- A procedure is a closure: code plus the environment in which it was defined.
- Name binding is environment lookup; a new frame extends an existing environment.
- Recursion and higher-order functions fall out of this model without special cases.

## The evaluation rules
- A name is looked up in the environment chain.
- A literal evaluates to itself.
- A procedure application evaluates the operator and operands (applicative order) then applies the closure.
- Special forms (if, define, lambda) have their own rules and are not applied like ordinary procedures.

## Applicative vs normal order
- Applicative order (most languages): evaluate arguments before the call.
- Normal order: delay argument evaluation until needed; this is the seed of lazy evaluation.
- Streams implement normal-order-style behavior with explicit delay/force.

## Building the evaluator
1. Represent expressions as data (lists/s-expressions or a syntax tree).
2. Implement eval over the expression forms and apply over closures.
3. Extend with environment mutation and definitions.
4. Add laziness by wrapping thunks and forcing on demand.
5. Test the evaluator on its own interpreter (a metacircular test) and on the target DSL.

## Verification discipline
- Run a reference program through both the interpreter and a hand-derived trace; outputs must match.
- Verify recursion depth, closures, and mutation semantics with targeted cases.

## Pairs with
sicp-abstraction-and-interpretation, domain-modeling-functional, clrs-algorithm-mastery, zero-trust-modular-decomposer.