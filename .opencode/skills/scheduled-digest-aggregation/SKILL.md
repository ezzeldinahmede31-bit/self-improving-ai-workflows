---
name: scheduled-digest-aggregation
description: "Accumulates events, delivers consolidated digests on schedule. Use to replace per-event spam."
---

# Scheduled Digest Aggregation

Per-event notifies drown; digests are read.

## Workflow
1. Classify urgent-now vs digest-worthy.
2. Accumulate durably (crash must not lose).
3. Render grouped by category with severity.
4. Suppress empty digests, respect recipient timezone.

## Core Rules
- Durable accumulation.

## Pairs with
- `notification-multi-channel-patterns`, `telegram-bot`, `cron-scheduling-automation`
