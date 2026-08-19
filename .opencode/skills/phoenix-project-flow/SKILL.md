---
name: phoenix-project-flow
description: Applies the Theory of Constraints from The Phoenix Project (Kim, Behr, Spafford) to IT operations and delivery: the goal is throughput of the whole value stream, not utilization of any one team; identify the single system bottleneck (the constraint), exploit it, subordinate everything else, elevate it, then recheck. Covers the Four Types of Work (business projects, IT operations, internal projects, changes), the work center, DevOps improvements as a constraint-breaker, and the improvement kata of daily standups that attack the bottleneck. Use when the user says 'why is IT delivery slow', 'bottleneck', 'theory of constraints in IT', 'four types of work', 'Phoenix Project', 'DevOps kata', 'value stream', 'work center', 'improve throughput of IT', 'unplanned work', or when IT projects keep slipping because operations is overwhelmed.
---

The Phoenix Project turns an IT organization around by treating the value stream like a factory line with one true bottleneck. This skill encodes that method so IT delivery problems get diagnosed by constraint, not by heroics.

## Operating rule
Throughput of the whole system is the goal. Local optimization (keeping one team busy) is a trap. Find the one constraint that limits the whole value stream, and attack it.

## Five focusing steps (the improvement loop)
1. IDENTIFY the constraint: find the step that queues up behind itself — the slowest, most-loaded step that everything else waits on. In IT it is often not the servers but a single team, a review process, or unplanned work flooding a group.
2. EXPLOIT the constraint: get the most from it without adding staff. Reduce the work it must do, kill waste, batch sensibly.
3. SUBORDINATE everything else: all other steps must not overproduce or starve the constraint. Buffer the constraint so it never idles.
4. ELEVATE the constraint: only now buy more capacity — more people, faster tools, more automation.
5. RECONNECT: after elevating, the constraint moves elsewhere. Repeat from step 1.

## The Four Types of Work
- Business projects: work that directly serves a business goal.
- IT operations: keeping existing systems running.
- Internal projects: IT's own improvements and infrastructure.
- Changes: the requests that modify systems.
Unplanned work (fires, interruptions) is the deadliest: it steals the constraint's capacity and hides the real bottleneck. An environment drowning in unplanned work must first reduce change failures before anything else.

## The work center view
Work moves through IT in a pipeline: development -> change request -> change approval -> deployment -> operation. Look at every queue at each handoff. The step with the longest queue and the longest wait is the bottleneck, not the step that feels busiest.

## Daily improvement kata
Run a daily standup that asks one question: what is constraining the value stream today, and what single experiment shrinks it? Small daily experiments, measured each week, outrun big annual initiatives.

## Applying this to n8n/automation builds
- When designing an automation, first name the constraint the automation removes. If it does not remove a real queue, it is busywork.
- When a team is overwhelmed, the fix is rarely 'more automations'; it is stopping unplanned work at the source and shrinking the queue at the bottleneck.
- Treat a slow workflow like a factory line: instrument every step, find the step with the largest queue/wait, and optimize only that step first.

## Hard rules
- Never optimize a non-constraint step while the real bottleneck sits unattended; it only makes the queue longer.
- Never claim 'the system is faster' without a before/after measurement of the whole value stream lead time.
- Unplanned work is a symptom of upstream failure; fix the source (better change approval, better testing) instead of absorbing it.
- The goal is throughput of work that the business values, not utilization of every worker.

## Worked pattern: a slow order-to-cash flow
Suppose orders pile up in a fulfillment step. Constraint analysis: identify the step where the queue grows and wait time is longest (fulfillment), exploit it (batch orders, remove rekeying), subordinate upstream (do not let sales produce more than fulfillment can handle), elevate (automate data entry), then recheck — the bottleneck will move to the next queue.

## Pairs with
devops-handbook-flow, value-stream-mapping, the-goal-constraints, thinking-theory-of-constraints, systems-performance-profiling, accelerate-dora-metrics, sre-reliability-engineering, continuous-delivery-pipeline.
