---
name: eip-message-routing
description: "Applies the message-routing patterns of Enterprise Integration Patterns (Hohpe & Woolf) to wire decoupled message flows: the Message Router, Content-Based Router, Message Filter, Splitter, Aggregator, Resequencer, Recipient List, and Scatter-Gather — and when to use each so routing logic stays explicit and testable instead of embedded in code. Use when the user says 'message router', 'content-based router', 'splitter', 'aggregator', 'recipient list', 'scatter-gather', 'resequencer', 'message filter', 'routing logic', 'fan out', 'fan in', 'EIP routing', or when building an n8n or service flow that must branch, split, and rejoin messages. Pairs with: enterprise-integration-patterns, n8n-subworkflow-modularizer, api-integration, designing-event-driven-systems, state-machine-persistence."
---

# Message Routing (EIP)

Routing decides where each message goes. Done in dedicated nodes it stays
explicit and testable; buried in code it becomes untraceable.

## When to use

- Building flows that branch, filter, split, or rejoin messages.
- Keeping routing logic visible on the canvas rather than inside a script.
- Wiring fan-out and fan-in without coupling producers to consumers.

## The core patterns

- **Message Router** — a decision point that chooses one destination from the
  message content.
- **Content-Based Router** — the router's main flavor: inspect a field, pick the
  target. Express the routing table explicitly.
- **Message Filter** — drop messages that do not meet criteria, forward the
  rest.
- **Recipient List** — send the message to a dynamic set of destinations.

## Splitting and recombining

- **Splitter** — break one message into parts (one per line, per item, per
  record) and route each part onward.
- **Aggregator** — collect related parts and combine them once all have arrived;
  needs a correlation rule and a completion condition.
- **Scatter-Gather** — fan out a request to multiple workers, collect the
  replies, and aggregate them into one response.
- **Resequencer** — restore order after parts arrive out of order, using a
  sequence-number field.

## Wiring rules

- Put the routing decision in a dedicated node with a named expression, never in
  scattered conditionals.
- Define correlation keys and completion conditions explicitly for every
  aggregator.
- Dead-letter: route undeliverable messages to an error destination rather than
  dropping them silently.

Pairs with: enterprise-integration-patterns, n8n-subworkflow-modularizer,
api-integration, designing-event-driven-systems, eip-message-transformation.
