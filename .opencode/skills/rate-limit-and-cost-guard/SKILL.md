---
name: rate-limit-and-cost-guard
description: "Calculate expected API cost and call volume for every n8n workflow, then add rate-control (Wait/Loop limits) so API keys are not banned and budgets are not blown. Use when building workflows that call external LLMs, paid APIs, Telegram, or any rate-limited service."
---

# Rate Limit & Cost Guard

Prevents API-key bans and runaway spend before they happen.

## Step 1 — Cost & calls estimation (do before building the loop)
For each paid/rate-limited node, estimate:
- `calls_estimate = items_in × loops_per_item (+ retries)`
- `cost_per_call` for LLMs: `~tokens_in/1k × $/1k + ~tokens_out/1k × $/1k`
- `total_budget = Σ costs`; if > user's stated budget → propose reducing limit,
  chunking, or using a cheaper model.

## Step 2 — Rate limiting (always)
- **LLM / OpenAI-compatible**: batch items and cap concurrency ≤ 10; add
  `Wait` node (or `retryOptions`) ~1s between batches; honor `429` with backoff.
- **Telegram**: 1 message/sec per chat (rooms) / 20 msg/min; add spacing Wait nodes.
- **Scrapers / Overpass**: respect their global throttle; add Wait ≥ 2s between calls.
- **Loop nodes**: always set a hard `maxIterations` (e.g., ≤ 20) with a break condition.

## Step 3 — Explicitness in the workflow
- Add a `Wait` node after any rate-limited node, delay configurable via expression.
- Annotate cost estimate as a node Note so the user sees expected spend.
- For unknown budgets: default conservative (e.g., limit=50, concurrency=3).

## Guard regex (mentally enforce)
- Any `for`/`while` loop that hits the network → must carry a counter + max.
- Any LLM node → verify `options.maxTokens` set and item cap present.
- Any HTTP node → `retryOnFail` bounded; `requestOptions.timeout` set.

## Cost report (include in every delivery)
```
Estimated calls : N
Estimated tokens: N in / N out
Estimated $    : $X  (at configured pricing)
Limit enforced : ≤ L items, concurrency C, maxRetries R
```
## Acceptance
- [ ] No unbounded loop can hit a live API.
- [ ] Backoff respected on 429.
- [ ] Budget estimate shared with user before heavy runs.
- [ ] Telegram/comms throttled to platform limits.