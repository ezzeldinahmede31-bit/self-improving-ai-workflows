---
name: high-performance-python
description: Applies High Performance Python by Micha Gorelick and Ian Ozsvald to make Python fast with evidence, not guesses: profile first, choose the right algorithm and data structure, vectorize with numpy, use multiprocessing and asyncio for the right workload, and drop to compiled extensions for hot loops. Encodes the discipline that every optimization starts from a measured baseline and ends with a re-measurement. Use when the user says 'why is my Python slow', 'profile this code', 'vectorize with numpy', 'speed up this loop', 'parallelize my script', or 'optimize this bottleneck'.
---

# high-performance-python

Python is slow by default and fast by design when you pick the right lever. The book's core move is measurement: find the hot path first, then apply the technique that actually addresses it, then re-measure. This skill encodes that profiling-first discipline and the technique catalog.

## Core principles

- Never optimize without a measured baseline.
- The right algorithm and data structure beat micro-optimization.
- Vectorize with numpy before reaching for loops.
- Choose the concurrency model by workload: I/O-bound or CPU-bound.
- Keep memory bounded; big data is processed in chunks.
- Re-measure after every change to prove the gain.

## Key patterns

- Profile with cProfile and line_profiler to find the real hot path.
- Use numpy broadcasting and ufuncs instead of interpreted loops.
- Parallelize CPU-bound work with process pools.
- Parallelize I/O-bound work with asyncio.
- Drop to Cython or CFFI for the narrow hot loop that nothing else fixes.
- Memoize and cache repeated computation with bounded caches.

## Applying this to scripting/automation/code

- Profile slow n8n Code nodes before touching them.
- Vectorize data transforms that run on large arrays.
- Chunk big payloads so memory stays flat.
- Add concurrency only where the workload rewards it.

## Hard rules

- Keep the unoptimized version as the correctness reference.
- Bound memory use; do not materialize data you can stream.
- Prefer numpy loops over Python loops in hot paths.
- Avoid premature parallelism; measure the gain first.
- Re-profile after every change before declaring victory.
- Document the baseline and the result of each optimization.

## Pairs with

systems-performance-profiling, computer-systems-programmers-perspective, code-execution-guided-swemaster, evidence-over-memory, database-internals-engines
