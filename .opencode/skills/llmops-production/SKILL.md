---
name: llmops-production
description: "Applies LLMOps practices (LLMOps: Managing Large Language Models in Production) to operating LLM features at scale: prompt and model versioning, evals in CI, cost and latency budgets, drift detection, guardrails, and rollback. Covers observability, shadow and canary rollout, and incident runbooks. Use when the user says 'operate my LLM feature', 'LLMOps', 'model versioning', 'prompt drift', 'LLM cost control', or 'rollback the model'."
---
# llmops-production

Production LLM features fail silently before they break loudly: prompts rot, costs creep, outputs drift, and safety regressions hide behind a passing happy path. This skill encodes the operating discipline that keeps a shipped LLM feature healthy — version everything, evaluate every change, watch cost and latency budgets, and revert fast.

## Core principles
- Treat prompts as code: store them in a repo, review changes, and tag each prompt-model pairing with a version.
- An LLM feature is only as good as its eval suite; gate every prompt, model, and temperature change through offline evals before rollout.
- Cost and latency are product constraints, not afterthoughts; meter them per feature and per user.
- Drift is expected. Watch input distribution, refusal rate, output schema validity, and user feedback.
- Every rollout has a rollback: keep the previous prompt-model version warm and a kill switch ready.
- Log the inputs, outputs, token usage, latency, and verdicts for every call so incidents are debuggable.

## Key patterns
- Prompt-model registry: one artifact per (prompt template, model id, temperature, tools), hash-identified.
- Shadow mode: run the candidate prompt in parallel on production traffic, compare verdicts, promote only on measured improvement.
- Canary release: serve the new version to a small slice of traffic, watch error and eval metrics, then widen.
- Guardrail sandwich: validate input before the model call and output after, so a single bad generation cannot leak to the user.
- Budget guard: per-feature token and spend ceilings that trigger fallback to a cheaper model or a cached answer.

## Applying this to n8n/Python automation
- Store prompt templates in a JSON or DB node that workflows fetch, so a prompt change is a data change, not a redeploy.
- Add an eval node after any LLM call that scores outputs against expected schemas and logs PASS or FAIL into a table.
- Wire litellm-tier-router for fallback when the primary model hits rate limits or cost ceilings.
- Use an HTTP Request node with the n8n executions API to pull failing runs into the same incident dashboard as the workflow errors.
- Log per-execution token cost from the model response usage field into an SQLite or data table for monthly budgets.

## Hard rules
- Never deploy a prompt or model change without an eval run that proves no regression on the frozen eval set.
- Never mute an eval failure; escalate to the human owner or revert the change.
- Never store prompts or evals only in the n8n UI; the repo is the source of truth.
- Never run a model upgrade without a shadow comparison on real traffic.
- Never ship a feature with a cost ceiling absent from the design.

## Pairs with
litellm-tier-router, evaluation, prompt-engineering-llm-apps, ai-engineering-foundation-models, n8n-rag-vector-qa, build-gates-pipeline
