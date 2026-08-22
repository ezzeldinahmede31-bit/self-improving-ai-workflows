---
name: rate-limit-aware-consumers
description: "Respects quotas with client throttling, accounting, burst planning. Use for paid APIs."
---

# Rate-Limit-Aware Consumers

Quotas blown -> blocked pipelines.

## Workflow
1. Tabulate limits: per-window, daily caps, burst.
2. Throttle client-side below limit (token bucket).
3. Track usage, alert at 50/80/95% budget.
4. Batch/cache to shrink volume.

## Core Rules
- Never discover limits by hitting 429 in prod.

## Pairs with
- `rate-limit-and-cost-guard`, `litellm-tier-router`, `retry-backoff-jitter`
