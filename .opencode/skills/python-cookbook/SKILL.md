---
name: python-cookbook
description: Applies the Python Cookbook by David Beazley and Brian K. Jones to solve everyday programming problems with idiomatic Python: the right data structure for the job, generators and iterators that stay lazy, string and text handling, class and function design, I/O and files, and concurrency. Encodes the recipes as transferable patterns so a solution is built from proven pieces instead of invented ad hoc. Use when the user says 'how do I do this in Python', 'a recipe for', 'idiomatic Python', 'parse this text', 'iterate over that data', or 'write this class cleanly'.
---

# python-cookbook

The Cookbook is a pattern library: each entry names a problem, shows the idiomatic solution, and explains why it beats the naive one. This skill carries that habit forward — before writing Python, name the problem, then reach for the known recipe and adapt it.

## Core principles

- Pick the data structure that matches the operation you actually run.
- Prefer generators and iterators so large data is never materialized eagerly.
- Use named records (namedtuple, dataclass) instead of raw dicts for structure.
- Manage resources with context managers, never manual open and close.
- Prefer composition and delegation over deep inheritance trees.
- Reach for the standard library before any third-party dependency.

## Key patterns

- Deque for bounded history; heapq for priority access; itertools for chaining.
- Generator pipelines that transform data one element at a time.
- Classes that expose a small protocol instead of many ad hoc methods.
- functools partial and wraps for callable composition.
- Thread or process pools for parallel work with clean results.
- Robust parsing that handles missing and malformed input gracefully.

## Applying this to scripting/automation/code

- Write n8n Code nodes as small, pure functions built from the recipes.
- Keep pipeline steps lazy so memory stays flat on large payloads.
- Use dataclasses for workflow records instead of fragile dict paths.
- Wrap every file or connection in a context manager so it always closes.
- Build result handling that fails predictably on bad input.

## Hard rules

- Never mutate a collection while iterating over it.
- Always close resources with a context manager.
- Keep generators lazy; do not convert them to lists unless required.
- Document any one-liner that is not obvious to a reader.
- Test edge inputs (empty, malformed, missing keys) on every recipe.
- Prefer the standard library until a third-party package clearly wins.

## Pairs with

code-linter-python-js, code-execution-guided-swemaster, evidence-over-memory, database-internals-engines, systems-performance-profiling
