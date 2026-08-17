---
name: the-goal-constraints
description: "Applies Eliyahu Goldratt's The Goal and the Theory of Constraints to operations, processes, and any flow you are responsible for: the goal is making money (for a business) — everything else is a means; find the single binding constraint in the flow, exploit it, subordinate everything else to it, elevate it, then recheck. Includes the drum-buffer-rope scheduling method, batch size and WIP reasoning, and local-efficiency traps (a cost-saving move that starves the constraint hurts throughput). Use when the user says 'why is our process slow', 'find the bottleneck', 'theory of constraints', 'drum buffer rope', 'improve throughput', 'reduce WIP', 'production line optimization', 'lean vs TOC', 'the goal', 'which step is the constraint', or when a pipeline, team, or factory flow needs real throughput improvement. Pairs with: thinking-theory-of-constraints, thinking-systems, systems-performance-profiling, elegant-puzzle-engineering-management."
---

# The Goal — The Theory of Constraints for Any Flow

Goldratt's novel teaches one idea that changed operations thinking: every system
has a single constraint that limits the whole, and throughput is improved by
managing that constraint — not by optimizing everything else.

## When to use

- A process, pipeline, team, or production line is slow or overwhelmed.
- You need to decide what to optimize first and what to leave alone.
- Diagnosing why a local improvement did not help overall output.

## The core: name the constraint
- The system's output is capped by its weakest link. Find it: where does work
  pile up, where is the queue longest, which step is always the last to finish?
- The constraint can be a machine, a person, a policy, or a market — look for the
  thing that, if improved, raises total throughput.
- Measure throughput at the system level (output of the whole), not per-step.

## The five focusing steps
1. **Identify** the constraint.
2. **Exploit** it: get the maximum output from it with the current resources —
   never let it idle, feed it the best work first.
3. **Subordinate** everything else: pace all other steps to the constraint's rate;
   overproducing upstream just creates WIP that clogs the flow.
4. **Elevate** the constraint: invest in it (add capacity, better tools, more
   people) only after steps 2-3.
5. **Repeat**: once the constraint moves, find the new one. Improvement is a
   loop, not a destination.

## Drum-buffer-rope
- **Drum**: the constraint sets the pace for the whole flow.
- **Buffer**: a deliberately sized safety stock of work in front of the constraint
  so it never starves.
- **Rope**: a signal pulling new work into the system at exactly the rate the
  constraint consumes it.
- Result: short lead times and low WIP without idling the bottleneck.

## The local-efficiency trap
- A step running at full capacity is not necessarily good — if it is not the
  constraint, its "efficiency" just creates inventory that waits.
- Optimizing a non-constraint does not raise system throughput; it can lower it
  by adding WIP and latency.
- Make the constraint visible and protect it from upstream variability.

## Verification
- State the system goal, name the single constraint, and define the throughput
  metric that will move.
- After a change, confirm total throughput rose and WIP fell — not just the
  local step's utilization.
- Re-run the five steps; the constraint you relieved is replaced by a new one.

## Pairs with
- `thinking-theory-of-constraints` — the mental model this skill applies.
- `thinking-systems` — the systems view (feedback, stocks, flows).
- `systems-performance-profiling` — finding the true bottleneck with data.
- `elegant-puzzle-engineering-management` — applying constraint logic to teams.