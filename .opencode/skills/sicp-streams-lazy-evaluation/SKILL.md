---
name: sicp-streams-lazy-evaluation
description: "Applies the streams and lazy-evaluation chapter of SICP (Structure and Interpretation of Computer Programs) to process unbounded or on-demand data: streams as delayed lists built with delay and force, memoized promises so each element is computed only once, infinite streams (integers, Fibonacci, prime sieve), and the lazy-evaluator variant that makes the whole language evaluate on demand. Use when the user says 'streams', 'lazy evaluation', 'delay and force', 'infinite sequence', 'on-demand computation', 'memoized promise', 'thunk', 'prime sieve', 'SICP streams', 'tail recursion with streams', or when a computation should only run when the result is actually demanded. Pairs with: sicp-abstraction-and-interpretation, sicp-interpreter-evaluator, functional-programming, enterprise-integration-patterns, progressive-context-compressor."
---

# Streams and Lazy Evaluation

Streams let a program work with sequences that never fully exist in memory.
The key idea is simple: the tail of a stream is computed only when someone asks
for it.

## When to use

- Processing data too large (or unbounded) to materialize as a list.
- Building an on-demand pipeline where downstream consumption decides how much
  upstream work runs.
- Simulating a long-lived sequence (Fibonacci, prime numbers, event ticks)
  without recursion depth or allocation problems.

## delay and force

- `(delay expr)` packages the expression as a promise; nothing runs yet.
- `(force p)` runs the promise the first time and caches the result, so a
  forced promise never recomputes.
- A stream is a pair whose head is an element and whose tail is a delayed
  stream: `cons-stream` builds it, `stream-car` reads the head, and
  `stream-cdr` forces the tail on demand.

## Infinite streams

- `(define ones (cons-stream 1 ones))` — an infinite stream of 1s that only
  ever materializes what is read.
- Fibonacci and integer streams are built the same way: the tail refers to a
  delayed computation of the next element.
- The prime sieve filters an infinite integer stream by rejecting multiples of
  each found prime, one layer of laziness at a time.

## The lazy evaluator

- SICP rebuilds the interpreter with normal-order evaluation: arguments to
  procedures are delayed instead of evaluated eagerly, and forced only when a
  primitive needs the value.
- This gives the language a uniform way to express infinite structures and
  short-circuiting behavior without special forms for every case.
- Memoization matters: without caching, a normal-order evaluator recomputes an
  argument every time it is used; with it, each element is computed only once,
  the first time it is demanded.

Pairs with: sicp-abstraction-and-interpretation (the abstraction discipline
streams belong to), sicp-interpreter-evaluator (the lazy evaluator variant),
functional-programming, enterprise-integration-patterns (event streams),
progressive-context-compressor (on-demand rehydration).
