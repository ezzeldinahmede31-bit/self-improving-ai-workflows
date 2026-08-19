---
name: generative-ai-design-patterns
description: "Applies Generative AI Design Patterns for cloud AI engineering to architect production generative systems: the request-response pattern, caching and deduplication, guardrails, chunking, and prompt versioning in the cloud. Covers cost, latency, and reliability patterns that recur across every generative workload. Use when the user says 'design a generative AI system', 'cloud AI architecture', 'caching LLM calls', 'guardrails', or 'generative design pattern'."
---
# generative-ai-design-patterns

Cloud generative AI work repeats a small set of architectural patterns regardless of the model: how to take a request, call a model safely and cheaply, cache and dedupe, guard the output, and version the prompts. This skill encodes those recurring patterns so a generative feature is architected once and reused.

## Core principles
- Every generative system is a pipeline with inputs, model calls, validation, and responses; design the pipeline, not the call.
- Caching is the cheapest correctness win: identical requests should never hit the model twice.
- Deduplication prevents wasted spend on near-identical inputs and retries on the same failed generation.
- Guardrails are layers, not a single check: input filtering, output validation, and policy checks all apply.
- Prompt versioning is mandatory; a live prompt is a deployed artifact with a history.
- Model calls are unreliable; the pattern must handle timeouts, malformed output, and content policy refusals.

## Key patterns
- Request-response with validation: schema-check the input, run the model, schema-check the output, return.
- Cache-aside: lookup by normalized request hash; store the generated response with a TTL.
- Retry with backoff and jitter for transient model errors; fail fast on policy refusals.
- Chunk-then-generate for large inputs: split, process per chunk, merge, and validate the merge.
- Versioned prompt registry served to the pipeline as configuration.
- Cost metering per request so spend is attributable and can be throttled.

## Applying this to n8n/Python automation
- Implement cache-aside with the Redis or a key-value data table node keyed on the normalized prompt hash.
- Add a dedupe node before model calls so repeated webhook payloads skip the expensive step.
- Wire an IF node for model failure branches: retry path, fallback model path, and human-review path.
- Keep prompt templates in a table or JSON config node so versioning is a data change.
- Record tokens and latency per run into an analytics table for the cost dashboard.

## Hard rules
- Never call the model for a request that the cache already answers.
- Never pass an unvalidated model output to the next system; validate the contract first.
- Never run a prompt change without versioning it and gating it through evals.
- Never design a generative feature without a budget ceiling and a fallback path.

## Pairs with
ai-engineering-foundation-models, evaluation, litellm-tier-router, designing-machine-learning-systems, n8n-workflow, build-gates-pipeline
