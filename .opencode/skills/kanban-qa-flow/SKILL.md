---
name: kanban-qa-flow
description: "Kanban QA flow distilled. Use when managing test WIP, pull policies, classes of service, flow metrics, bottlenecks in QA columns."
---

# Kanban QA Flow

## Purpose

Keep quality flowing in Kanban: explicit WIP limits on test columns, pull policies, expedite handling, flow metrics driving improvement.

## When to use

Use when the user says 'Kanban QA', 'WIP limit', 'pull policy', 'flow metrics', 'bottleneck QA', 'classes of service'.

## Steps

1. Visualize test stages as explicit columns with WIP limits.
2. Define pull policies per column (what ready means downstream).
3. Give defects an expedite lane with strict entry rules.
4. Track flow time plus throughput plus aging work daily.
5. Attack the bottleneck column first when flow stalls.

## Anti-patterns

- Unlimited WIP hiding a test bottleneck.
- Push behavior flooding testers regardless of capacity.
- Expedite lane used for everything urgent.
- Metrics collected but never changing policy.

## Example

Policy card: "Test column WIP 3; pull only stories with green contract suite."

## Verification

WIP limited, policies posted, expedite disciplined, flow metrics improving.

## Pairs-with

scrum-qa-integration, value-stream-mapping, the-goal-constraints, quality-metrics-dashboard.
