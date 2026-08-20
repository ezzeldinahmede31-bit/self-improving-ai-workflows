---
name: linux-kernel-scheduler
description: Applies the process-scheduling chapters of Robert Love's Linux Kernel Development to understand and tune how the Linux kernel chooses which task runs: the scheduler's goals and structure, CFS and virtual runtime, preemption and context-switch cost, and the real-time scheduling classes. Use when the user says 'how does Linux schedule tasks', 'CFS', 'virtual runtime', 'scheduler', 'preemption', 'nice value', 'real-time scheduling', 'SCHED_FIFO', 'SCHED_RR', 'context switch', 'kernel scheduling', 'Robert Love', or when reasoning about which process runs and why.
---

# Linux Kernel Development: The Scheduler

The scheduler decides which runnable task gets the CPU and for how long, and that decision shapes system responsiveness and throughput. Robert Love's Linux Kernel Development explains the design in terms of goals and mechanisms, from the per-CPU run queues to CFS's virtual runtime. This skill encodes the model for understanding and tuning scheduling behavior.

## Scheduler Goals and Structure
- The scheduler must balance responsiveness, throughput, fairness, and per-CPU cache affinity — no single metric wins.
- Scheduling runs in two contexts: an explicit schedule call when a task yields or sleeps, and a preemption when a higher-priority task becomes runnable.
- Each CPU keeps its own run queue, which gives cache affinity and avoids lock contention on the hot path.
- Scheduler domains group CPUs so load balancing can move work while respecting topology.

## CFS and Virtual Runtime
- CFS (Completely Fair Scheduler) gives each task a virtual runtime that advances slower for higher-priority (lower nice) tasks.
- The task with the smallest virtual runtime runs next, so the CPU is shared proportionally to weight.
- Nice values map to weights; the weight ratio determines the slice of CPU each task receives.
- A task that sleeps accumulates virtual runtime credit, so interactive tasks wake to run promptly.

## Preemption and Context Switches
- Linux is a fully preemptive kernel: the scheduler can interrupt a running task whenever a more deserving one appears.
- Every context switch costs CPU — register saves, cache misses, TLB misses — so the scheduler is the constant that makes responsiveness cost something.
- Small timeslices keep latency low but raise switching overhead; the balance is tuned per workload.
- Measure with perf or the scheduler stats rather than guessing which factor dominates.

## Real-Time Classes and Tuning
- SCHED_FIFO and SCHED_RR give real-time tasks strict priority over the normal CFS class.
- SCHED_FIFO runs a task until it blocks or yields; SCHED_RR adds a time slice rotation for equal-priority real-time tasks.
- Real-time tasks can starve normal tasks, so assign them sparingly and verify the effect with load tests.
- Tune nice values for latency-sensitive batch work and reserve real-time priority for genuinely time-critical loops.

## Pairs with
linux-kernel-development, understanding-linux-kernel, operating-systems-three-easy-pieces, systems-performance-profiling, linux-administration-handbook
