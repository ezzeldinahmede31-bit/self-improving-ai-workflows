---
name: enterprise-integration-patterns
description: Applies Hohpe & Woolf's Enterprise Integration Patterns (EIP) to wiring systems together: Message Channel, Message Router, Content-Based Router, Splitter, Aggregator, Message Translator, Pipes-and-Filters, and asynchronous messaging with guaranteed delivery, idempotent consumers, and error channels. Encodes the rules that stop integration spaghetti in n8n workflows and service pipelines. Use when the user says 'integration patterns', 'message router', 'splitter', 'aggregator', 'message translator', 'pipes and filters', 'guaranteed delivery', 'idempotent consumer', 'dead letter', 'EIP', 'Hohpe', 'message channel', 'how do I connect these systems', or when a workflow becomes a tangle of point-to-point integrations. Pairs with: api-integration, webhook-automation, cloud-native-patterns, zero-trust-modular-decomposer.
---

# Enterprise Integration Patterns (EIP) Skill

## Core Philosophy: Messaging as Integration Backbone

> "Enterprise integration goes beyond creating a single distributed application... integrated applications are independent programs that function by coordinating with each other in a loosely coupled way."

**Four integration styles** (choose one):
1. **File Transfer** — batch, high latency
2. **Shared Database** — tight coupling, schema dependency
3. **Remote Procedure Invocation** — synchronous, tight coupling
4. **Messaging** — asynchronous, loose coupling (RECOMMENDED)

**EIP mandate**: Use messaging for decoupled, resilient integration.

---

## Pattern Catalog (65 Patterns, 9 Categories)

### 1. Channel Patterns (Transport)
| Pattern | Purpose | n8n Equivalent |
|---------|---------|----------------|
| **Point-to-Point Channel** | One consumer per message | Queue node |
| **Publish-Subscribe Channel** | Multiple consumers | Webhook + multiple listeners |
| **Datatype Channel** | Separate channel per data type | Type-based routing |
| **Invalid Message Channel** | Handle malformed messages | Error Trigger |
| **Dead Letter Channel** | Store unprocessable messages | Dead Letter Queue node |
| **Guaranteed Delivery** | Message persists until consumed | Persistent queue + ack |
| **Channel Adapter** | Connect app to messaging | HTTP Request, Webhook |
| **Messaging Bridge** | Connect channel types | Cross-platform sync |
| **Message Bus** | Shared infrastructure | Kafka, RabbitMQ, n8n queue |

### 2. Message Construction
| Pattern | Purpose |
|---------|---------|
| **Command Message** | Invoke procedure in receiver |
| **Document Message** | Transfer data (no behavior) |
| **Event Message** | Notify of occurrence |
| **Request-Reply** | Synchronous over async |
| **Correlation Identifier** | Match request to reply |
| **Message Sequence** | Order related messages |
| **Format Indicator** | Declare message format |

### 3. Message Routing (Core for n8n)
| Pattern | Purpose | n8n Node |
|---------|---------|----------|
| **Content-Based Router** | Route by message content | IF / Switch |
| **Message Filter** | Discard unwanted | IF (filter) |
| **Dynamic Router** | Runtime routing rules | Custom routing logic |
| **Recipient List** | Multiple destinations | Multiple outputs |
| **Splitter** | Break composite message | Split In Batches |
| **Aggregator** | Combine related messages | Merge |
| **Resequencer** | Reorder messages | Sort + Wait |
| **Composed Message Processor** | Multi-step processing | Sub-workflow |
| **Scatter-Gather** | Broadcast + collect | Fan-out + Fan-in |
| **Routing Slip** | Dynamic route sequence | Dynamic workflow |
| **Process Manager** | Stateful orchestration | State machine |
| **Message Broker** | Central routing hub | n8n as broker |

### 4. Message Transformation
| Pattern | Purpose | n8n Node |
|---------|---------|----------|
| **Envelope Wrapper** | Wrap/unwrap payload | Set / Code |
| **Content Enricher** | Augment with external data | HTTP Request + Merge |
| **Content Filter** | Remove unwanted fields | Set (keep only) |
| **Claim Check** | Store large payload externally | S3 + reference |
| **Normalizer** | Canonical format | Set / Code |
| **Canonical Data Model** | Shared schema | Type definitions |

### 5. Message Endpoints (Consumers/Producers)
| Pattern | Purpose | n8n Node |
|---------|---------|----------|
| **Messaging Gateway** | Hide messaging from app | Webhook trigger |
| **Messaging Mapper** | Map domain ↔ message | Set / Code |
| **Transactional Client** | Atomic send/receive | Transactional DB + queue |
| **Polling Consumer** | Pull on demand | Schedule trigger |
| **Event-Driven Consumer** | Push on arrival | Webhook trigger |
| **Competing Consumers** | Load balance | Multiple workers |
| **Message Dispatcher** | Route to handler | Router |
| **Selective Consumer** | Filter by criteria | IF on trigger |
| **Durable Subscriber** | Persistent subscription | Queue with persistence |
| **Idempotent Receiver** | Handle duplicates | Deduplication |
| **Service Activator** | Invoke service from message | Any action node |

### 6. System Management
| Pattern | Purpose |
|---------|---------|
| **Control Bus** | Manage messaging system |
| **Detour** | Route around problems |
| **Wire Tap** | Inspect without consuming |
| **Message History** | Audit trail |
| **Message Store** | Persistent message log |
| **Smart Proxy** | Add behavior transparently |
| **Test Message** | Validate flow |
| **Channel Purger** | Clean up |

---

## n8n-Specific Pattern Mapping

| EIP Pattern | n8n Implementation |
|-------------|---------------------|
| **Message Channel** | Connections between nodes |
| **Message** | Item (JSON object) flowing through |
| **Content-Based Router** | IF node, Switch node |
| **Splitter** | Split In Batches, Item Lists |
| **Aggregator** | Merge node (all modes) |
| **Message Translator** | Set node, Code node |
| **Message Filter** | IF node (continue on false) |
| **Dead Letter Channel** | Error Trigger workflow |
| **Guaranteed Delivery** | Queue mode + persist data |
| **Idempotent Receiver** | Deduplication node / dedupe keys |
| **Scatter-Gather** | Split In Batches + Merge |
| **Process Manager** | State machine workflow |
| **Wire Tap** | Copy item to debug/log branch |

---

## Anti-Patterns to Avoid

| Anti-Pattern | EIP Fix |
|--------------|---------|
| **Point-to-point spaghetti** | Message Broker / central routing |
| **Synchronous chains** | Async messaging + callbacks |
| **Shared database integration** | Canonical Data Model + events |
| **No error handling** | Dead Letter Channel + Error Trigger |
| **Duplicate processing** | Idempotent Receiver + dedupe keys |
| **Lost messages** | Guaranteed Delivery + persistence |
| **Format coupling** | Message Translator + Canonical Model |
| **Temporal coupling** | Event-Driven Consumer + async |

---

## Design Principles for n8n Workflows

1. **Every workflow has a trigger** (Messaging Gateway)
2. **Nodes = endpoints** (Service Activator)
3. **Connections = channels** (Message Channel)
4. **IF/Switch = Content-Based Router**
5. **Split/Merge = Splitter + Aggregator**
6. **Set/Code = Message Translator / Enricher / Filter**
6. **Error Trigger = Dead Letter Channel**
7. **Dedupe = Idempotent Receiver**
8. **Sub-workflows = Process Manager / Composed Processor**

---

## Decision Checklist for Any Integration

Before connecting systems:
1. **Async or sync?** Prefer async (messaging)
2. **One-to-one or one-to-many?** Pub-sub for many
3. **Ordering required?** Resequencer or partition by key
4. **Duplicates possible?** Idempotent Receiver mandatory
5. **Large payloads?** Claim Check (store externally)
6. **Schema evolution?** Canonical Data Model + versioning
7. **Failure handling?** Dead Letter + retry + alert
8. **Observability?** Wire Tap + Message History
9. **Testing?** Test Message pattern
10. **Monitoring?** Control Bus metrics

---

## Trigger Phrases

`integration patterns`, `message router`, `splitter`, `aggregator`, `message translator`, `pipes and filters`, `guaranteed delivery`, `idempotent consumer`, `dead letter`, `EIP`, `Hohpe`, `message channel`, `how do I connect these systems`

---

## Pairings

- `api-integration` — REST/webhook patterns
- `webhook-automation` — inbound integration
- `cloud-native-patterns` — resilience in integration
- `zero-trust-modular-decomposer` — isolation boundaries