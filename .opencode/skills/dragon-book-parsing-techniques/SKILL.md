---
name: dragon-book-parsing-techniques
description: Applies the parsing chapters of the Dragon Book (Compilers: Principles, Techniques, and Tools) to build correct language front-ends: grammar formalization, top-down LL(1) and recursive-descent parsing, bottom-up LR/SLR/LALR parsing with conflict resolution, and practical error recovery. Use when the user says 'build a parser', 'grammar for my language', 'LL(1)', 'LR(1)', 'LALR', 'recursive descent', 'parse table', 'conflict in my grammar', 'tokenizer and parser', 'lookahead', 'grammar ambiguity', 'left recursion', 'error recovery in parsing', or when implementing any front-end that must accept a well-defined syntax. Pairs with: dragon-book-compilers, crafting-interpreters, sicp-interpreter-evaluator, algorithm-design-manual-war-stories.
---

# Dragon Book Parsing Techniques

Transfers the parsing toolkit of Aho, Lam, Sethi and Ullman to real language front-ends: formalize the syntax, pick the right parsing strategy for the grammar, and resolve conflicts with evidence instead of guesswork.

## When to use
- Building a lexer plus parser for a new language or DSL.
- Choosing the parsing strategy — recursive descent, LL(1), or a bottom-up LR-family approach.
- Debugging a grammar with shift/reduce or reduce/reduce conflicts.
- Adding sensible error reporting and recovery to a hand-written parser.

## Grammar formalization
- Write the grammar as a context-free grammar first; every parser decision follows from the production rules.
- Remove left recursion and left-factor productions so the grammar is LL(1) when top-down parsing is the goal.
- Keep the grammar unambiguous; ambiguous productions force arbitrary precedence hacks into the parse.

## Top-down parsing
- LL(1) tables require a predict set per production; the parse succeeds only when the lookahead token lands in the predict set.
- Recursive descent is the LL(1) idea expressed as functions: one function per nonterminal, choosing the production from the lookahead.
- Handle the classic failures — left recursion (infinite descent), common prefixes (left factoring), and optional/star constructs that hide decisions.

## Bottom-up parsing (LR family)
- LR parsers read tokens left to right and reduce only when the right-hand side is complete; the table holds states and actions.
- SLR uses follow sets; LR(1) tracks lookahead in each item; LALR merges states to shrink the table while keeping most LR(1) power.
- Shift/reduce conflicts usually mean a precedence or associativity choice is needed; reduce/reduce conflicts usually mean the grammar is ambiguous.
- Resolve a conflict by declaring precedence or by rewriting the grammar — never by tweaking the parser output.

## Error recovery
- Report the first error clearly: the offending token, the line, and the set of expected tokens.
- Panic-mode recovery: skip tokens until a synchronizing token appears, so one error does not cascade into many.
- Error productions and error markers keep the parse alive long enough to report a useful diagnostic.

## Verification discipline
- Keep a corpus of valid and invalid inputs; assert every valid input parses and every invalid input is rejected with a diagnostic.
- Add grammar-regression tests for each conflict you resolve.

## Pairs with
dragon-book-compilers, crafting-interpreters, sicp-interpreter-evaluator, algorithm-design-manual-war-stories.