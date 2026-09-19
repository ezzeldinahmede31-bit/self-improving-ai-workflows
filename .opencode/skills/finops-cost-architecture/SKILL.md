---
name: finops-cost-architecture
description: "Design with the price tag on: unit economics, cloud cost trade-offs, cost fitness functions. Use when the user says 'cloud bill too high', 'cost optimization', 'FinOps', 'تكلفة السحابة', 'unit economics', 'cost per request', or needs architecture where cost is a first-class characteristic."
---

# FinOps Cost Architecture

Distilled from Storment & Fuller *Cloud FinOps*, *Architecting for
Scale* economics, AWS/Azure cost-architecture lenses, *Software
Architecture: The Hard Parts* cost dimension. Cost is an architecture
characteristic — specify it, measure it, govern it.

## The protocol

1. **Unit economics first.** Cost per 1K requests, per GB stored, per
   active user. Every design compares options in these units, not in
   monthly totals nobody can attribute.
2. **Tag to attribute.** Cost without allocation tags is trivia. Every
   resource carries service/env/owner before it ships; untagged spend
   gets a budget of zero attention and full accountability.
3. **Trade-offs with price tags.** Serverless vs containers vs VMs,
   managed vs self-hosted, multi-AZ vs multi-region, retention windows,
   log verbosity — each with $/unit attached. Pairs with
   `tradeoff-analysis` and `architecture-decision-framework`.
4. **Elasticity discipline.** Scale-to-zero where idle, autoscale on
   the right signal (queue depth, not CPU), kill zombies on schedule
   (unattached disks, idle LBs, old snapshots, over-provisioned DBs).
5. **Cost fitness functions.** Automated guards: per-deploy cost delta,
   per-service budget burn alerts, anomaly detection on daily spend.
   Pairs with `fitness-function-engineering`.
6. **Showback rhythm.** Monthly per-service cost review with owners.
   Engineers optimize what they see — invisible cost grows 20-30%/yr
   on its own.

## Verification

Cost design ships with: unit economics per option, allocation tags,
priced trade-off matrix, autoscale signals, cost fitness functions,
showback owner + cadence. A design without $/unit is incomplete.

## Pairs with

- `production-capacity-planning` (capacity math),
  `tradeoff-analysis` (priced matrix),
  `architecture-decision-framework` (record cost decisions),
  `fitness-function-engineering` (cost guards),
  `system-design-production-blueprint` (phase 7).
