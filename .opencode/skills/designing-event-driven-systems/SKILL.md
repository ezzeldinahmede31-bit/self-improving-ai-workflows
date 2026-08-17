---
name: designing-event-driven-systems
description: "Applies Ben Stopford's Designing Event-Driven Systems to build decoupled, real-time event pipelines: event-centric thinking (events as facts, event streams as the integration backbone), event-driven topology (event gateways, event log / Kafka-style log as system of record), guaranteed delivery and exactly-once semantics, event versioning and schema evolution (schema registry), event sourcing and CQRS, and the operational reality of running streaming infrastructure. Use when the user says 'event-driven', 'events vs REST', 'build an event pipeline', 'Kafka', 'event sourcing', 'CQRS', 'schema registry', 'event versioning', 'outbox pattern', 'event backbone', 'async integration', 'real-time data', or when connecting services should stop calling each other directly and instead share a stream of facts. Pairs with: streaming-systems, api-integration, cloud-native-patterns, distributed-systems-concepts-design, n8n-subworkflow-modularizer."
---

# Designing Event-Driven Systems

Stopford's book: events are the most natural unit of change — instead of services
asking each other for data (request/response coupling), they publish immutable
facts to a shared stream, and whoever cares consumes them. The event log is the
system of record; services are derived views.

## When to use

- Services need data from each other but should not be coupled by direct calls.
- You need an audit-able history of everything that happened.
- You want near-real-time reactions to business events across services.

## The core model

1. **Events are facts.** An event is an immutable, timestamped statement that
   something happened (`OrderPlaced`, `PaymentCaptured`). Never update or delete
   an event; emit a new one. The log of events is the source of truth.
2. **The event log is the backbone.** Write events to a durable, ordered log
   (Kafka-style). Consumers replay it independently — they can catch up or rebuild
   their state at any time. This turns point-to-point integration into a hub.
3. **Event-driven topology**: an *event gateway* (or the log itself) is the
   integration layer; producers publish once, many consumers subscribe. No one
   owns another service's data — they own their *view* of it.

## Design rules

- **Schema evolution is a first-class problem.** Events outlive their producers.
  Version every event schema and keep a registry; consumers must tolerate
  `oldVersion` and `newVersion`. Never break a consumer with an incompatible
  change — add a new event or a new field instead.
- **Choose delivery semantics per link.** At-least-once + idempotent consumers
  is the pragmatic default. Exactly-once needs dedupe keys or transactional
  coordination — name what each link promises.
- **Prefer event sourcing + CQRS for stateful domains.** Write state as a stream
  of events (event sourcing), rebuild projections for reads (CQRS). You get
  history, replay, and audit for free. Apply it where history matters, not as a
  blanket rule.
- **The outbox pattern protects consistency.** When a write must both update a
  DB and emit an event, write the event into the DB in the same transaction, then
  a relay publishes from the outbox. Avoids the dual-write problem.
- **Avoid synchronous calls inside an event flow.** An event handler that calls
  another service synchronously reintroduces coupling; emit an event and let the
  next stage consume it.

## Operational reality
- A log is infrastructure: monitor lag, retention, and partition health. Design
  partitions around the key you need ordered (per entity id), and size partitions
  for the consumer parallelism you need.
- Backpressure: consumers slower than producers is the normal failure. Design
  for it (consumer groups, buffer, dead-letter handling) rather than hoping.

Pairs with: streaming-systems (time/watermarks semantics), api-integration
(webhooks/async patterns), cloud-native-patterns (async wiring), n8n-subworkflow-
modularizer (applying the same decoupling in n8n).