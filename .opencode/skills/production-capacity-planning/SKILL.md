---
name: production-capacity-planning
description: "Size production with math, not hope: demand curves, Little law, headroom, load tests. Use when the user says 'server sizing', 'capacity planning', 'السعة', 'headroom', 'load test plan', 'Little law', 'forecast traffic', or needs machine/shard/replica counts with evidence."
---

# Production Capacity Planning

Distilled from Menasce & Almeida *Capacity Planning for Web Services*,
Allspaw *Art of Capacity Planning*, McConnell *Software Estimation*,
Gram-Vaccarino queueing practice, AKF headroom rules. Capacity is a
model plus a measurement, never a guess.

## The protocol

1. **Demand model.** Users -> sessions -> requests: DAU, peak-to-avg
   ratio (measure, never assume 1), growth rate, seasonality. Output:
   peak QPS per endpoint with a date on it.
2. **Service model.** Per-request cost: CPU ms, memory bytes, downstream
   calls, bytes in/out. Measure on prod-shaped data, not laptops.
   Capacity per box = 1 / (costliest resource per request).
3. **Queueing check.** Little's law (concurrency = throughput x
   latency) sizes pools, threads, connections. Utilization target
   60-70%: past 80% latency explodes before throughput does. Pairs
   with `queueing-theory-performance`.
4. **Headroom + N+1.** Plan for one failure domain down AND one deploy
   in flight. Headroom % is a policy (growth + failure + deploy),
   written and reviewed, not vibes.
5. **Storage forecast.** Bytes x retention x replication x growth,
   plus compaction/index overhead (20-30% for LSM, 15% for B-tree).
   Disk-full is the most embarrassing outage — forecast it quarterly.
6. **Load-test the claim.** Test the stage you run, with prod-shaped
   traffic mix, until the knee (latency inflection) is found. Ship the
   graph, not the assertion.

## Estimation anchors

- 1M DAU ~ 12 QPS avg / ~120 peak. 1KB x 10M writes/day x 3 x 365d
  ~ 11TB/yr. p99 budget: split edge/service/DB/cache on paper first.
  Cost per 1K requests is the unit everything else divides by.

## Verification

Plan ships with: demand model + date, per-request costs measured,
Little's-law pool sizes, headroom policy, N+1 math, storage forecast,
load-test graph to the knee. Missing measurement = PARTIAL.

## Pairs with

- `system-design-production-blueprint` (phase 7),
  `queueing-theory-performance` (queueing math),
  `akf-scalability-cube` (growth axes), `finops-cost-architecture`
  (cost per request), `sre-workbook-practices` (SLOs under load),
  `alex-xu-system-design` (back-of-envelope).
