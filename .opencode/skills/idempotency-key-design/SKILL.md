---
name: idempotency-key-design
description: "Makes writes safe to repeat via natural or synthetic keys enforced at store. Use for payments, creates, side effects."
---

# Idempotency Key Design

Retries become harmless no-ops when keys are right.

## Workflow
1. Derive key from stable business identity (order ID, not timestamp).
2. Enforce uniqueness at store (constraint/upsert), not just check-before-write.
3. Store key with result for replay.

## Core Rules
- Stable identity over random.
- Scope keys narrowly: same key = same intended effect.

## Pairs with
- `retry-backoff-jitter`, `saga-compensation-flows`, `api-design-patterns`
