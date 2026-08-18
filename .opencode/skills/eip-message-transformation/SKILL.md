---
name: eip-message-transformation
description: "Applies the message-transformation half of Hohpe & Woolf's Enterprise Integration Patterns (EIP) to reshape messages as they travel through an integration: Message Translator, Canonical Data Model, Envelope Wrapper, Content Enricher, Content Filter, Claim Check, and Normalizer. Encodes the rules that keep field names, encodings, and semantics consistent across different systems so each consumer receives exactly the shape it expects. Use when the user says 'message translation', 'canonical data model', 'enrich the payload', 'strip fields', 'claim check', 'normalize the data', 'field mapping', 'EIP transformation', 'convert formats', 'translate the message', or when two systems disagree on field names, units, or payload shape. Pairs with: eip-message-routing, enterprise-integration-patterns, api-integration, n8n-code-nodes-official, n8n-syntax-v2-enforcer."
---

# EIP Message Transformation

The routing patterns decide *where* a message goes; the transformation patterns
decide *what it looks like* when it arrives. Every integration boundary that
translates data is an instance of these patterns, whether it runs in n8n Code
nodes, a service, or a broker.

## When to use

- Two systems use different field names, units, or encodings for the same fact.
- A consumer needs extra context it cannot obtain itself (lookups, enrichment).
- A payload carries internal or sensitive fields that a downstream system must
  not see.
- Many producers and consumers all talk slightly different dialects of the same
  data.

## The patterns

1. **Message Translator** — a dedicated component that converts one system's
   message format into another's. Keep each translation isolated so a schema
   change in one system touches only its translator.
2. **Canonical Data Model** — define one agreed intermediate representation for
   the whole integration; every system translates to and from the canonical
   model instead of translating pairwise. N translators instead of N squared.
3. **Envelope Wrapper** — wrap the business payload with routing/transport
   headers the payload itself should never carry.
4. **Content Enricher** — consult an external data source (database, API,
   lookup table) to add context missing from the original message.
5. **Content Filter** — strip non-essential fields before forwarding, often for
   privacy, size, or contract reasons.
6. **Claim Check** — store a large payload (file, blob) in a shared store and
   pass only a reference; the consumer retrieves it when needed.
7. **Normalizer** — accept many formats from many sources and emit one canonical
   format, routing each source's format to its matching translator.

## How to apply in n8n and services

- One Code node per distinct translator, named by the source and target shape
  (`map-legacy-order-to-canonical`, not `transform-data`).
- Keep enrichment idempotent: an enrich step re-run on an already-enriched
  message must not duplicate fields or double-apply.
- Claim Check over large binaries: store the file once (S3, a bucket, a data
  table) and pass the reference in the workflow items instead of dragging the
  binary through every node.
- Content Filter at the boundary: strip secrets and internal ids before the
  payload leaves your trust zone.
- When a message has no source system (an event you generate), build it in the
  canonical model directly instead of translating twice.

Pairs with: eip-message-routing (where the transformed message goes next),
enterprise-integration-patterns (the full catalog), api-integration,
n8n-code-nodes-official (Code-node implementation), n8n-syntax-v2-enforcer
(v2 expression discipline inside translators).
