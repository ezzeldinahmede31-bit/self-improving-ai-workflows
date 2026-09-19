---
name: websocket-event-testing
description: "WebSocket and event testing distilled. Use when testing sockets, subscriptions, reconnects, ordering, backpressure, event contracts."
---

# WebSocket Event Testing

## Purpose

Test real-time channels: connect and subscribe flows, reconnect behavior, message ordering, backpressure, event schema conformance.

## When to use

Use when the user says 'WebSocket test', 'socket.io', 'subscription test', 'reconnect', 'message ordering', 'event schema'.

## Steps

1. Test connect, subscribe, message, unsubscribe, close as a lifecycle.
2. Kill and restore connections; assert resume plus missed-event handling.
3. Assert ordering guarantees where the contract promises them.
4. Validate event payloads against schemas on publish and receive.
5. Load the channel to observe backpressure and slow-consumer handling.

## Anti-patterns

- Happy-path socket tests with no reconnect coverage.
- Asserting arrival order the contract never promises.
- Unvalidated event payloads drifting across versions.
- Load tests ignoring slow-consumer disconnects.

## Example

JS:

```js
socket.emit('subscribe', { channel: 'orders' });
const msg = await nextMessage('orders');
expect(msg).toMatchObject({ type: 'ORDER_CREATED' });
```

## Verification

Lifecycle covered, reconnect semantics proven, schemas validated, backpressure observed.

## Pairs-with

grpc-contract-testing, message-queue-testing, async-testing-patterns, api-testing-contract-patterns.
