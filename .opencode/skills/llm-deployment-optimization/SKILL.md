---
name: llm-deployment-optimization
description: "Optimizes production LLM serving: latency budgets, token metering, prompt compression, caching, model routing, batch inference, autoscaling, and cost-per-request control for self-hosted or API models. Makes LLM features fast, cheap, and dependable under real traffic. Use when the user says 'deploy an LLM', 'reduce latency', 'token cost', 'cache the model output', 'model routing', 'batch inference', 'autoscale the endpoint', or 'optimize LLM serving'."
---
# llm-deployment-optimization

Deploying an LLM feature means more than picking a model: it means controlling latency, metering tokens, caching repeats, routing by difficulty, and scaling under load. This skill encodes the serving-side engineering that turns a working prompt into a production endpoint that is fast, cheap, and observable.

## Core principles
- Latency budget first: define the end-to-end time the feature must meet, then attribute cost per stage.
- Token metering is the unit of cost; measure input, output, cache-hit, and failure tokens separately.
- Most traffic is repetitive: caching exact and near-duplicate prompts removes a large share of cost.
- Model routing pays: cheap models handle easy calls, expensive models only hard ones, with a router.
- Batch inference raises throughput on self-hosted endpoints; latency-sensitive traffic stays unbatched.
- Every optimization must be verified with a load test, never trusted from config alone.

## Key patterns
- Router tier: classify request difficulty, then send to the smallest model that meets the quality bar.
- Semantic cache: embed the prompt, find a near-duplicate, reuse its cached answer, store the hit in metering.
- Prompt compression: drop instructions and context the task does not need before sending.
- Streaming: return tokens as they generate to hide time-to-first-token for interactive chat.
- Batch fill: coalesce independent requests on self-hosted endpoints to raise GPU utilization.
- Autoscaling: scale on queue depth and token rate, not raw request rate; prewarm before spikes.

## Applying this to n8n/Python automation
- Insert a router node that classifies incoming requests before the AI Agent node and sends easy calls to a small model.
- Add a caching step (data table or Redis) keyed on a prompt hash before calling the model.
- Meter tokens in the audit table so every workflow run reports its cost and latency.
- Set the AI Agent's maxIterations and output size so long loops cannot run away the budget.
- Run a load test against the endpoint before shipping, and monitor token rate as the autoscale signal.

## Hard rules
- Never cache a prompt that contains fresh user-specific secrets or PII without hashing and access control.
- Never route a safety-critical call to a weak model; hard rules keep the strong model path.
- Never report latency without separating network, queue, first-token, and generation time.
- Never ship an optimization that fails the load test.

## Pairs with
ai-engineering-foundation-models, litellm-tier-router, nvidia-nim-integrator, evaluation, designing-machine-learning-systems, n8n-workflow, build-gates-pipeline
