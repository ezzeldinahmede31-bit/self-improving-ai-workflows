---
name: n8n-autodoc-mermaid
description: "Automatically generate a README.md with a Mermaid flowchart, inputs/outputs table, and step-by-step client runbook for every n8n workflow delivered. Use ONLY when delivering a completed or substantially-changed n8n workflow, or when a user asks to document an existing workflow."
---

# n8n Auto-Documentation & Mermaid Generator

Every delivered workflow ships with a human-readable README that a non-technical
client can follow.

## Output contract (per workflow)
Generate `<WorkflowName>.README.md` containing EXACTLY:
1. **Overview** — 1-2 lines: what the automation does, who uses it.
2. **Mermaid flowchart** — a `flowchart TD` graph of ALL nodes in order, with branches:
   - node names as boxes
   - arrows showing main flow + the error branch (from Error Trigger path)
   - trigger at top, final delivery at bottom
   - example:
     ```mermaid
     flowchart TD
       A[Telegram Webhook] --> B[Parse Intent]
       B --> C[Fetch Brand: Overpass]
       C --> D[LLM Classify]
       D --> E{Valid email?}
       E -- yes --> F[Save to DB]
       E -- no --> G[Error Branch]
       F --> H[Build CSV]
       H --> I[Send Telegram File]
     ```
3. **Inputs / Outputs table** — markdown table:
   | Field | Type | Source | Example | Required |
   |-------|------|--------|---------|----------|
   list every input the client must supply and every output that returns.
4. **Client runbook** — numbered steps in plain Arabic/English (user's preference):
   how to trigger, what to expect, how to read results, common errors & fixes.
5. **Configuration notes** — credentials used (by NAME, never values), env vars,
   and any manual step the client must do (e.g. enable workflow, add webhook).

## How to build the Mermaid
- Read the workflow structure (n8n_get_workflow `mode: structure` or the JSON).
- Walk connections in order; name nodes using their `name` field (not type).
- Fold sub-workflows as a single node labeled `sub:name` (no need to expand internals).
- Include the error/notification branch so the client sees what happens on failure.

## Delivery rules
- File is written next to the workflow JSON backup, e.g.
  `<WorkflowName>/README.md`.
- If user asked for a specific language → render runbook in that language.
- Never embed real credentials / URLs-with-tokens in the README.
- If the user does not want docs: still generate, but report it as optional.

## Acceptance
- [ ] Mermaid renders (balanced `graph/flowchart` + `-->`/`-- text -->`).
- [ ] Every node appears at least once.
- [ ] Inputs/outputs table complete.
- [ ] Runbook is a client can follow or paste to their team.