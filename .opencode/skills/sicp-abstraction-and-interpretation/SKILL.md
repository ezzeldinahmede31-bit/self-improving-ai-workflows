---
name: sicp-abstraction-and-interpretation
description: "Applies the SICP (Structure and Interpretation of Computer Programs) discipline to system design and code: build programs as layers of abstraction with named procedures, data abstractions with constructors/selectors, and (for hard problems) your own evaluator/domain language via meta-linguistic abstraction. Includes the SICP mental toolkit — substitution model reasoning, recursion as the core of control, higher-order functions, streams/lazy evaluation, and symbolic data. Use when the user says 'abstract this', 'build a domain-specific language', 'write an interpreter', 'higher-order functions', 'design for change', 'remove duplication by abstraction', 'evaluator', 'streams and lazy evaluation', 'bottom-up design', or when a codebase needs a simpler mental model. Pairs with: zero-trust-modular-decomposer, domain-modeling-functional, agent-arch-system-design, proactive-spec-expander."
---

# SICP — Abstraction and Interpretation

SICP teaches that programming is the craft of building layered abstractions, and
that the most powerful tool is writing programs that write programs (interpreters
and domain languages). The book's value is the *way of thinking*, not any syntax.

## When to use

- Designing a new module or subsystem where the module boundaries are unclear.
- A codebase whose components duplicate logic or lack a unifying mental model.
- When a problem needs its own notation or mini-language (parsers, rule engines,
  workflow DSLs).
- Before choosing recursion vs iteration, or eager vs lazy evaluation.

## The SICP method

### 1. Build by layers of abstraction
- Each layer exposes a small, named interface to the layer above.
- Data abstraction: define constructors and selectors; callers never touch the
  representation, so the representation can change without touching callers.
- Procedures as first-class values: pass behavior as an argument (higher-order
  functions) instead of scattering similar loops.

### 2. Reason with the substitution model first
- Before optimizing, trace execution by substituting arguments into the procedure
  body. This catches design errors cheaply.
- Name the recursion/iteration shape: linear recursive, tail-recursive (iterative),
  tree recursion. Prefer the shape whose stack and space behavior is deliberate.

### 3. Meta-linguistic abstraction (the SICP superpower)
When a domain has its own vocabulary and rules, write a small evaluator for that
domain rather than encoding every case with if/else:
- Define the data model (the "expressions") of the mini-language.
- Define the environment (variables/bindings) and the evaluation rules.
- Then the domain logic becomes data + one interpreter — orders of magnitude
  easier to extend.
- Apply to config systems, workflow DSLs, rule engines, form builders, prompt
  templates — any place a growing switch/case signals a hidden language.

### 4. Streams and lazy evaluation
- Decouple producers from consumers by representing infinite/expensive sequences as
  streams (elements computed on demand).
- Use when strict evaluation would compute work the consumer never touches (data
  pipelines, generated sequences, windowed processing).

### 5. Symbolic data
- For problems that manipulate symbols and structure (not numbers), represent the
  problem's own data types and work on the tree of the input, not a flattened copy.

## Verification
- After abstracting, run the original behavior tests unchanged — abstraction must be
  behavior-preserving (see `code-execution-guided-swemaster` verification).
- For an interpreter/DSL: write a test that exercises the mini-language end to end
  and prove it evaluates to the expected result.
- Check the abstraction boundary: can you swap the representation and keep callers
  intact?

## Pairs with
- `zero-trust-modular-decomposer` — file-level modular boundaries for the layers.
- `domain-modeling-functional` — types as the contract for domain models.
- `agent-arch-system-design` — system-level architecture from the abstraction layering.
- `proactive-spec-expander` — expanding a prompt into the layer plan before coding.