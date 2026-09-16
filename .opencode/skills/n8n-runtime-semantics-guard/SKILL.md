---
name: n8n-runtime-semantics-guard
description: Guards n8n runtime semantics that schema checks miss. Use when building or reviewing any n8n workflow, before the gates run, or when a workflow validates green yet misbehaves live.
---

# n8n Runtime Semantics Guard

Schema-green does not mean runtime-correct. This skill encodes the runtime
facts learned the hard way on live n8n 2.30.x: response envelope shapes, item
pairing across fan-outs, per-item Code discipline, merge pairing, and the
Package H gate rules. Load it on every workflow build alongside
`gate-first-pass-builder`, and mirror every rule below with a live run.

## 1. Response envelope shapes (Redis / GET / KEYS)

- n8n HTTP GET of a single value returns `{propertyName: value}`, not the
  bare value. KEYS-style scans return a `{key: value}` map. Every reader
  downstream must unwrap tolerantly: accept the raw value, the propertyName
  wrapper, and the map form. A reader that assumes one shape silently yields
  `undefined` on the other two.
- Rule: the node that reads a store output never trusts `$input` passthrough
  after a reorder. Reorders, inserts, and fan-outs rebind `$input`, so every
  read names its source explicitly with a paired `$('NodeName')` ref that
  travels with the item.

## 2. Per-item-safe Code

- The Code node `mode` flag is ignored at runtime. Write every Code node so a
  single item executes correctly on its own: `$input.first()`, skip on `[]`,
  never `all()` across the whole run. Loops live in SplitInBatches or in
  fan-out items, never as merges inside split loops (merge nodes mis-pair
  items across iterations — remove the loop or unwind the merge).
- Merge `combine` needs `combineByPosition` AND joinMode keepEverything;
  the validator passes broken merge configs, runtime is the truth.
- Single-output nodes (code, redis, telegram, set) take single-group fan-outs
  only. A `main[1]` edge off a single-output node is dead config.

## 3. Fan-out execution order

- n8n runs fan-out branches depth-first, not in parallel. A flag written by
  one branch and read by another races. Encode state as data on the item
  (paired flag fields), never as branch timing. Suppression gates read the
  paired flag, never a side channel.

## 4. Sub-workflow input envelope

- Execute Workflow inputs arrive inside the webhook `.body` envelope, not at
  the top level of the payload. Lane entry nodes unpack `.body` first, then
  validate. Cross-workflow `$()` refs are forbidden; paired data travels with
  the item through Unpack entry nodes.

## 5. JavaScript discipline (Package H FAIL rules)

- Code nodes run JavaScript: `true` / `false` / `null`. Python literals throw
  at runtime (H2).
- Expressions must be the whole value: `={{ ... }}`. A literal prefix ahead
  of `{{...}}` evaluates wrong (H3).
- `requiresHumanApproval` belongs inside `parameters`, never at node level
  (H4, auto-fixed by the pipeline).
- Redis has no `decr` operation; use incr with a negative amount or SET (H6).
- `settings.errorWorkflow` must be a plain workflow-ID string, never an
  expression (H5).
- Node `id` values must be unique across the workflow (H1).

## 6. Warning-level traps (Package H warnings)

- `$env` reads need a `||` fallback (H7); literal `+HH:MM` offsets in URLs
  need `%2B` or Zulu form (H8); `alwaysOutputData` is inert on empty branches
  on 2.30.x, so verify the empty path with an always-one-item envelope (H9);
  dedup keys scope on `<chat>:<mid>`, never a bare message id (H10); calendar
  flows format wall time with an explicit zone such as Africa/Cairo (H11).

## 7. Verification

- Run `venv/bin/python scripts/build_gates_pipeline.py <artifact>
  --schema-cache memory/n8n_schema_cache.json` until VERDICT
  READY_FOR_DEPLOYMENT. Package H violations block under PRECISION with the
  same verdict chain as Packages A-G. Warnings stay non-blocking but each one
  maps to a real incident — clear them before delivery.
- Pairs with: gate-first-pass-builder, build-gates-pipeline,
  automation-known-issues-compass, n8n-deployment-ops-guard,
  incremental-generation.
