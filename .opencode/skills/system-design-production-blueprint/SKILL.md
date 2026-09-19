---
name: system-design-production-blueprint
description: "Master production system-design protocol: requirements, estimation math, API/data contracts, component design, failure modes, capacity, cost, ADR. Use when the user says 'صمم سيستم', 'design the system', 'system design', 'architecture from scratch', 'production architecture', 'how should we build this', or needs a complete defensible backend design, not an interview sketch."
---

# System Design Production Blueprint

Distilled from the books that make a designer expert — Alex Xu *System Design
Interview* (estimation + building blocks), Kleppmann *Designing
Data-Intensive Applications* (replication, partitioning, consistency),
Abbott & Fisher *The Art of Scalability* (AKF cube), Google *SRE*
(SLOs, capacity, failure budgets), Richardson *Microservices Patterns*,
Newman *Monolith to Microservices*, Ford/Richards *Software Architecture:
The Hard Parts* (trade-offs with numbers). Interview skills sketch;
this skill SHIPS.

## Purpose

Turn "we need a system that does X at scale Y" into a complete,
reviewable production design: quantified requirements, estimation page,
API + data contracts, component diagram, bottleneck deep-dive, failure
story, capacity plan, cost sanity, ADRs. A design without numbers,
contracts, and a failure story is a drawing.

## The protocol (never reorder — each phase feeds the next)

1. **Requirements with numbers.** Functional (reads/writes, entities,
   operations) + non-functional quantified: DAU/peak QPS, p50/p99
   latency budgets, durability/availability targets (nines), consistency
   lean (per-operation, not per-system), retention, geography, budget.
   Output: requirements table. Design answers THIS table.
2. **Back-of-envelope estimation.** QPS avg/peak, storage (bytes x
   retention x replication factor), bandwidth in/out, working-set vs
   cache memory, per-request CPU x QPS. Powers of ten, stated
   assumptions, one page. The estimate picks the architecture.
3. **API + data contracts.** Endpoints with shapes/status codes,
   event schemas with versioning, DB schema with access patterns
   (queries first, tables second), cache keys + TTLs, queue topics.
   Contracts before components — components serve contracts.
4. **High-level blocks.** Gateway -> services -> storage -> cache ->
   queue -> CDN with data flow. Boring proven blocks first; novelty
   needs a written reason. Classify with `systems-design-methodology`;
   pick primitives from `architecture-primitives`.
5. **Bottleneck deep-dive.** From the estimate: the ONE component that
   breaks first gets the effort — sharding key + hot-key story, cache
   policy + stampede guard, queue sizing + DLQ, DB choice with
   read/write math. Name the AKF axis (`akf-scalability-cube`) and the
   DDIA mechanism (`ddia-replication-partitioning`).
6. **Failure + SLO story.** What breaks, what degrades, what pages.
   Per-dependency: timeout/retry/circuit-breaker/bulkhead. SLOs per
   user-visible operation, error budget, on-call consequence.
   Zero single points without a written acceptance.
7. **Capacity + cost sanity.** Machines/shards/replicas from phase 2
   numbers, headroom %, growth path (where the NEXT bottleneck lands),
   per-user infra cost inside budget. If cost kills it, redesign now.
8. **Decide + record.** Every contested choice becomes an ADR
   (`architecture-decision-framework`): options, trade-off matrix with
   numbers, decision, reversible-or-not. Then self-review with
   `architecture-review` + `systems-design-review-methodology` before
   calling it done.

## Estimation cheat sheet (memorize the anchors)

- 1M DAU ~ 12 QPS avg, ~120 QPS peak (10x). 1KB x 10M writes/day x
  3 replicas x 365d ~ 11TB/yr. 1 req = 100KB at 1K QPS = 100MB/s.
- Latency budget split: edge 20ms, service 50ms, DB 10ms, cache 2ms —
  spend it on paper before spending it in prod.
- Cache hit 95% turns 10K DB QPS into 500. Queue depth = peak minus
  capacity times duration — size it, don't hope it.

## Verification

Design ships with: requirements table, estimation page, API/data
contracts, block diagram, bottleneck deep-dive with numbers, failure +
SLO story, capacity + cost page, ADRs, adversarial self-review notes.
Missing any one = PARTIAL, say which.

## Pairs with

- `alex-xu-system-design` (interview-depth blocks), `akf-scalability-cube`
  (growth axes), `ddia-replication-partitioning` (storage mechanics),
  `systems-design-methodology` (phase governance),
  `systems-design-review-methodology` + `architecture-review` (review),
  `architecture-primitives` (pattern catalog), `tradeoff-analysis`
  (quantified trade-offs), `system-type-distributed` /
  `system-type-event-driven` (domain patterns),
  `architecture-decision-framework` (ADRs), `software-architecture-design`
  (runtime/platform topology), `python-backend-architecture-review`
  (Python backend lens), `sre-workbook-practices` (SLO/error budgets),
  `proactive-spec-expander` (edge-case expansion),
  `tradeoff-and-postmortem-documenter` (record decisions).
