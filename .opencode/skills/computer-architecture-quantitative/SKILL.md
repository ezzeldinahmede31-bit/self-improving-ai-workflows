---
name: computer-architecture-quantitative
description: Applies Hennessy & Patterson's Computer Architecture: A Quantitative Approach to architecture-level decisions with data: the quantitative principles of design, instruction-level parallelism and superscalar execution, limits of ILP, memory hierarchy design, multiprocessors and coherence, and measuring architecture with benchmark-driven evaluation. Use when the user says 'quantitative approach', 'superscalar', 'instruction level parallelism', 'ILP', 'memory hierarchy design', 'cache coherence', 'multiprocessor', 'benchmark evaluation', 'Hennessy Patterson', 'architecture analysis', or when a hardware or performance decision must be justified with measurement.
---

# Computer Architecture: A Quantitative Approach (Hennessy & Patterson)

This is the graduate companion that replaces opinion with measurement. This skill applies its quantitative method to architecture, sizing, and performance decisions.

## Quantitative principles

- Make design decisions from measured costs: the rule is to focus optimization where the program actually spends its time.
- Track the relevant metrics (miss rate, cycles per instruction, throughput) and change one factor at a time.
- Use the geometric mean for ratios across benchmarks so no single outlier dominates the verdict.

## Instruction-level parallelism

- Superscalar and out-of-order execution extract parallelism from sequential code; the limit is the dependence chain.
- Branches, memory latency, and limited issue width bound the achievable speedup; model the bottleneck honestly.
- Write code that exposes parallelism: independent operations, predictable branches, and streaming access patterns.

## Memory hierarchy and coherence

- Design the hierarchy for the workload's access pattern: capacity, latency, and bandwidth trade off against cost.
- Multiprocessor coherence adds protocol overhead; keep shared data traffic low to avoid coherence misses.
- Latency hiding (prefetching, multithreading, out-of-order) only helps when there is independent work to overlap.

## Benchmark-driven evaluation

- Choose benchmarks that resemble the real workload; the wrong benchmark misleads every conclusion.
- Report the setup, the inputs, and the environment so the result is reproducible.
- A single-number verdict hides the distribution; show the spread across the benchmark suite.

## Pairs with
computer-organization-design, computer-systems-programmers-perspective, multiprocessor-concurrency, systems-performance-profiling, distributed-systems-concepts-design
