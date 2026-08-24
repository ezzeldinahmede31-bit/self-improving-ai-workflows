---
name: llm-workflow-production-tactics
description: Distills the production-workflow guidance of the O'Reilly LLM-stack literature that "Real-World Workflows with LLMs"-style books cover — Berryman & Ziegler's Prompt Engineering for LLMs (LLM Workflows chapter), Yan/Bischof/Frye/Husain/Liu/Shankar's emerging-LLM-stack tactics, and ML Platform Engineering production chapters — into workflow patterns for turning manual processes into reliable LLM pipelines: single-shot vs chained vs routed vs parallelized workflows, n-shot prompting discipline, chain-of-thought placement, retrieval grounding, HITL checkpoints, eval-driven iteration, version-controlled prompts, observability of multistep reasoning, guardrails and adversarial testing before production. Use when the user says 'turn this process into an LLM workflow', 'production LLM pipeline', 'workflow patterns', 'chain vs route vs parallelize', 'prompt versioning', 'HITL checkpoint', 'observability for my LLM flow', 'حول العملية دي لـ workflow بالـ AI'. Pairs with agentic-workflows, evaluation, prompt-engineering-llm-apps, build-gates-pipeline, mlops-production.
---

## Purpose

A workflow is a fixed graph of LLM steps plus code steps, designed once and run many times — unlike an agent that decides its own path. Production reliability comes from choosing the right pattern and instrumenting it, not from clever prompts.

## Gate 1 — Pattern selection ladder

Escalate complexity only when the simpler pattern measurably fails:
1. **Single-shot** — one prompt does it all.
2. **Chained** — decompose into sequential steps where later steps refine earlier ones.
3. **Routed** — classify input first, dispatch to a specialized branch per class.
4. **Parallelized** — independent subtasks run side by side, results merged.
5. **Orchestrator** — a planner assigns dynamic work (this is the agent boundary).
Every escalation adds latency, cost, and failure modes — justify each.

## Gate 2 — Prompting fundamentals inside workflows

n-shot examples aligned to expected output format (few enough to avoid over-anchoring), chain-of-thought only where reasoning genuinely helps (and kept internal), relevant resources injected via retrieval rather than hoping parametric memory suffices. Prompts live in version control with tests — they are code.

## Gate 3 — Grounding + HITL

Ground answers with retrieved documents for anything factual or fresh. Insert human checkpoints where errors are expensive or irreversible; make the checkpoint cheap (batch review, sampled audit) so it survives real volume.

## Gate 4 — Evals drive iteration

Define the eval set early; measure quality, cost, latency per change. No workflow ships a prompt/model/structure change without comparing against baseline evals. A/B thinking beats vibes.

## Gate 5 — Production hardening

Observability over every multistep reasoning chain (log inputs, outputs, intermediate states); guardrails on inputs and outputs (schema validation, safety filters); adversarial testing of the workflow itself; graceful degradation when a step fails.

## Output contract

Deliver workflows with: chosen pattern + justification from Gate 1, prompt inventory (versioned), grounding source list, HITL points marked on the graph, eval plan, and observability fields logged per step.
