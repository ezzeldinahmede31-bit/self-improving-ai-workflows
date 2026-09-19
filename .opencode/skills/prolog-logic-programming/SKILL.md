---
name: prolog-logic-programming
description: "Programs in logic: facts, rules, queries, and search. Use when the user says 'Prolog', 'logic programming', 'unification', 'resolution', 'DCG', 'constraint programming', 'knowledge base', 'inference', 'Learn Prolog Now', or when a problem is relations and search rather than steps and state."
---

# Prolog Logic Programming

Distilled from Blackburn/Bos/Striegnitz *Learn Prolog Now!*: describe WHAT
holds; let resolution search find HOW. Programs are theories, queries are
theorems, answers are proofs.

## Purpose

Solve relation-heavy problems (parsing, reasoning, planning, program
analysis) by declaring knowledge and querying it — with full control of the
search when needed.

## The core (in learning order)

1. **Facts, rules, queries.** `parent(tom,bob).` is data; `sibling(X,Y) :-
   parent(Z,X), parent(Z,Y), X \= Y.` is knowledge; `?- sibling(tom,X).`
   asks. Variables unify; answers are bindings that make the query true.
2. **Unification + resolution.** Execution = SLD resolution: match the goal
   against clause heads, substitute, recurse depth-first left-to-right. Know
   the search order or be surprised by it — clause AND goal order both shape
   behavior and termination.
3. **Recursion is the loop.** Base case + step case over lists/trees
   (`[H|T]` patterns). Accumulators for tail recursion; difference lists for
   O(1) appends. Termination argument: a measure that shrinks each call.
4. **Control the search.** Cut (`!`) prunes choice points — green cuts (pure
   efficiency, same answers) vs red cuts (change semantics; comment them).
   Negation-as-failure (`\+`) means "not provable", not "false" — use only on
   ground goals.
5. **DCGs for language.** Definite Clause Grammars turn grammar rules into
   parsers directly (`sentence --> noun_phrase, verb_phrase`); arguments
   thread semantics alongside syntax. Parsing, generation, and analysis from
   one description.
6. **Constraints lift search.** CLP(FD) prunes domains before labeling
   (SEND+MORE=MONEY style): model with domain constraints, propagate, then
   label. Order variables by fail-first for speed.

## Debugging logic (different from imperative debugging)

- Trace the proof tree (`trace`), not values: which clause matched, where
  choice points remain, where infinite recursion loops (left recursion in
  DCGs is the classic).
- Instantiation errors mean a variable is still free where groundness was
  assumed — add the missing generator goal earlier.

## Verification

Each program ships with: sample queries + expected bindings, termination
argument, cut color justification, and a test where the goal must FAIL
(negative tests catch over-general rules).

## Pairs with

- `sicp-interpreter-evaluator` (evaluation models),
  `dragon-book-parsing-techniques` (grammar theory),
  `pgm-inference-variable-elimination` (probabilistic cousin),
  `tdd-sandbox-proof-engine` (query-as-test).
