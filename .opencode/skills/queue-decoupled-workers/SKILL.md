---
name: queue-decoupled-workers
description: "Decouples producers/consumers via durable queues for independent scale/fail. Use for async pipelines."
---

# Queue-Decoupled Workers

Direct chains couple availability; queues absorb bursts.

## Workflow
1. Split direct call -> produce + consume.
2. Message carries full context + correlation ID.
3. Consumer idempotent, poison -> dead-letter after bounded attempts.
4. Monitor depth/age.

## Core Rules
- Scale consumers on depth/latency.

## Pairs with
- `event-driven-ai-workflows`, `queueing-theory-performance`, `dead-letter-error-routes`
