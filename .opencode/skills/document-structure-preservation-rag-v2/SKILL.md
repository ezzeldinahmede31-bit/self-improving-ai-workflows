---
name: document-structure-preservation-rag-v2
description: "Applies Document Structure Preservation during Parsing for RAG Pipelines to production: distilled patterns, anti-patterns, and checklists for building reliable document structure preservation during parsing for rag pipelines that survive real load, partial failure, and human review. Use when the user says 'document structure preservation during parsing for rag pipelines' or asks about the capability behind this book. Pairs with automation-known-issues-compass, build-gates-pipeline, gate-first..."
---

# Document Structure Preservation during Parsing for RAG Pipelines — Skill 800

Operational distillation of **Document Structure Preservation during Parsing for RAG Pipelines** (Book 800) for immediate use in n8n, Python, and autonomous agent stacks. No theory for theory sake — every section maps to a shippable check.

## Core idea

Document Structure Preservation during Parsing for RAG Pipelines succeeds when the system behaves correctly under load, failure, and change. This skill encodes that as guardrails.

## When to use

- The user mentions "document structure preservation during parsing for rag pipelines" or the domain "Vector/DocStructure".
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

Wire this domain as a sub-workflow with a verb-first name (`document-structure-preservation-rag-v2`), one responsibility per node, and an `Execute Workflow` edge from the parent. Keep config in env/credentials, not in expressions.

## Verification

Run `venv/bin/python scripts/build_gates_pipeline.py <artifact> --schema-cache memory/n8n_schema_cache.json` — expect `READY_FOR_DEPLOYMENT`. For RAG/vector paths, also confirm collection wiring and embedding `input_type`.
