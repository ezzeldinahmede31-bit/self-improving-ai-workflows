---
name: drepper-memory-hierarchy
description: "Exploits the memory hierarchy: caches, NUMA, prefetching, and measurement. Use when the user says 'cache friendly', 'false sharing', 'NUMA', 'prefetching', 'memory bandwidth', 'cache misses', 'Drepper', 'what every programmer should know about memory', or when performance lives or dies in RAM."
---

# Drepper Memory Hierarchy

Distilled from Ulrich Drepper's *What Every Programmer Should Know About
Memory*: CPUs got fast, RAM did not — performance IS memory access patterns.
Seven sections compressed into working rules with numbers.

## Purpose

Make software cache-conscious and NUMA-aware: measure misses, fix layout,
and prove the gain — the highest-ROI performance work on modern hardware.

## The rules (each with its reason)

1. **Know the numbers (measure YOURS).** L1 ~1ns, L2 ~3-4ns, L3 ~10-15ns,
   RAM ~60-100ns, NUMA-remote RAM worse. A cache miss costs hundreds of
   cycles — the entire game is miss rate × miss penalty. Get real numbers
   from lmbench/perf on the target machine; rules of thumb tune, data decides.
2. **Sequential beats strided beats random.** Prefetchers (hardware +
   software `__builtin_prefetch`) hide latency only for predictable streams.
   Data layout follows ACCESS order: struct-of-arrays for scanned fields,
   array-of-structs only when whole records are touched together.
3. **Fit working sets to levels.** Block/tiling (loops restructured so the
   inner kernel lives in L1/L2); problem-size awareness (algorithm choice
   changes at cache boundaries — the fastest O(n log n) loses to a tiled
   O(n²) below the threshold). Cache-oblivious designs where sizes vary.
4. **Kill false sharing.** Independently-written variables sharing a cache
   line ping-pong across cores ( atomics/counters per-thread, then combine;
   align/pad hot shared structures to line boundaries). Multithreaded
   slowdowns that scale INVERSELY with cores scream false sharing — confirm
   with perf c2c before restructuring.
5. **NUMA: allocate local, thread local.** First-touch policy means the
   allocating thread's node owns the pages — initialize data where it will
   be used (parallel init!), pin threads to cores, keep per-node pools.
   Remote-node access is a different performance regime; design for it or
   suffer it.
6. **Bandwidth is shared and finite.** Streaming workloads saturate the bus
   long before cores saturate; concurrent streams interfere. Budget GB/s per
   socket; compress in flight (bandwidth vs compute trade, measured).

## Verification

Optimization ships with: perf-counter evidence (miss rates, bandwidth) before
AND after, on the production-class machine — never laptop numbers for server
claims. No counters, no conclusion.

## Pairs with

- `computer-systems-programmers-perspective` (architecture basics),
  `systems-performance-profiling` (measurement method),
  `bpf-performance-tools` (hardware counters),
  `multiprocessor-concurrency` (sharing discipline).
