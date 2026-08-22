---
name: distributed-training-foundation-models-v2
description: "Applies Distributed Training of Foundation Models: Frameworks and Hardware Optimization to production: distilled patterns, anti-patterns, and checklists for building reliable distributed training of foundation models: frameworks and hardware optimization that survive real load, partial failure, and human review. Use when the user says 'distributed training of foundation models: frameworks and hardware optimization' or asks about the capability behind this book. Pairs with automation-known-iss..."
---

# Distributed Training of Foundation Models: Frameworks and Hardware Optimization — Skill 763

Operational distillation of **Distributed Training of Foundation Models: Frameworks and Hardware Optimization** (Book 763) for immediate use in n8n, Python, and autonomous agent stacks. No theory for theory sake — every section maps to a shippable check.

## Core idea

Distributed Training of Foundation Models: Frameworks and Hardware Optimization succeeds when the system behaves correctly under load, failure, and change. This skill encodes that as guardrails.

## When to use

- The user mentions "distributed training of foundation models: frameworks and hardware optimization" or the domain "LLMOps/Training".
- Building, reviewing, or hardening anything in this domain.
- Debugging a failure that matches the patterns below.

## Patterns (use these)

- Define interface first, keep modules narrow, isolate side effects.
- Prefer idempotent, retryable, observable units over fragile chains.
- Validate inputs at the boundary, handle errors loudly, log with correlation IDs.

## Anti-patterns (avoid)

- God workflows that mix trigger, transform, notify, and persist in one canvas.
- Silent failure, missing retry, or unbound loops/cost.
- Secrets inline, placeholder credentials, unauthenticated write endpoints.

## Minimal checklist

- [ ] Trigger + auth + error path exist and are tested
- [ ] Credentials via n8n store, never in code
- [ ] Pinned data present for instant replay
- [ ] Rate/cost ceiling declared, backoff defined
- [ ] Observable: logs, metrics, and trace ID emitted

## n8n / code hint

Wire this domain as a sub-workflow with a verb-first name (`distributed-training-foundation-models-v2`), one responsibility per node, and an `Execute Workflow` edge from the parent. Keep config in env/credentials, not in expressions.

## Verification

Run `venv/bin/python scripts/build_gates_pipeline.py <artifact> --schema-cache memory/n8n_schema_cache.json` — expect `READY_FOR_DEPLOYMENT`. For RAG/vector paths, also confirm collection wiring and embedding `input_type`.
