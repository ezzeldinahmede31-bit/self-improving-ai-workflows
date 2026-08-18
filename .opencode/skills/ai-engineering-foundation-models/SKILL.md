---
name: ai-engineering-foundation-models
description: Applies Chip Huyen's AI Engineering to design production systems around foundation models and LLMs — when to use an LLM at all, prompting and context engineering, retrieval-augmented generation (RAG), agentic tool use, structured output, evaluation of LLM applications, and the cost/latency/quality trade-offs of model choice, fine-tuning, and deployment. Covers the full lifecycle from prototyping a prompt to serving a dependable, observable LLM feature. Use when the user says 'AI engineering', 'build an LLM feature', 'RAG pipeline', 'prompt engineering', 'structured output', 'LLM evaluation', 'eval set', 'model choice', 'fine-tune vs prompt', 'cost per request', 'latency budget', 'Chip Huyen', 'agent tool use', 'guardrails', or when designing a production application that calls foundation models. Pairs with: n8n-rag-vector-qa, designing-machine-learning-systems, nlp-transformers-huggingface, prompt-engineering-llm-apps, evaluation, litellm-tier-router.
---

# AI Engineering with Foundation Models

Transfers Chip Huyen's AI Engineering discipline onto production LLM systems: treat the model as a component with a cost/latency/quality contract, evaluate relentlessly, and add retrieval, tools, and guardrails only when they measurably help.

## When to use
- Designing any production feature that calls an LLM or foundation model.
- Choosing between prompting, retrieval, fine-tuning, or a smaller task-specific model.
- Building an evaluation harness for an LLM application.

## The engineering workflow
1. Decide if an LLM is the right primitive; a rules or lookup solution may win on cost and determinism.
2. Prototype with prompting and context engineering; measure quality before adding machinery.
3. Add retrieval (RAG) when knowledge must be current or domain-specific; add tools when the model must act.
4. Force structured output whenever downstream code parses the response.
5. Define an eval set from real user inputs before tuning anything.

## Cost, latency, quality
- Model choice is a three-way trade-off; profile a realistic batch of requests, not one.
- Context length raises cost and latency; retrieve only what the task needs.
- Fine-tuning buys reliability on a narrow, well-labeled task; prompting wins when the task is broad or changing.

## Verification discipline
- Keep a regression eval set and run it after every prompt, retrieval, or model change.
- Track cost and latency per request alongside accuracy; a small accuracy gain that doubles cost is a real loss.
- Monitor drift: model behavior, upstream data, and user input change over time.

## Pairs with
n8n-rag-vector-qa, designing-machine-learning-systems, nlp-transformers-huggingface, prompt-engineering-llm-apps, evaluation, litellm-tier-router.