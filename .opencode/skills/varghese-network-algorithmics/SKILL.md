---
name: varghese-network-algorithmics
description: "Implements packet processing at line rate: fast lookups, classification, and scheduling. Use when the user says 'line rate', 'packet classification', 'longest prefix match', 'tries', 'TCAM', 'fair queueing implementation', 'Varghese', or when software must forward millions of packets per second."
---

# Varghese Network Algorithmics

Distilled from George Varghese *Network Algorithmics*: wire speed comes from
algorithmics, not gigahertz — 15 design principles that turn impossible
packet rates into routine implementations.

## Purpose

Build data-plane software/hardware that keeps up with the wire: lookups,
classification, and scheduling at millions of packets per second.

## The principles that pay (the load-bearing subset)

1. **Shift work in time (P1-P3).** Precompute (compile-time tables),
   lazy evaluation (do work only when needed), share work across packets
   (header prediction: the common case cached, the rare case slow-pathed).
2. **Shift work in space.** Locality (caches for flows/rules), trading
   certainty for speed (probabilistic structures: Bloom filters for
   membership, sketches for measurement — sized by the math, not hope).
3. **Relax the spec.** Bottleneck link approximation, controlled loss of
   precision where the protocol tolerates it. Exactness is a budget item.
4. **Tries for longest-prefix match.** Binary/level-compressed
   (LC-trie)/multibit tries turn routing lookups into a few memory
   accesses; TCAM when power budget allows (parallel match, expensive watts).
   Measure lookups in cache misses, not comparisons.
5. **Packet classification at scale.** Decision-tree cutting (HiCuts),
   tuple-space search, decomposition across fields. Rule-set structure
   (overlap? ranges?) picks the algorithm — profile YOUR rules, not the
   paper's.
6. **Scheduling that keeps promises.** WFQ for fairness with weights,
   deficit round robin for cheap byte-fairness, priority + policing for
   real-time. Implement the scheduler the SLA names, not the easiest one.
7. **Endsystem + measurement discipline.** Zero-copy I/O, batching (amortize
   per-packet cost), lock-free rings; measure with hardware timestamps,
   report p99/p999 (means lie at line rate).

## Implementation order

Profile the bottleneck (lookup? classify? schedule?) → apply the matching
principle → measure in misses/packets-per-core → iterate. Optimizing the
non-bottleneck is the classic failure — Varghese's whole book is aim first.

## Verification

Ships with: bottleneck profile, principle cited per optimization, line-rate
test (offered load = link rate, loss/delay bounded), and p99 numbers — not
averages. "Fast on average" at line rate means "drops under burst".

## Pairs with

- `tcp-ip-illustrated` (what the packets mean),
  `systems-performance-profiling` (measurement),
  `bpf-performance-tools` (kernel fast paths),
  `high-performance-browser-networking` (endpoint side).
