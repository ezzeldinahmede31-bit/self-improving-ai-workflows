---
name: litellm-tier-router
description: "Dynamic SLA-aware model routing and multi-provider failover engine. Handles OpenRouter/DeepSeek free-tier rate-limits (RPM/RPD caps), missing SLA, latency spikes, and automatic tier escalation with zero end-user error. Use whenever calls are made to a model API or LiteLLM proxy, when a 429/timeout/5xx must not reach the user, when free-tier daily quotas are near exhaustion, or when a workflow requires guaranteed uptime. Trigger phrases: 'how do I route between models', 'free tier rate limit', 'append fallbacks', 'litellm proxy config', 'avoid downtime', 'model failover'."
---

# LITELLM TIER & FAILOVER ROUTER SKILL

## DIRECTIVE

Never make single-provider API calls. Route every LLM request through a 3-Tier
fallback hierarchy managed by LiteLLM Proxy to guarantee zero downtime and
SLA compliance. A free model whose quota is exhausted or whose provider is on
fire is NOT an error — it is a routing decision.

## ROUTING & FAILOVER MATRIX

```
            [Incoming Task Request]
                        │
     ┌──────────────────┴──────────────────┐
     ▼                                     ▼
[Tier 1: Free/Routine]        [SLA Error / Rate Limit / Timeout]
 * DeepSeek V4-Flash                       │
 * Llama 3.3 70B Free                      ▼
     │                     [Tier 2: Standard Production]
     │                     - DeepSeek V4-Pro ($0.87/M)
     │                     - GLM-5.2 ($4.40/M)
     └────────────┬───────────────────────┼────────────┐
                  ▼                       ▼            ▼
      [Fallback Threshold]     [Critical/Security]  [Quota 80%]
                  │                       │            │
                  ▼                       ▼            ▼
          [Tier 3: Frontier]       [Direct Frontier]  [Local Ollama]
          - Claude Opus 4.8        - Kimi K3          (force-route)
```

## IMPLEMENTATION RULES

1. **Rate Limit Handling:** On HTTP 429 (Too Many Requests) or latency >
   4000 ms on Tier 1, failover INSTANTLY to Tier 2 without surfacing an
   end-user error. Use circuit-breaker state, not cold retries.
2. **Quota Tracker:** Track daily requests (RPD). When Tier 1 reaches 80% of
   its daily quota (e.g. 40/50), force-route all subsequent non-critical calls
   to local Ollama or Tier 2. Reserve the remaining 20% for burst/retry head.
3. **LiteLLM Config Blueprint:**
   ```yaml
   model_list:
     - model_name: routine-tier
       litellm_params:
         model: openrouter/deepseek/deepseek-v4-flash:free
         fallbacks:
           - "openrouter/meta-llama/llama-3.3-70b-instruct:free"
           - "deepseek/deepseek-chat"
         tpm: 10000
         rpm: 20
     - model_name: critical-tier
       litellm_params:
         model: anthropic/claude-3-7-sonnet
         fallbacks:
           - "moonshot/kimi-k3"
   ```
4. **SLA Error Taxonomy:** 429/timeout/5xx on Tier N ⇒ try Tier N+1; successful
   model stays sticky for the remainder of the task (session stickiness) so a
   transient blip doesn't thrash between providers.
5. **Observability:** Record per-tier success/failure, latency, and cost so the
   router learns which tier is alive right now — never assume availability from
   yesterday's health check.

## INTEGRATION

Grounds the existing `model_failover.FailoverDriver` and
`tool_gateway.LiteLLMFailover`. Replaces fixed one-shot chains with a live
3-tier hierarchy driven by measured failure + quota + latency state.

With `cognitive-task-triager`: triager decides WHICH tier class the task needs;
this router decides WHICH concrete provider answers and what to do when it
fails.

## NVIDIA Implementation (LIVE)

**`scripts/nvidia_model_router.py`** — complete implementation for NVIDIA NIM:
- Auto-discovers 82+ models from `https://integrate.api.nvidia.com/v1/models`
- 3-tier fallback: Free → Standard → Frontier
- Circuit breaker (3 failures = 60s cooldown)
- Quota tracking per tier (Free: 500/day, Standard: 200/day, Frontier: 50/day)
- 410 GONE handling: model marked permanently unhealthy
- Health checks before use
- Compatible with `model_failover.ModelLadder` via `create_nvidia_ladder()`

Usage:
```python
from scripts.nvidia_model_router import NvidiaModelRouter
router = NvidiaModelRouter()
result = router.complete([{"role": "user", "content": "Hello"}])
```

Test: `venv/bin/python scripts/nvidia_model_router.py` — discovers all models