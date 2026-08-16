---
name: n8n-subworkflow-modularizer
description: "Split complex n8n automations into small, independent sub-workflows wired together with Execute Workflow nodes. Use when building, refactoring, or reviewing any n8n workflow that exceeds ~6 nodes or has multiple distinct responsibilities."
---

# n8n Sub-Workflow Modularizer

One giant workflow is a maintenance and debugging trap. Split by responsibility.

## When to split
- More than ~6 nodes.
- Distinct responsibilities: ingestion / processing / classification / storage / delivery.
- Repeated logic used in several workflows (shared helper as sub-workflow).
- Need to run parts in parallel or independently.

## Split categories (typical)
| Category | Example sub-workflow |
| --- | --- |
| Input/Trigger | Telegram receive, cleanup ↔ normalize payload |
| Processing | LLM classification, enrichment |
| Business logic | Filter by size/country, dedupe |
| Persistence | Upsert to Supabase / Redis / file DB |
| Delivery | CSV/XLSX build + Telegram file send + summary |
| Errors | Format + notify on any failure |

## Wiring rules
- Use `n8n-nodes-base.executeWorkflow` node.
- Pass data via `options: { data: "={{ $json }}", sourceMain: ... }` (array of objects).
- Return data from sub-workflows via the last node; capture with the Execute Workflow node's `dataPropertyName` (default `data`). Access results as `$json.data[0].json`.
- Set timeout on the Execute Workflow node so parent isn't blocked forever.
- Keep sub-workflows stateless where possible; pass all context in (see state-machine-persistence for multi-turn state).

## Naming convention
`sub:<purpose>` e.g. `sub:classify-brands`, `sub:save-to-db`, `sub:send-telegram`.
Main workflow names stay descriptive e.g. `Lead Gen: Telegram → Export`.

## Benefits checklist (report when done)
- [ ] Each sub-workflow has a single responsibility and ≤ ~6 nodes.
- [ ] No node count > 12 in any single workflow (unless unavoidable + justified).
- [ ] Sub-workflows are independently testable (pinned data in each).
- [ ] Error handling lives at the boundary (parent) and inside risky subs.