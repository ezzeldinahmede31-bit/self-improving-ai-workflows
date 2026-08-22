---
name: saga-compensation-flows
description: "Coordinates multi-step distributed actions with forward steps plus compensating undos. Use for cross-system transactions."
---

# Saga Compensation Flows

No DB transaction across systems — saga gives ordered steps + explicit undo.

## Workflow
1. List steps with compensating action (or skippable).
2. Order hardest-to-undo last.
3. Persist saga state outside memory (step, completed set).
4. Compensation itself idempotent.

## Core Rules
- Unresolved sagas escalate to humans.

## Pairs with
- `microservices-patterns`, `state-machine-persistence`, `event-driven-ai-workflows`
