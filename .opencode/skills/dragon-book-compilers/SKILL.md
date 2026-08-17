---
name: dragon-book-compilers
description: "Applies the Dragon Book (Compilers: Principles, Techniques, and Tools) to build and reason about compilers, interpreters, and language tools: the front-end pipeline (lexing, parsing, semantic analysis), intermediate representations, code generation and optimization (data-flow analysis, loops, SSA), symbol tables and type checking, and the engineering discipline of context-free grammars, LL/LR parsing, and error recovery. Use when the user says 'build a compiler', 'write a parser', 'grammar for my language', 'LR parsing', 'LL(1)', 'lexer', 'tokenizer', 'AST', 'intermediate representation', 'code generation', 'optimize my compiler', 'symbol table', 'type checker', 'how do compilers work', 'DSL implementation', or when designing any language-processing tool. Pairs with: crafting-interpreters, sicp-abstraction-and-interpretation, algorithm-design-manual-war-stories, algorithmic-math-reasoner."
---

# Compilers: Principles, Techniques, and Tools

The Dragon Book's framework: a compiler is a pipeline — front end (understand the
source), middle (optimize), back end (emit target code). Every language tool
inherits these stages; knowing them lets you build correct, fast tools and debug
the ones you use.

## When to use

- Building a compiler, interpreter, parser, DSL, or code transformer.
- Understanding why a tool rejects or mis-parses your input.
- Designing a language or a syntax.

## The pipeline

1. **Lexing**: turn characters into tokens. A lexer is a deterministic finite
   automaton over a set of regular expressions — keep token definitions small and
   unambiguous; longest-match rules govern.
2. **Parsing**: turn tokens into a parse tree according to a grammar.
   - Top-down (LL): easy to write by hand, one-token lookahead common.
   - Bottom-up (LR / LALR): more powerful, prefers tool generation (yacc/bison).
   - Grammar design: eliminate left recursion for LL; factor common prefixes;
     a grammar that is ambiguous produces a broken parser — test with adversarial
     inputs.
3. **Semantic analysis**: symbol tables + type checking. Resolve identifiers,
   check types, catch uses that are syntactically valid but meaningless. This is
   where most real bugs are caught.
4. **Intermediate representation**: a stable middle form linking source and target.
   A well-designed IR (three-address code, SSA) is what enables optimization and
   retargeting to multiple back ends.
5. **Code generation + optimization**: data-flow analysis (def/use, reaching
   definitions), loop optimizations, register allocation, instruction selection.
   Optimize where profiling shows cost — the Dragon Book gives the machinery;
   the compiler writer still decides what matters.

## Engineering principles

- **Separate the front end from the back end.** The same IR lets one language
  compile to many targets and many languages share one optimizer.
- **Error handling is a feature.** Recovery strategies (panic mode, error
  productions, phrase-level) keep the compiler useful instead of dying on the
  first mistake. Users judge compilers by error messages.
- **Correctness before cleverness.** A parser that is 10% faster but rejects
  valid input is a bug. Build the boring correct version first, then optimize
  with measurements.
- **Grammars are contracts.** Document the grammar, keep it testable, and test
  both accepted and rejected programs.

## Verification checklist
- Every token: is its regex unambiguous and ordered correctly for longest-match?
- Every production: LL-usable or LR-usable; no ambiguity; tested on edge inputs.
- Symbol table: scoping rules explicit (lexical vs dynamic); shadowing correct.
- Types: checker exists before any code generation; type errors are caught early.
- IR: invariants defined (SSA, no unreachable defs) so optimization is safe.

Pairs with: crafting-interpreters (hands-on build path), sicp-abstraction-and-
interpretation (language design philosophy), algorithm-design-manual-war-stories
(algorithm selection for parsing/optimization).