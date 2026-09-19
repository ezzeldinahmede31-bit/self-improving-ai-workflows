---
name: message-queue-testing
description: "Message queue testing distilled. Use when testing queues, topics, ordering, redelivery, dead letters, idempotent consumers, backpressure."
---

# Message Queue Testing

## Purpose

Prove async messaging correct: delivery semantics, ordering where promised, redelivery, dead-letter routing, idempotent consumers, backpressure.

## When to use

Use when the user says 'queue test', 'Kafka test', 'RabbitMQ', 'dead letter', 'redelivery', 'idempotent consumer', 'ordering'.

## Steps

1. Assert delivery semantics per contract (once versus effective-once).
2. Test redelivery: poison messages reach dead letters with context.
3. Prove consumer idempotency under duplicate delivery.
4. Verify ordering only where the broker promises it (keyed partitions).
5. Saturate consumers to observe lag, backpressure, and scaling.

## Anti-patterns

- Assuming global ordering on unordered topics.
- No dead-letter queue, so poison blocks the partition.
- Non-idempotent handlers billed twice on redelivery.
- Lag dashboards missing while queues grow silently.

## Example

Python:

```python
publish(order_created); publish(order_created)  # duplicate
assert consumer.effects() == [charge_once]      # idempotent
```

## Verification

Semantics documented per topic, dead letters routed with context, duplicates safe, lag alerted.

## Pairs-with

grpc-contract-testing, websocket-event-testing, designing-event-driven-systems, streaming-systems.
