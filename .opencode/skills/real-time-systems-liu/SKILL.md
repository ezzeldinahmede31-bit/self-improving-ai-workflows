---
name: real-time-systems-liu
description: Applies Jane Liu's Real-Time Systems to hard real-time design: the characterization of real-time tasks, scheduling theory (rate-monotonic, earliest-deadline-first, fixed-priority and their schedulability analysis), priority inversion, resource access protocols, and the engineering of systems whose deadlines are part of correctness. Use when the user says 'real-time systems', 'rate monotonic', 'EDF', 'schedulability', 'deadline', 'priority inversion', 'priority ceiling', 'periodic task', 'Jane Liu', 'hard real-time', or when a system must guarantee that work finishes by a deadline.
---

# Real-Time Systems (Jane W. S. Liu)

Liu's book is the theoretical core of hard real-time scheduling. This skill applies that theory so a deadline is a guarantee, not a hope.

## Task modeling

- Model work as periodic, sporadic, or aperiodic tasks with cycle times, execution times, and deadlines.
- A feasible schedule exists when the utilization and deadline tests pass; compute them, do not guess.
- State the worst-case execution time honestly; the analysis depends on it.

## Fixed-priority scheduling

- Rate-monotonic assigns priority by period and is optimal for fixed priority; its utilization bound is a sufficient test.
- The exact response-time analysis gives the real check when the simple bound is too pessimistic.
- Harmonic cycle times make the utilization bound easier to satisfy; exploit the structure when possible.

## Dynamic scheduling and EDF

- Earliest-deadline-first is optimal on a single processor and uses all available capacity.
- EDF guarantees every deadline when total utilization does not exceed one.
- Overload is the danger: detect it and shed load deliberately instead of missing random deadlines.

## Resources and priority inversion

- Sharing a resource among real-time tasks can invert priority and blow deadlines.
- Priority inheritance and ceiling protocols bound the blocking time; use them on any shared resource.
- The blocking analysis is part of the schedulability test, not a footnote.

## Pairs with
operating-systems-three-easy-pieces, embedded-systems-architecture, distributed-control-systems-design, scheduling-theory-performance, queueing-theory-performance
