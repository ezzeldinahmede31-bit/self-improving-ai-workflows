---
name: zapier-system-cloner
description: "Replicates any Zapier (Zap) system — especially premium/expensive ones — with identical outputs and quality on n8n or code, using different (free/local) tools when needed. Reads the Zap definition via one of three sources (official Zapier Editor JSON export / zapier-sdk CLI draft JSON / user description), maps every step (trigger, filter, paths, formatter, code, digest, delay, AI action, search) to n8n nodes with the scripts/zap2n8n.py converter, designs free equivalents for Zapier-premium features, builds the n8n workflow through the connected n8n MCP, validates, deploys and runs a PARITY test: same inputs → same outputs, field by field. Use whenever the user says 'clone this Zap', 'replicate this system from Zapier', 'make the same automation on n8n', 'this Zap costs money — rebuild it free', 'monkey see it on Zapier', 'استنسخ/انقل نظام Zapier', or shares a Zapier export/description to rebuild. Pairs with zapier-sdk, zapier-make-patterns, n8n-mcp-workflow-builder, n8n-error-boundary-architect, n8n-e2e-test-runner, n8n-subworkflow-modularizer."
---

# Zapier System Cloner

Goal: take ANY Zapier workflow and deliver a working clone with the same
outputs/quality, usually on n8n (self-hosted = free forever) using different
tools if the original uses premium-only ones.

## Phase 1 — INGEST (get the Zap definition)

Priority order:

1. **Zapier Editor JSON export** (best): user opens the Zap → Edit →
   ⇤/⋯ menu → Export → JSON. Read that file directly.
2. **zapier-sdk** (when the user is logged in — `npx zapier-sdk get-profile`):
   ```bash
   npx zapier-sdk list-workflows --json          # find the Zap ID
   npx zapier-sdk --experimental list-workflow-drafts <workflow-id> --json
   ```
   yields the full step structure (trigger + steps, app, operation, inputs).
3. **Description/screenshot**: if neither is available, interview the user
   (one round of questions max): What triggers it? What does each step do?
   What are the exact outputs (message/row/email shape) that must be
   identical? Which apps hold the data, and can we reach them?

ALWAYS end Phase 1 with a written capability table: every step =
`{source app/operation, inputs used, output shape, side effects}`.

## Phase 2 — MAP (Zapier → n8n)

Run the converter (it knows ~40 mappings + generic fallbacks):

```bash
venv/bin/python scripts/zap2n8n.py <zap.json> --out <tmp>/cloned.json
```

Then review the report:
- **[MAP]** = direct node mapping — keep it.
- **[GENERIC_HTTP / GENERIC_CODE]** = right idea, wrong lawnmower: rebuild
  the operation properly (HTTP Request node configured against that API, or
  real Code-node logic), NOT the placeholder.
- **[UNMAPPED]** = design decision needed (see Phase 3).

Core mapping cheat-sheet (already in the tool):
trigger (webhook/schedule/poll) → Webhook/Schedule/★Trigger nodes;
Filter → IF node; Paths → Switch; Formatter → DateTime/Code;
Code by Zapier → Code node (JS/Python); Delay → Wait;
Digest → Code aggregation (accumulate + schedule, or data-table SQL);
AI by Zapier → OpenAI node (or our LLM MCP) — same job, cheaper;
Search → Get/Fetch node then IF; Webhook by Zapier → n8n Webhook.

## Phase 3 — GAP DESIGN (premium → free, 1:1 behavior)

For every UNMAPPED/premium step design the substitute BEFORE building:

- **compute pricing**: what the Zap costs/mo vs the clone at $0 (motive).
- **AI steps**: Zapier AI Actions (paid per task) → OpenAI node with the
  same model+prompt, or a local model via our stack if offline is wanted.
- **Digest/aggregation**: Zapier-only → Code node with `accumulate()` over
  triggers + a periodic Flush workflow, or Supabase/data-table aggregation.
- **Premium app/API not in n8n**: HTTP Request node with the app's public
  REST API (documented by the app) + credential as n8n credential.
- **Pagination/large data**: use n8n pagination options or a Loop.
- **Error behavior parity**: replicate On Error handling — see
  `n8n-error-boundary-architect`.

Write the design decision for each gap BEFORE any build step.

## Phase 4 — BUILD on n8n (via the connected n8n MCP)

1. `n8n_create_workflow` with the skeleton from Phase 2 (nodes +
   connections). 2. Refine per Phase-3 design (update nodes, expressions).
   Port every literal and reference from the Zap inputs — the `zap2n8n
   --port-inputs` flag copies scalar values and converts `{{field}}`
   references to `={{ $json.field }}` (double-check each one).
3. Wire credentials: register n8n credentials via
   `n8n_manage_credentials getSchema` → create (NEVER hardcode keys —
   `n8n-credential-security-guard`).
4. `n8n_validate_workflow` → fix errors (autofix if needed) → repeat until
   clean.
5. Error boundaries + retries (`n8n-error-boundary-architect`), pinned
   sample data (`n8n-pinned-data-mocking`) so the user can test manually.
6. Split >6-node single-responsibility chains into sub-workflows
   (`n8n-subworkflow-modularizer`).

## Phase 5 — PARITY VERIFY (the honest gate)

Same inputs → same outputs, field by field:

1. `n8n_test_workflow` with a representative sample payload (mirror the
   original Zap's execution history if available).
2. Compare: output data shape (field names/nesting), side effects (email
   sent, row written, message posted), error behavior (what happens on
   bad input — the Zap's response vs the clone's).
3. Quality gate = original behavior reproduced with no missing steps and no
   extra side effects. Document ANY deviation (e.g., "original uses Gmail
   aliases, clone uses the same account creds").
4. Deliver: workflow JSON + a parity report (what matches, what differs,
   why) — never claim 'identical' without the test run.

## Safety rules

- NEVER hardcode credentials anywhere (refs only).
- NEVER read/modify the user's Zapier Zaps without permission; cloning is
  read-only on Zapier until explicitly asked to create.
- If the Zap uses an app we cannot reach (no API, no n8n node, no creds),
  SAY SO and offer the substitution explicitly — no silent approximations.