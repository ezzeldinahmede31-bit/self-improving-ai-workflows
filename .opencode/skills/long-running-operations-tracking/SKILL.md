---
name: long-running-operations-tracking
description: "Models multi-minute/day jobs as operation resources with status/progress/resume. Use for jobs outliving one request."
---

# Long-Running Operations Tracking

Jobs that outlive a request need lifecycle tracking.

## Workflow
1. Start returns operation ID, status resource.
2. Enumerate states: queued/running/succeeded/failed/cancelled.
3. Persist checkpoints to resume after interruption.
4. Notify on terminal states.

## Core Rules
- Support cancellation with cleanup.

## Pairs with
- `api-long-running-operations`, `state-machine-persistence`, `agentic-workflows`
