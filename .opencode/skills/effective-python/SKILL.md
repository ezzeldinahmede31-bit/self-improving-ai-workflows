---
name: effective-python
description: Applies Brett Slatkin's Effective Python to write clear, idiomatic, and correct Python through concrete rules: explicitness over magic, small helper functions, generators for large data, comprehensions used with restraint, exceptions that carry meaning, composition over inheritance, and disciplined testing. Encodes the rule-of-thumb checks that catch the most common Python defects before they ship. Use when the user says 'write idiomatic Python', 'python best practices', 'how should I structure this module', 'make this code maintainable', or 'what is the right Python idiom for this'.
---

# effective-python

Effective Python is a list of concrete rules, each with a clear why and a concrete before-and-after. This skill carries the rule-reflex forward: before accepting a piece of Python, run it through the checklist the book gives — is it explicit, small, idiomatic, and testable?

## Core principles

- Explicit is better than implicit, always.
- One obvious way to write something beats many clever ways.
- Small functions with one job are easier to test and reuse.
- Generators keep large data processing memory-safe.
- Exceptions should say what went wrong and be caught where action is possible.
- Favor composition and data classes over inheritance trees.

## Key patterns

- Keyword-only arguments make call sites self-documenting.
- Dataclasses replace verbose record classes.
- Context managers guarantee cleanup on any exit path.
- Generator expressions and zip/enumerate replace index soup.
- Raise early with a precise message; catch narrowly.
- Use pathlib for all filesystem paths.

## Applying this to scripting/automation/code

- Build n8n Code nodes as small pure functions with explicit inputs.
- Keep workflow transformations readable and testable.
- Make error paths visible in code instead of silent fallbacks.
- Write scripts that a reviewer can understand in one pass.

## Hard rules

- Never catch bare exceptions or swallow errors silently.
- Never use mutable objects as default arguments.
- Prefer dataclasses over hand-written record classes.
- Do not shadow builtin names.
- Keep functions short enough to test directly.
- Write a test for every behavior the module promises.

## Pairs with

code-linter-python-js, code-execution-guided-swemaster, test-driven-development, evidence-over-memory, pragmatic-programmer
