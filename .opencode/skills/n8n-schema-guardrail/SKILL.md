---
name: n8n-schema-guardrail
description: "Verify generated n8n workflow JSON against the actual installed node schemas before deploy. Use ONLY after generating or editing workflow JSON, to check node type names, typeVersion numbers, and parameter keys against the live n8n node registry via the n8n MCP (get_node / validate_node / validate_workflow)."
---

# n8n Schema Guardrail

Purpose: catch invalid node types, wrong `typeVersion`, and misspelled parameter
keys BEFORE the workflow is deployed, so the canvas never shows red nodes.

## Mandatory verification flow (before ANY deploy)
1. For each node type in the workflow, call `get_node` on the n8n MCP with
   `nodeType: "n8n-nodes-base.<type>"` and confirm:
   - The type string matches exactly (case-sensitive).
   - The `typeVersion` used is a valid, existing version (use `versions`/`compare` if unsure).
   - Required parameters exist in the schema.
2. For complex/optional params, run `validate_node` with the intended config; fix
   anything returned as error, review warnings.
3. Before creating/updating the workflow, run `validate_workflow` on the full JSON.
4. Only create/update after validation returns no errors (warnings may be acceptable but must be justified).

## Rules
- Never invent a node type that doesn't exist; always `search_nodes` or `get_node` first.
- Never bump `typeVersion` speculatively — use the version confirmed by the schema call.
- Parameter keys must match schema exactly (camelCase as in `get_node` output),
  never random renamed keys.
- Type assertions: if a schema lists a field as string but you generated an array,
  fix the type before deploy.
- For community nodes, verify the package is installed in THIS instance (via list
  of installed nodes) before referencing it.

## Failure modes to catch
- `n8n-nodes-base.http-request` vs correct `n8n-nodes-base.httpRequest` (wrong casing/dash).
- Using `operation: "create"` on a node whose schema says `"create"` under a resource
  object — confirm nesting: `resource` then `operation`.
- Referencing a field name in an expression that the schema doesn't produce.

## Output contract
After validation, report per node:
- type + typeVersion confirmed? yes/no
- required params present? yes/no
- validation errors = 0 (required before create/update)