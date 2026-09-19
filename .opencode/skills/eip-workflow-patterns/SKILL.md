---
name: eip-workflow-patterns
description: "Design n8n workflows with the Enterprise Integration Patterns vocabulary (Hohpe/Woolf): content-based router, splitter, aggregator with completeness conditions, recipient list, claim check, normalizer, canonical data model, idempotent receiver, dead letter channel, control bus — each mapped to concrete n8n nodes. Use when designing any multi-step workflow, choosing If/Switch/fan-out shapes, or reviewing whether a graph uses the right pattern for its problem. Pairs with n8n-subworkflow-modularizer, live-workflow-surgery, stability-patterns-production, n8n-oom-crash-recovery."
---

# EIP Workflow Patterns (n8n mapping)

The world's integration architects share one vocabulary — 65 patterns from
"Enterprise Integration Patterns" (Hohpe/Woolf). This skill maps the routing
and transformation core onto n8n nodes so every design decision names its
pattern instead of improvising shapes.

## Source (adopted baseline)

enterpriseintegrationpatterns.com (canonical site + Ch. 3 PDF): patterns are
technology-independent, harvested from proven solutions; async messaging
acknowledges latency and partial failure. A router that knows every
destination becomes a maintenance bottleneck — prefer explicit routing tables
over clever hidden logic.

## Routing patterns → n8n

- Pipes and Filters → linear node chains; each node one job, explicit items
  in/out. Default shape; deviate deliberately.
- Content-Based Router → If/Switch on message content (field values,
  existence). Keep the routing function in ONE maintainable place; when rule
  volume grows, graduate to a rules table (Set/Code lookup) not nested Ifs.
- Message Filter → If-gate discarding invalid payloads EARLY (see shed load).
- Recipient List → one message to many lanes (multi-output If, parallel
  branches, executeWorkflow fan-out). Unlike pub-sub, the sender controls the
  list — audit it.
- Splitter → Split In Batches / Split Out: one composite message into per-item
  messages for individual processing.
- Aggregator → Code node collecting correlated messages (correlation id
  REQUIRED) until a completeness condition, then publishing one distilled
  message. Conditions: wait-for-all (needs known total + timeout + missing
  policy), timeout window, first-best, external event. STATEFUL — persist
  partial state in Redis/staticData or a crash loses the aggregate.
- Resequencer → Sort node restoring order after parallel processing.
- Scatter-Gather → parallel branches gathering competitors/alternatives +
  Merge/Aggregator selecting (first, best scored, all).

## Transformation patterns → n8n

- Message Translator → Code/Set mapping external shapes to internal ones.
- Content Enricher (add) vs Content Filter (strip): enrich late, strip EARLY
  (memory diet — a 150-field object through 20 nodes is the OOM antipattern).
- Claim Check → store the heavy payload in Redis/DB, pass only the key
  downstream; retrieve at the node that needs it. The memory-footprint fix.
- Normalizer → ONE Set node at ingress forcing every source into the same
  shape before routing diverges.
- Canonical Data Model → one internal schema every workflow in the fleet
  speaks; translators live at the edges, never in the middle.

## Reliability patterns → n8n

- Idempotent Receiver → dedup-key check (Redis SET NX EX window) BEFORE any
  side effect; duplicates short-circuit with the original response.
- Dead Letter Channel → Error Trigger workflow + dead-letter store (payload,
  reason, source) for inspection and replay — never silent drops.
- Control Bus → settings flags / Redis keys steering behavior without edits
  (feature flags, SAFE_MODE, lane toggles). Separate deployment from release.
- Competing Consumers → queue mode workers draining one queue; add consumers
  to scale, not bigger single runs.

## Choosing (decision order)

Single path → Pipes and Filters. Branch on content → Content-Based Router.
One-to-many items → Splitter (+ Aggregator iff recombination needed, with a
named completeness condition). Many destinations, sender-controlled →
Recipient List. Heavy payload, many hops → Claim Check. Untrusted/duplicate
delivery → Idempotent Receiver + Dead Letter Channel. Runtime steering →
Control Bus. If none fits, say so — forcing a pattern is worse than none.

## Verification

Every graph names its patterns in sticky notes; Aggregator states its
completeness condition; stateful nodes name their store; router rules live in
one place. Review with world-class-design-review.
