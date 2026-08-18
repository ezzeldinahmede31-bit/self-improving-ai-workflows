---
name: workflow-management-van-der-aalst
description: Applies Wil van der Aalst's Workflow Management to design and reason about process-aware information systems — workflow modeling with Petri nets and their formal semantics, workflow patterns (sequence, parallel split, synchronization, exclusive choice, merge, iteration, cancellation), soundness analysis of workflow nets, and the workflow management system (WfMS) architecture with its routing, resource, and data views. Use when the user says 'workflow management', 'Petri net', 'workflow patterns', 'soundness', 'van der Aalst', 'workflow net', 'WfMS', 'process modeling formal', 'routing constructs', 'workflow verification', or when designing an automated process that must be proven sound before execution. Pairs with: business-process-management-weske, fundamentals-of-bpm, process-mining, n8n-workflow, algorithmic-math-reasoner, state-machine-persistence.
---
# Workflow Management (van der Aalst)

Transfers van der Aalst's formal treatment of workflows — Petri nets and workflow patterns — so an automated process is modeled with precise semantics and proven sound before it runs.

## When to use
- Designing a process-aware system where correctness of control flow matters.
- Verifying that a workflow has no deadlocks, unreachable paths, or dangling tasks.
- Choosing the right routing construct for a branching or merging situation.

## The formal core
1. Model workflows as Petri nets (workflow nets) with one start and one end place; tokens, transitions, and firing rules give unambiguous semantics.
2. Use the classic workflow patterns — sequence, parallel split, synchronization, exclusive choice, merge, iteration, and cancellation — mapped to their net constructs.
3. Prove soundness: from the start marking, every state is reachable, the net can always reach completion, and no dead tasks remain; unsound nets fail at runtime in ways testing misses.
4. Build the WfMS as three views: process (control flow), resource (who/what executes), and data (case attributes and the information flow).

## Discipline
- Model before automating; the net is the executable contract.
- Verify soundness statically before deployment, then confirm with execution.
- Handle exceptions explicitly; cancellation and compensation are part of the model, not an afterthought.

## Verification discipline
- Check the workflow net for soundness (reachability of completion, absence of deadlock) before wiring to live systems.
- Test every branch construct with a minimal case, then with real data.
- Keep the model in sync with the running workflow; drift is the classic failure.

## Pairs with
business-process-management-weske, fundamentals-of-bpm, process-mining, n8n-workflow, algorithmic-math-reasoner, state-machine-persistence.