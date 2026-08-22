---
name: cron-scheduling-automation
description: "Builds reliable scheduled jobs: cron expressions, timezone, overlap guards, missed-run policy. Use for timed workflows."
---

# Cron and Schedule Automation

Scheduled jobs fail quietly — timezone, overlap, missed runs.

## Workflow
1. Convert business cadence to explicit cron + timezone (e.g., Africa/Cairo).
2. Add overlap guard: lock or skip-if-running.
3. Define missed-run policy: skip / catch-up-once / alert.
4. Observe three consecutive fires, verify timestamps.

## Core Rules
- Pin timezone explicitly, never host default.
- Log intended vs actual fire time.

## Pairs with
- `trigger-design-selection`, `practice-of-cloud-system-administration`, `n8n-self-hosting`
