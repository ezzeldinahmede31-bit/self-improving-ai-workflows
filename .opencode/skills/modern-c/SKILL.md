---
name: modern-c
description: Applies Jens Gustedt's Modern C to write safe, portable, maintainable C11/C17: explicit types, bounds-aware design, memory ownership discipline, error handling as data, and checked arithmetic. Encodes the modern idioms that eliminate the classic C failure modes (silent overflow, off-by-one access, uninitialized state) so C code is correct by construction. Use when the user says 'write C code', 'C11 or C17', 'safe memory management in C', 'design a C API', 'avoid undefined behavior', or 'how should I structure this C program'.
---

# modern-c

Modern C is about treating the language the way it was meant to be used: with explicit types, disciplined ownership, and a compiler that is enlisted as an ally rather than ignored. This skill carries the book's safety-first discipline into every C program, from a small utility to a native kernel.

## Core principles

- Make types explicit; let the compiler catch mistakes at build time.
- Bounds and sizes are part of the design, not an afterthought.
- Memory ownership is explicit: whoever allocates is whoever frees.
- Errors are data returned and checked, not hidden or assumed.
- Undefined behavior is unacceptable, never merely unlikely.
- Small functions with clear contracts over long clever ones.

## Key patterns

- Index and size with size_t, never int, for arrays and loops.
- Use designated initializers and static assertions to document intent.
- Prefer enums and constants over magic numbers.
- Check every allocation and every input before use.
- Use checked arithmetic helpers instead of relying on overflow.
- Wrap each resource with a paired cleanup function (RAII style).

## Applying this to scripting/automation/code

- Write performance-critical kernels and native helpers with safe idioms.
- Structure n8n code and tooling that wraps C libraries with clear boundaries.
- Build parser and protocol code that is bounds-checked everywhere.

## Hard rules

- Always check the result of an allocation before using it.
- Initialize every variable before it is read.
- Keep pointer arithmetic inside known, verified bounds.
- Use stdint fixed-width types for portable data layouts.
- Never let arithmetic overflow silently.
- Free memory in the same scope and level that allocated it.

## Pairs with

computer-systems-programmers-perspective, operating-systems-three-easy-pieces, systems-performance-profiling, code-execution-guided-swemaster, evidence-over-memory
