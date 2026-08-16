---
name: code-linter-python-js
description: "Deterministically lint and structurally check any JavaScript or Python written for n8n Code nodes before delivery. Use ONLY when authoring or reviewing n8n Code-node scripts, to guarantee valid syntax, correct scope, and an array-of-objects return shape."
---

# Code Linter: Python & JavaScript for n8n Code Nodes

## Rules
1. **Return shape (JS)**: if multi-item, return an array of `{ json: {...} }`.
   If single-item, return `{ json: {...} }`. Never return a bare object/primitive.
2. **Return shape (Python)**: return a list of dicts, or a dict with `"json"` key(s).
   n8n Python Code node expects a JSON-serializable structure.
3. No `import`/`require` of modules not whitelisted (`N8N_CODE_NODE_ALLOWED_MODULES`).
   JS safe set includes `crypto`, `luxon`, `lodash` (if enabled). Never `fs`, `http`, `net`.
4. Avoid `var`. Use `const`/`let`. Prefer arrow functions where clear.
5. Handle missing fields defensively: optional chaining `?.` in JS, `.get()`/`None` in Python.
6. No infinite loops: any `while` must have a bounded counter; prefer `.filter().map()`.
7. Keep code deterministic: no `Math.random()`, `Date.now()` (unless intended & documented),
   or `process.exit()`.

## Static self-check procedure (do NOT skip)
1. `(JS)` Balanced braces/parens: open(`{(` count equals close(`})`.
2. `(JS)` Every early `return` path emits `{ json: ... }` or array-of-that.
3. `(Python)` No `range` on a potentially unbounded input without `.limit()` guard.
4. Variable names: no typos against referenced fields — verify each `input.field`.
5. If code is > 60 lines, mentally run 3 sample inputs through it and note output shape.

## Critical n8n gotchas
- JS item context: with `typeVersion >= 2` use `$input.item.json`; legacy `$json`
  only for typeVersion 1 or expression context. Adjust per node typeVersion.
- In newer n8n JS Code nodes, an item object may need `{ json, binary, pairedItem }` —
  `pairedItem` maps output items to input runs for AI nodes.
- Access upstream: `$('NodeName').first().json` — NOT `$node['Node'].json`.

## Exit criteria
- [ ] Syntax valid (no parse errors).
- [ ] Returns array-of-objects (or documented `{json}`).
- [ ] References only existing fields from the schema.
- [ ] No banned modules, no unbounded loops, no nondeterminism.
- [ ] TypeVersion-aware accessors used.