---
name: advanced-python-programming
description: Applies Quan Nguyen's Advanced Python Programming to build high-performance, concurrent, and maintainable Python systems: profiling-driven optimization, threading and multiprocessing with the GIL understood, async programming, memory management, and integrating compiled extensions. Encodes the discipline of choosing the concurrency model by workload and building components that are safe, reusable, and measured. Use when the user says 'concurrency in Python', 'threads or processes or asyncio', 'build a high-performance Python service', 'GIL', 'profile and optimize', or 'integrate a C extension'.
---

# advanced-python-programming

Advanced Python is about the seams: where performance, concurrency, and memory meet everyday Python. The book teaches you to profile first, then pick the right tool — threads, processes, or asyncio — and to understand the GIL well enough to work around it honestly instead of guessing.

## Core principles

- Choose the concurrency model by the workload, not by fashion.
- Understand the GIL: it serializes CPU-bound threads, so use processes there.
- Measure before and after every change.
- Design components to be reusable and thread-safe by contract.
- Keep memory behavior explicit and bounded.
- Keep the module small and the interfaces clear.

## Key patterns

- Process pools for CPU-bound work; thread pools for I/O-bound work.
- Async/await pipelines for many concurrent I/O operations.
- Worker queues with bounded size to control backpressure.
- Cython and ctypes for hot loops and native-library integration.
- Caching and memoization with bounded stores.
- Context managers that guarantee cleanup of pools and connections.

## Applying this to scripting/automation/code

- Scale out n8n Code nodes that process many items or call external APIs.
- Keep long-running automation jobs responsive and crash-clean.
- Integrate native libraries behind a small, testable Python wrapper.
- Bound resource use so a busy workflow does not exhaust the machine.

## Hard rules

- Never share mutable state across threads without a lock.
- Know that the GIL caps CPU-bound threading; prefer processes there.
- Always close pools and connections on every exit path.
- Cap worker and queue sizes to bound resource use.
- Test concurrency under realistic load before trusting it.
- Document what is thread-safe and what is not.

## Pairs with

systems-performance-profiling, computer-systems-programmers-perspective, code-execution-guided-swemaster, evidence-over-memory, code-linter-python-js
