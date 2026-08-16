---
name: reflection-and-audit-loop
description: "Impose a mandatory 4-stage structured workflow before delivering any n8n workflow JSON or Code-node script: plan the path, draft, structural self-critique, then final export. Use when building, fixing, or refactoring n8n workflows; it forces self-review so errors are caught before the user sees output."
---

# Reflection & Audit Loop

Every n8n deliverable MUST pass 4 stages before being shown. Never skip a stage.

## Stage 1 — Plan the path (upstream → downstream)
- State the trigger, each step's purpose, the final output.
- List data flow: fields created/modified per node.
- Identify where failures can occur (API timeouts, missing fields, LLM token limits).
- Determine a sub-workflow split point (see n8n-subworkflow-modularizer) if > 6 nodes.

## Stage 2 — Draft the workflow / code
- Build nodes with confirmed schema (n8n-schema-guardrail).
- Write expressions with modern syntax (n8n-syntax-v2-enforcer).
- Add pinned data for testability (n8n-pinned-data-mocking).
- Add error handling (n8n-error-boundary-architect).

## Stage 3 — Structural self-critique (adversarial pass)
Ask, then answer honestly:
1. "Is every expression actually resolvable with real data, or only with pinned/mock?"
2. "Does every node's output shape match what the next node expects?"
3. "Are there redundant nodes or dead branches (Does Not Need to run)?"
4. "Are Webhook/Trigger paths & auth correct? Can a malformed payload break it?"
5. "Is rate limiting & cost guarded (rate-limit-and-cost-guard)?"
6. "If any node fails, does the workflow degrade gracefully or poison downstream?"
If any answer reveals a flaw → return to Stage 2 and fix, THEN re-run Stage 3.

## Stage 4 — Final export
- Validate full workflow via `validate_workflow` (schema guardrail).
- Confirm final JSON: valid array of nodes, connections object correct,
  no leftover TODO/pseudo placeholders.
- Deliver with a short "what could still fail" note so the user knows the risks.

## Anti-patterns to reject
- Shipping "first draft" without critique.
- Silently assuming upstream data while never verifying downstream field names.
- Omitting error branches because "it usually works".

## Metric
Every delivered workflow reports: nodes = N, subworkflow split = yes/no,
error branches = count, validation errors = 0.