---
name: grpc-contract-testing
description: "gRPC contract testing distilled. Use when testing protobuf contracts, services, streaming RPCs, deadlines, error codes, buf breaking changes."
---

# gRPC Contract Testing

## Purpose

Keep gRPC services compatible: protobuf conformance, unary plus streaming coverage, deadline behavior, canonical error codes, breaking-change detection.

## When to use

Use when the user says 'gRPC test', 'protobuf', 'streaming RPC', 'deadline', 'error code', 'buf breaking'.

## Steps

1. Lock `.proto` files in version control; detect breaking changes in CI.
2. Test unary calls for request validity plus response shape.
3. Test streaming: client, server, and bidirectional flows with early-cancel cases.
4. Assert deadlines propagate and expirations surface as DEADLINE_EXCEEDED.
5. Assert canonical error codes (NOT_FOUND, INVALID_ARGUMENT) instead of messages.

## Anti-patterns

- Asserting on error message text across versions.
- Streaming tests that never cancel or time out.
- Proto changes merged without compatibility check.
- Deadlines tested only in happy-path timing.

## Example

Python:

```python
with pytest.raises(grpc.RpcError) as e:
    stub.GetOrder(request, timeout=1)
assert e.value.code() == grpc.StatusCode.DEADLINE_EXCEEDED
```

## Verification

Breaking-change check green, streaming cancel covered, deadlines asserted, codes canonical.

## Pairs-with

api-testing-contract-patterns, graphql-advanced-testing, websocket-event-testing, message-queue-testing.
