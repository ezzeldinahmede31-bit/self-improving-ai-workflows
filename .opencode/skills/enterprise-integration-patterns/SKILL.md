---
name: enterprise-integration-patterns
description: "Applies Hohpe & Woolf's Enterprise Integration Patterns (EIP) to wiring systems together: Message Channel, Message Router, Content-Based Router, Splitter, Aggregator, Message Translator, Pipes-and-Filters, and asynchronous messaging with guaranteed delivery, idempotent consumers, and error channels. Encodes the rules that stop integration spaghetti in n8n workflows and service pipelines. Use when the user says 'integration patterns', 'message router', 'splitter', 'aggregator', 'message translator', 'pipes and filters', 'guaranteed delivery', 'idempotent consumer', 'dead letter', 'EIP', 'Hohpe', 'message channel', 'how do I connect these systems', or when a workflow becomes a tangle of point-to-point integrations. Pairs with: api-integration, webhook-automation, cloud-native-patterns, zero-trust-modular-decomposer."
---
# Enterprise Integration Patterns (EIP - Hohpe & Woolf)

EIP is the vocabulary of integration. Point-to-point spaghetti (every system calling every other system directly) is the disease; channels, routers, translators, and splitters are the cure. In n8n, sub-workflows and message buses are the channel layer.

## Core Patterns (decision guide)

| Pattern | Problem it solves | n8n mapping |
|---|---|---|
| Message Channel | Decouple senders from receivers | A queue/topic or a webhook endpoint |
| Content-Based Router | Route one message to the right consumer | Switch node keyed on content |
| Splitter | Break one message into many | SplitInBatches / Code splitter |
| Aggregator | Combine many messages into one | Merge node with correlation key |
| Message Translator | Convert across formats | Code node at the boundary |
| Pipes-and-Filters | Compose processing steps cleanly | Linear chain of sub-workflows |
| Guaranteed Delivery | Do not lose messages on failure | Persistent queue / retry + stored payload |
| Idempotent Consumer | Safe to receive duplicates | Dedup by message/event ID |
| Dead Letter / Error Channel | Capture and inspect failures | Error Trigger + storage of bad messages |

## Integration Design Rules

1. **Never point-to-point across more than a handful of systems** - introduce a channel/router layer.
2. **Translate at the boundary** - each system speaks its own dialect; a Message Translator converts, never the systems themselves.
3. **Idempotent consumers always** - assume duplicates; dedup by a stable message/event ID.
4. **Guaranteed delivery or acknowledge the loss** - if a failure can drop a message, store-then-send or use a persistent queue.
5. **Failure goes to a channel, not a black hole** - every error path routes to a Dead Letter/Error channel that someone observes.
6. **Correlation keys for aggregation** - the Aggregator needs a stable key to group related messages.

## Integration Anti-patterns (severity)

- **A1 - Integration spaghetti** (HIGH): Systems calling each other directly in a web. Fix: centralize through channels/routers.
- **A2 - No idempotency** (HIGH): Duplicate delivery creates duplicate orders/emails/writes. Fix: dedup by event ID.
- **A3 - Lost messages on failure** (HIGH): No retry, no storage, failure drops the message silently. Fix: guaranteed delivery + Dead Letter.
- **A4 - Translation everywhere** (MEDIUM): Every consumer re-translates the same payload. Fix: translate once at the boundary.
- **A5 - Unobserved error channel** (MEDIUM): Errors routed 'to the error branch' but nobody reads it. Fix: alert on Dead Letter.
- **A6 - Missing correlation** (MEDIUM): Aggregator cannot group because the key was dropped. Fix: preserve a stable correlation ID end-to-end.

## Verification

Trace one message through the full path: channel in, router decision, split/aggregate, boundary translation, error path. Confirm dedup ID survives the whole journey and a failed delivery lands in an observed error channel. Run the build gates to READY_FOR_DEPLOYMENT.
