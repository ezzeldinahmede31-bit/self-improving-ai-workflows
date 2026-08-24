---
name: llm-engineers-handbook
description: Applies Paul Iusztin & Maxime Labonne's LLM Engineer's Handbook to build end-to-end LLM systems as three pipelines (feature/training/inference): advanced RAG (pre-retrieval query optimization, retrieval upgrades, post-retrieval rerank/compression), the SFT escalation ladder (prompt engineering first, then instruction dataset, then LoRA/QLoRA), DPO preference alignment, inference optimization (quantization, batching, latency-vs-throughput), monolith-vs-microservices serving split (GPU-bound LLM service separated from CPU-bound business logic), and LLMOps CI/CD/CT with prompt+answer monitoring. Use when the user says 'LLM Engineer Handbook', 'build the full LLM system', 'advanced RAG', 'fine-tune or just prompt', 'DPO', 'serve my fine-tuned model', 'LLMOps pipeline', 'quantize and deploy', 'feature training inference pipelines'. Pairs with ai-engineering-foundation-models, n8n-rag-vector-qa, qdrant-ops, llm-deployment-optimization, mlops-production.
---

## Purpose

Turn "an LLM app" into a disciplined three-pipeline system instead of one tangled script:
1. **Feature pipeline** — collect data, chunk, embed, index (RAG feature side).
2. **Training pipeline** — instruction datasets, SFT, preference alignment, evaluation.
3. **Inference pipeline** — retrieve, rerank, prompt, serve, monitor.

The book's rule: adapt standard MLOps principles to LLM work; do not invent new shapes per project.

## Gate 1 — Escalation ladder before any fine-tuning

Order of levers, cheapest first:
1. Prompt engineering (+ few-shot) on open-weight or closed models.
2. RAG for private/fresh knowledge — bypasses retraining for new data entirely.
3. Instruction dataset + SFT only when prompting/RAG measurably miss requirements.
4. Preference alignment (DPO) only after SFT, using a real preference dataset.
Never skip building the eval harness early: accuracy, cost, latency are measured at every rung.

## Gate 2 — Advanced RAG, three stages

- **Pre-retrieval**: clean/chunk data for indexing quality; optimize the query (expansion, self-querying metadata filters).
- **Retrieval**: stronger embedding models; hybrid dense + keyword (BM25); metadata filtering.
- **Post-retrieval**: filter noise from retrieved docs; compress context before the prompt; rerank, take top-K, build the final prompt.
Book-end lesson: dense-only retrieval misses exact terms — add BM25 into the rerank stage.

## Gate 3 — Inference optimization trade-offs

Four limits shape every deployment decision: latency (network + serialization + inference), throughput (dynamic batching raises per-request latency but lifts system-wide capacity), data shape/size (context assembly and retrieval hops add network time), infrastructure (GPU sizing, disks, network). Over-optimizing latency underutilizes hardware and inflates cost/request. Quantization (4-bit QLoRA-class) makes fine-tuned models servable on modest hardware.

## Gate 4 — Serving architecture split

Monolith (preprocess + model + postprocess in one deployable) ships fastest and suits CPU-only/small models. Once GPUs enter: split the GPU-bound LLM service from CPU/IO-bound business+RAG logic so each scales independently with the right runtime. Add autoscaling for spikes.

## Gate 5 — LLMOps loop

CI tests code integrity; CD automates deployment; CT automates retraining; a monitoring pipeline logs every prompt and generated answer. Model registry + experiment tracker + orchestrator are the backbone tools.

## Output contract

Report per build: which rung of Gate 1 was justified, the three RAG stages applied, the latency/throughput posture chosen, monolith-vs-microservices verdict with reason, and which LLMOps loops exist. Never deliver a fine-tuning plan without the cheaper-lever justification.
