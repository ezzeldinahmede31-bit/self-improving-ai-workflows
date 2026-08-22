---
name: fan-out-fan-in-merge
description: "Splits work parallel then rejoins by key, handling partial failures. Use for parallel branches."
---

# Fan-Out / Fan-In Merge

Parallelism speeds but merge points bite.

## Workflow
1. Identify parallel segment + join point.
2. Correlation key carried through every branch.
3. Merge waits for all or explicit partial policy.
4. Test one branch failing.

## Core Rules
- Correlate by key, never arrival order.

## Pairs with
- `eip-message-routing`, `n8n-subworkflow-modularizer`, `cloud-native-patterns`
