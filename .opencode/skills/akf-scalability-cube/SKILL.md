---
name: akf-scalability-cube
description: "Scales systems along three axes: clone, split, and partition. Use when the user says 'scale the system', 'AKF cube', 'X axis Y axis Z axis', 'sharding', 'microservices split', 'scale cube', or when growth must not mean rewrite."
---

# AKF Scalability Cube

Distilled from Abbott & Fisher *The Art of Scalability*: scale along three
independent axes — X (clone), Y (split by function/service), Z (split by
data/shard). Every scaling move is a point in this cube; name the axis or
argue about nothing.

## Purpose

Grow capacity without redesign: pick the axis (or combination) that attacks
the actual bottleneck, in the cheapest order.

## The three axes (apply X, then Y-or-Z by bottleneck)

1. **X axis: horizontal duplication.** Clone identical instances behind load
   balancing; no code changes, near-linear gains while stateless. First move
   always: terminate SSL at the edge, cache aggressively, replicate reads.
   Ceiling: shared state (sessions, single DB) — the bottleneck moves, it
   does not vanish.
2. **Y axis: split by service/function.** Decompose along business
   capabilities (verbs, resources, data domains): separate deploy/scale per
   service. Pays when different functions have different load profiles or
   teams step on each other. Costs: distributed transactions, observability
   burden, network failure modes — adopt with the distributed-systems
   toolkit loaded.
3. **Z axis: split by data (sharding).** Partition by key (customer, region,
   time): each shard independent. Pays for data-volume bottlenecks.
   Demands: shard-key discipline (hot keys kill), rebalancing story,
   cross-shard queries minimized by design (denormalize deliberately).

## Rules of the cube

- Bottleneck-first: measure (CPU? memory? I/O? lock contention? data
  volume? team contention?) then move on the axis that relieves IT.
- Statelessness enables X; bounded contexts enable Y; shard keys enable Z —
  each axis has an architectural prerequisite; build it before you need it.
- Scale reads and writes separately (replicas/CQRS for reads, partitioning
  for writes). Conflating them wastes the move.
- Cost awareness: each axis trades simplicity for capacity — revisit whether
  the cheaper axis still has headroom before paying the complex one.

## Verification

Scaling plan ships with: bottleneck evidence, axis choice + order, the
prerequisite built (statelessness/contexts/shard keys), and the NEXT
bottleneck predicted (scaling moves the wall — name where it lands).

## Pairs with

- `microservices-boundary-design` (Y-axis splits),
  `ddia-replication-partitioning` (Z-axis mechanics),
  `alex-xu-system-design` (bottleneck estimation),
  `systems-performance-profiling` (finding the bottleneck).
