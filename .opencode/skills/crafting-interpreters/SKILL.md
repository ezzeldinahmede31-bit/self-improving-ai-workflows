---
name: crafting-interpreters
description: "Applies Robert Nystrom's Crafting Interpreters to build a complete, correct language interpreter end to end: two working interpreters (jlox in Java, clox in C) covering the scanner, Pratt parser, and recursive-descent parser, evaluation and tree-walking, environments and scoping, closures and functions, classes, garbage collection, and bytecode compilation + virtual machine execution. Use when the user says 'build my own programming language', 'write an interpreter', 'make a scripting language', 'Pratt parsing', 'recursive descent', 'bytecode VM', 'garbage collection', 'closures', 'scoping', 'how to design a language', 'DSL with real semantics', or when implementing any evaluator, parser, or virtual machine and wants a proven, incremental path with a testable design. Pairs with: dragon-book-compilers, sicp-abstraction-and-interpretation, tdd-sandbox-proof-engine, algorithm-design-manual-war-stories."
---

# Crafting Interpreters

Nystrom's book walks you through two real interpreters — a fast-to-write tree
walker and a bytecode virtual machine — with the explicit philosophy: the best
way to learn how languages work is to *build one*. Every piece is small, ordered,
and testable.

## When to use

- Building any interpreter, evaluator, or small language.
- Understanding how closures, scoping, and garbage collection really behave.
- Choosing a tree-walking interpreter vs a bytecode VM for a real tool.

## The tree-walking interpreter (start here)

1. **Scanner**: characters to tokens (strings, numbers, identifiers, punctuation,
   comments). Keep it a simple loop with clear error messages — it is the
   smallest stage and easy to get right.
2. **Parser**: recursive descent for expressions using **Pratt parsing** for
   operator precedence (a table of binding powers + prefix/infix handlers — the
   cleanest way to handle precedence and precedence levels).
3. **Representation**: a small class hierarchy for AST nodes (literal, unary,
   binary, variable, assignment, call, grouping).
4. **Evaluation**: a tree-walker that evaluates nodes, plus an **Environment**
   (scope chain) for variables. Environments make closures and lexical scoping
   precise: each function call gets a fresh environment, closures capture the
   environment that existed at their creation.
5. **Control flow, functions, classes**: implement by adding node types, not by
   patching. Statements return control to the evaluator (break/return via
   exceptions is a common clean mechanism).

## The bytecode VM (when performance matters)

- Compile the AST to a bytecode instruction stream (push, pop, get-local,
  set-local, jump, call) and run it on a stack-machine VM with a value stack.
- A real interpreter in C forces the hard truths: **garbage collection** (mark-and-
  sweep over the VM's roots) and careful memory ownership. These are exactly the
  lessons that make the difference for real language implementations.
- Constants pools, local variable slots, and jump tables make execution fast while
  staying simple to reason about.

## Engineering lessons

- **Build in tiny increments with a test at each step.** The book's structure is
  the discipline: every chapter leaves a working, runnable interpreter. Do the
  same — never carry a broken state forward.
- **Errors are part of the language.** Good error messages (with line numbers and
  context) are a feature users feel immediately.
- **Design for both readers and machines.** Choose the representation that is
  easiest to reason about for each stage — then optimize only when measured.
- **Semantics are the contract.** Before adding syntax, write down what it means
  (evaluation order, scoping, mutation). Ambiguity in the spec becomes bugs in
  the interpreter.

Pairs with: dragon-book-compilers (formal foundations), sicp-abstraction-and-
interpretation (design philosophy of evaluators), tdd-sandbox-proof-engine
(incremental test-driven build).