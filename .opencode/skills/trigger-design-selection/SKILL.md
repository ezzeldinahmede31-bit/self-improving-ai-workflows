---
name: trigger-design-selection
description: "Picks trigger type by freshness, cost, reliability: webhook, schedule, poll, queue, manual. Use when choosing how a workflow starts."
---

# Trigger Design and Selection

Trigger decides freshness, cost, failure modes for everything downstream.

## Workflow
1. Assess freshness need vs source events.
2. Prefer push (webhook) over pull (poll) when source supports it.
3. Document payload schema and dedupe key.
4. Test duplicate delivery handling.

## Core Rules
- Push over pull when available.
- Manual triggers for testing/repair only.
- Every trigger must handle double-fire (idempotent handler).

## Pairs with
- `webhook-trigger-hardening`, `cron-scheduling-automation`, `webhook-automation`
