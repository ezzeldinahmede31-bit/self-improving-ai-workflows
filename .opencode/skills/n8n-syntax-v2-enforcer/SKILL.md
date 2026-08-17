---
name: n8n-syntax-v2-enforcer
description: "Enforce modern n8n 2.x expression and Code-node syntax deterministically. Use ONLY when writing or editing n8n nodes, expressions, or Code-node JavaScript. Forces $input.item.json / $input.first().json instead of legacy $json, bans moment.js in favor of Luxon, and standardizes on {FIELD} placeholders in HTTP/data nodes. Clean Code alignment: enforces 'meaningful names' (expression variables should be intention-revealing, not single letters or cryptic), 'small expressions' (keep each expression doing one transformation), 'no duplication' (avoid repeating the same expression pattern), and 'command-query separation' (separate data access from transformation in Code nodes). Trigger: 'enforce syntax', 'validate n8n expression', 'code node check'."
---

# n8n Syntax V2 Enforcer

Force every n8n expression and Code node to use the modern (2.x) API. The legacy
syntax still parses but is unstable across node types and produces audit failures.

## Hard Rules (violate = rewrite)

### 1. Expression placeholders
- Use `{{ }}` interpolation with the modern accessors.
- Prefer `{{ $json.fieldName }}` for the current node's data — field names should be intention-revealing (Clean Code: "use intention-revealing names; avoid encodings and prefixes").
- Use `{{ $('NodeName').item.json.fieldName }}` for a specific upstream node's item in an expression context.
- NEVER use `{{ $node['NodeName'].json.fieldName }}` — legacy.

### 2. Code-node accessors (Code typeScriptVersion >= 2)
- Current item data: `$input.item.json`
- First item of upstream: `$('NodeName').first().json`
- All items of upstream: `$('NodeName').all()`
- Legacy banned: `$json`, `items[0]`, `$node['X'].json`.
- Single-item code: use `$input.item.json` and return an object like `{ json: {...} }`.
- Clean Code alignment: Code node logic should do one thing (single responsibility), not mix data fetching with transformation.

### 3. Date handling
- Use `luxon` (`import { DateTime } from 'luxon';` returns ISO) — ALWAYS available in n8n Code nodes.
- NEVER import or reference `moment` / `moment-timezone`. Banned.
- `dayjs` allowed only if the node runtime documents it; prefer luxon.

### 4. HTTP / Webhook nodes
- Body fields configured via JSON path keys with `=fieldName` where applicable.
- For any field that accepts an expression, use `=\{\{ $json.X \}\}` pattern.
- Pagination, auth, and headers must be authored as object maps, not string-concatenated URLs.
- Clean Code alignment: avoid "needless repetition" — don't reuse the same expression pattern for multiple fields if the schema provides a dedicated key.

## Pre-write Checklist
1. I will verify the node `type` and `typeVersion` against current n8n (via n8n-mcp `get_node`) BEFORE writing parameters.
2. I will confirm which accessor set the target typeVersion expects (v1 vs v2).
3. I will prefer v2 accessors unless the node typeVersion is 1.x (then I explicitly note why).
4. I will never mix legacy and modern accessors in the same node.

## Self-audit regex checks (run mentally on every generated expression)
- `$node[` present  → FAIL → rewrite using `$('NodeName')` or `$json`.
- `items[0]` present → FAIL → rewrite using `$input.item.json`.
- `moment(` present  → FAIL → rewrite using luxon.
- `$json` inside a Code node with typeVersion 2 → FAIL unless `$json` is the object returned.
- **Clean Code: no duplication check** — if the same `{{ $json.X }}` pattern appears in multiple places without a dedicated parameter key, flag it as potential duplication and propose a shared variable or schema key instead.