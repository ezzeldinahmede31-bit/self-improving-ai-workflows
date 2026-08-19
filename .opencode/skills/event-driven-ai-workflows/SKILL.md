---
name: event-driven-ai-workflows
description: "Applies event-driven architecture to AI workflows: events as facts, async decoupling, queues and topics, delivery semantics (a message may arrive more than once), idempotent consumers, outbox pattern, and failure handling for LLM-driven pipelines. Turns brittle request-response automations into resilient stream-shaped systems. Use when the user says 'event-driven', 'async workflow', 'event backbone', 'message queue', 'outbox', 'idempotent consumer', 'event sourcing', or 'decouple my pipeline'."
---
# event-driven-ai-workflows

Event-driven architecture makes AI workflows resilient and decoupled: producers emit facts, brokers carry them, and consumers react. This skill encodes the messaging patterns that keep LLM-heavy automations reliable when requests arrive asynchronously, in bursts, or in the wrong order.

## Core principles
- An event is an immutable fact about what happened, not an instruction about what to do next.
- Decouple producers from consumers through a broker; a producer must never know the consumer's address.
- Consumers must be idempotent: the same event arriving twice must not produce two side effects.
- Delivery may duplicate, so every consumer must handle replays; never assume exactly-once delivery.
- A failed consumer must not block the stream; dead-letter the event and alert, do not silently drop it.

## Key patterns
- Event stream: a durable log of facts (Kafka-style) used as the system of record for the pipeline.
- Outbox: write the event in the same transaction as the state change, then publish from the outbox.
- Queue: delivery may duplicate, so consumers are idempotent; retries with a DLQ capture poison events.
- Idempotent consumer: deduplicate on an event ID before running the side effect.
- Saga orchestration: each step emits the next event; compensations undo completed steps on failure.
- Event versioning: a schema registry so consumers tolerate older event shapes during rollout.

## Applying this to n8n/Python automation
- Use a broker (Redis, RabbitMQ, or an HTTP queue) in front of heavy LLM nodes so bursts do not pile up at the trigger side.
- Model the outbox in n8n: write the fact to a data table in the same step that changes state, then a scheduler drains it.
- Deduplicate with a Redis key or data-table lookup keyed on the event ID before calling the model.
- On model failure, route to a DLQ and alert rather than replaying blindly into the same error.
- Version events by adding a schema field; keep readers tolerant of older shapes while migrating.

## Hard rules
- Never send an event before the underlying state change is committed.
- Never build a consumer that is not idempotent on its event ID.
- Never drop a poison event without a dead-letter record and an alert.
- Never assume exactly-once delivery from any broker.

## Pairs with
ai-engineering-foundation-models, designing-machine-learning-systems, multi-agent-patterns, context-engineering, build-gates-pipeline, n8n-workflow
