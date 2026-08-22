---
name: dead-letter-error-routes
description: "Routes failures to inspectable dead-letter stores with payload, reason, context. Use for batch/error handling."
---

# Dead-Letter and Error Routes

Failures are data — preserve them as a work queue.

## Workflow
1. Attach error output to every network node -> common sink.
2. Enrich record: payload, error, timestamp, run IDs, attempt history.
3. Continue past poison items in batches.
4. Build replay path through normal pipeline.

## Core Rules
- Alert on growth rate.

## Pairs with
- `n8n-error-boundary-architect`, `observability-execution-monitoring`, `enterprise-integration-patterns`
