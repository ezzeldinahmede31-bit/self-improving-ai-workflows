---
name: llm-rails-validators-adapter
description: "LLM rails and validators adapter (NeMo input/output/retrieval rails, Guardrails AI validators, PII/jailbreak/topical controls). Use when an LLM call needs input/output guarding, structured-output guarantees, PII redaction on retrieval, jailbreak/topical rails for chat, or a validator-hub pattern without new infra. Trigger phrases: 'add rails', 'validate LLM output', 'PII rail', 'jailbreak rail', 'ضوابط لمخرجات النموذج'."
---

# LLM Rails + Validators Adapter (Two Layers, One Call Path)

Adapter over **NVIDIA NeMo Guardrails** (Colang dialogue/topical/
jailbreak/fact rails, input→retrieval→dialog→execution→output stages,
Apache 2.0) and **Guardrails AI** (50+ Hub validators, RAIL/Pydantic
schemas, re-ask/auto-fix on failure, Apache 2.0). Industry split: NeMo
owns the conversational layer, Guardrails AI owns the structured-output
layer — run both when both failure classes exist.

## When to use

- Single LLM calls needing guarantees: schema enforcement, PII/
  toxicity checks, re-ask-or-fix instead of fail.
- Chatbots/agents needing flow control: topical rails (refuse
  off-scope), jailbreak rails, fact-check rails on retrieval.
- RAG outputs: retrieval rail (sensitive-data check on chunks) +
  output validators (grounding/shape) before delivery.

## Steps

1. Output layer first (cheapest): Pydantic/RAIL schema + validators
   (PII, toxicity, restrict-to-topic, format); parallel independent
   validators; on failure re-ask or fix, then fail closed.
2. Conversational layer where needed: Colang topical + safety +
   jailbreak rails; input rails run before the app model, output rails
   after; retrieval rails guard RAG chunks.
3. Custom policy as Python actions/validators (org-specific rules the
   catalog lacks); lightest control that satisfies the evidence bar.
4. Pin versions (library + config + prompts + guard models) together;
   re-run regression + adversarial evals before promotion; staged
   rollout with rollback.
5. Benchmark YOUR config (latency/token/error/saturation on
   representative traffic); declare fail-open vs fail-closed per rail
   explicitly — never inherit silently.
6. No prompts/responses leave your infra beyond the providers you
   configure; telemetry opt-out where available.

## Verification

- Adversarial prompt battery + regression suite green per release.
- Every rail has a named failure policy; version pins recorded.
- Telemetry/data-handling reviewed for regulated data.

## Pairs with

`guardians-formal-verification-adapter` (proof-grade checks),
`promptfoo-eval-redteam-adapter` (regression + redteam),
`build-gates-pipeline` (MATH/REASONING), `credential-secret-handling`.
