---
name: alex-xu-system-design
description: "Designs internet-scale systems interview-style: estimation, bottlenecks, and evolution. Use when the user says 'system design', 'design Twitter', 'URL shortener', 'rate limiter', 'consistent hashing', 'back-of-envelope', 'Alex Xu', or when any large system needs sizing before shaping."
---

# Alex Xu System Design

Distilled from Alex Xu's *System Design Interview* volumes: every large
system is estimation + a small set of composable building blocks, arranged
against the bottleneck, then evolved. Clarify, estimate, design, deep-dive —
in that order, every time.

## Purpose

Produce defensible large-system designs under time pressure: numbers first,
blocks second, bottlenecks third, evolution last.

## The protocol (never reorder)

1. **Clarify functional + non-functional.** Reads/writes, consistency vs
   availability lean, latency budgets, scale (DAU, peak ratios — average
   lies, peak bills). Write the requirements table; design answers it, not
   an imagined fancier problem.
2. **Back-of-envelope estimation.** Traffic (QPS avg/peak), storage (bytes ×
   retention × replication), bandwidth, memory (working set vs cache), CPU
   (per-request cost × QPS). Powers of ten, stated assumptions, one page.
   The estimate picks the architecture more often than taste does.
3. **High-level blocks.** API/gateway → services → storage → cache → queue →
   CDN: draw the five-block sketch with data flow. Choose boring proven
   blocks first (managed services over hand-rolled); novelty needs a written
   reason.
4. **Deep dive the bottleneck.** From the estimate: the one component that
   breaks first gets the design effort (sharding strategy, cache policy,
   queue sizing, DB choice with the read/write math shown). Everything else
   stays sketch-level — depth follows risk.
5. **Evolve and defend.** Single point → replicated → partitioned → cached →
   async: show the growth path. Then attack it: failures (what breaks, what
   degrades), consistency choices named (and their user-visible effects),
   cost sanity (per-user infra cost in the budget).

## The building-block cheat sheet (reach for these first)

- Consistent hashing (elastic membership, minimal reshuffle). Rate limiting
  (token bucket/leaky bucket + distributed counters). Key-value (Dynamo-style
  for scale, relational for relations — name why). Blob/object storage for
  bytes, CDN for geography. Message queues to decouple peaks from capacity.
  ID generation (Snowflake-style: time+worker+sequence, k-ordered).

## Verification

Design review: requirements table, estimation page, block diagram, bottleneck
deep-dive with numbers, evolution path, failure/cost story. A design without
numbers is a drawing.

## Pairs with

- `akf-scalability-cube` (growth axes), `rate-limit-and-cost-guard`
  (limiter math), `ddia-replication-partitioning` (storage scaling),
  `thinking-probabilistic` (peak estimation).
