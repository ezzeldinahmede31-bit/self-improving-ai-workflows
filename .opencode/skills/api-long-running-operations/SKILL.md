---
name: api-long-running-operations
description: Applies the long-running operations chapter of API Design Patterns (Geewax): model asynchronous jobs correctly with a standard resource that starts, reports progress, and yields a final result — with idempotent create, operation status endpoints, polling guidance, and webhook notifications. Use when the user says 'long-running operation', 'async job', 'operation resource', 'job status', 'polling', 'webhook notification', 'asynchronous API design', 'operationId', 'start a background job', 'progress endpoint', 'cancel a job', or when an API endpoint must start work that outlives a single request. Pairs with: api-design-patterns, api-integration, api-versioning-compatibility, webhook-automation, state-machine-persistence.
---

# API Long-Running Operations

Transfers the long-running operation (LRO) pattern from API Design Patterns (Geewax) to real APIs: turn blocking endpoints that take too long into a standard operation resource the client can start, poll, and cancel.

## When to use
- An endpoint that takes longer than a typical request timeout.
- Batch processing, exports, model inference, or any work with a completion time that varies widely.
- A client that must survive disconnects and resume by polling.

## The standard LRO shape
1. Create: `POST` returns 202 with an operation resource (its own URI).
2. Operation resource: fields for state (pending/running/done/failed), progress, and the final result or error.
3. Poll: `GET` the operation URI; the client polls with backoff, not tight loops.
4. Notify: optional webhook delivers completion so polling is unnecessary.
5. Cancel: a delete/cancel action that stops work and reports the partial outcome.

## Correctness requirements
- Idempotent create: a retried create returns the same operation, never a duplicate.
- State transitions are explicit and terminal states are final (done/failed/cancelled).
- The operation persists across client disconnects; state lives server-side, not in the client.
- Progress is monotonic and honest; errors surface in the operation body with a structured code.

## Verification discipline
- Test the full lifecycle: start, poll to done, verify the final result shape, and cancel a running op.
- Simulate a disconnect and confirm the client can resume polling without a new create.

## Pairs with
api-design-patterns, api-integration, api-versioning-compatibility, webhook-automation, state-machine-persistence.