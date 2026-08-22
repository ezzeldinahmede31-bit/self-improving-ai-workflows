---
name: state-machine-workflow-modeling
description: "Represents workflows as explicit state machines with persisted state. Use for multi-step status flows."
---

# State-Machine Workflow Modeling

Implicit state -> fragile. Explicit machines are enumerable.

## Workflow
1. Enumerate states, events, guards, terminal states.
2. Declare transitions, guarded + logged.
3. Persist state atomically with event.
4. Illegal transitions fail loudly.

## Core Rules
- Every situation maps to one named state.

## Pairs with
- `state-machine-persistence`, `workflow-management-van-der-aalst`, `saga-compensation-flows`
