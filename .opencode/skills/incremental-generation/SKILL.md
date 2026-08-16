---
name: incremental-generation
description: "Build n8n workflows incrementally — one node (or one small chain) at a time, validating EACH node against the live schema cache and the installed node registry BEFORE the next node is generated — instead of emitting a whole 10-15 node workflow blind and discovering schema/type errors at deploy time. Turns 'build me a workflow' into a loop of generate-one → schema-check-one → wire-one → next, so every node lands with its exact type, typeVersion and parameter keys confirmed before it is connected. Use whenever creating a workflow of more than ~3 nodes, whenever the node types or parameter shapes are uncertain, or whenever a previous attempt was rejected by SchemaPreflightGate / n8n-schema-guardrail / build-gates-pipeline with SCHEMA_PREFLIGHT_FAILED. Trigger phrases: 'ابني workflow', 'build the workflow node by node', 'incremental build', 'schema cache', 'preflight', 'validate as I build'."
---

# Incremental Generation

Purpose: eliminate the "whole-workflow blind emit" failure mode. A 15-node
workflow emitted in one shot has a high chance of containing a wrong node
type, a missing typeVersion, or a misspelled parameter key somewhere in the
middle; discovering it at deploy time wastes the whole build. This skill
builds one node at a time and checks it immediately.

## Contract: one node, one check, then wire

1. **Enumerate first** — write the node list (name + type + role) for the whole
   workflow from the confirmed contract. This is PLANNING only, not emission.
2. **Emit exactly one node** — type string, typeVersion, and every parameter
   key from the schema, never invented.
3. **Check that node now** — see the validation loop below. Fix or discard
   before proceeding. Never carry a broken node forward.
4. **Wire it** — add the connection to its upstream node only after it passes.
5. **Repeat** — next node, next check, next wire.
6. **Whole-workflow gates still run last** — incremental build does NOT skip
   `build-gates-pipeline` / `n8n-validate-workflow` on the finished JSON.

## The per-node validation loop (choose by availability, in order)

1. **Schema cache** (fastest, offline): if `memory/n8n_schema_cache.json`
   exists, check `type` is a key and every parameter key is present in the
   cached schema. Cache build: `search_nodes` / `get_node` per type from the
   n8n MCP, then save to `memory/n8n_schema_cache.json` in the shape
   `{ "<node-type>": { "required": ["param1", ...], "params": [...] } }`.
2. **Live registry** (authoritative): `n8n_get_node` with the exact
   `nodeType`, confirm type + typeVersion exist; `n8n_validate_node` with the
   intended config — fix errors, justify warnings.
3. **Run the pipeline preflight** after each node when practical:
   `venv/bin/python scripts/build_gates_pipeline.py <workflow.json> --no-hitl
   --schema-cache memory/n8n_schema_cache.json` — watch the `[PREFLIGHT]` row;
   it must be `PASS` before the node is considered good.

## Rules

- **Never emit a node without a schema check** for it. If no cache and no
  registry access is available, STOP and ask — do not guess a type or a key.
- **One node at a time** for nodes you are not 100% sure of. Well-known
  trigger/leaf nodes (webhook, httpRequest, IF, Telegram send) may be batched
  in a single small group, but still each one is checked before wiring.
- **typeVersion comes from the schema call**, never a guess; never bump it
  speculatively (n8n-schema-guardrail).
- **Parameter keys are camelCase exactly as the schema lists them.**
- If `build-gates-pipeline` returns `SCHEMA_PREFLIGHT_FAILED` or
  `DRY_RUN_EVIDENCE_MISSING`, fix that node/pinned-data BEFORE adding more
  nodes — the error-pattern DB is there to make repeats decline.
- Every check failure gets logged into the accumulated error patterns
  (Feature 5) — the next session's preflight injects "AVOID previous
  rejection" notes automatically.

## Failure modes this catches

- Wrong casing/dash in a node type (`http-request` vs `httpRequest`).
- Missing `typeVersion` or an invalid one.
- Misspelled / invented parameter key that the live schema rejects.
- A required parameter absent from an early node, propagating wrong shapes
  to every downstream node.

## Output contract

- Report per node as you go: `node X: type ✓ / typeVersion ✓ / params ✓ /
  preflight ✓`, then the wire.
- At the end: `N nodes built incrementally, M preflight-fixed on the spot,
  final build-gates verdict = <READY_FOR_DEPLOYMENT | ...>`.

## Pairs with
- `n8n-schema-guardrail` (per-node live registry checks)
- `build-gates-pipeline` (SchemaPreflightGate + DryRunGate + error patterns)
- `n8n-validation-expert`, `n8n-mcp-workflow-builder`, `n8n-error-boundary-architect`
