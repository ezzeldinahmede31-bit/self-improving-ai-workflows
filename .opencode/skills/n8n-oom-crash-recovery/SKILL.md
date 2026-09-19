---
name: n8n-oom-crash-recovery
description: "Diagnose and fix n8n out-of-memory crashes (NodeCrashedError / WorkflowCrashedError) and oversized graphs: the OOM triage ladder, memory knobs (NODE_OPTIONS heap, N8N_CONCURRENCY_PRODUCTION_LIMIT, queue mode), the data diet (Split In Batches, strip fields early), and the split-vs-leave decision for graphs past 15-20 nodes. Use when an execution shows status crashed, n8n may have run out of memory, a workflow has 20+ nodes and the editor is sluggish, or you must decide whether to split a live graph into sub-workflows. Pairs with n8n-subworkflow-modularizer, n8n-deployment-ops-guard, n8n-error-boundary-architect, automation-known-issues-compass."
---

# n8n OOM Crash Recovery

Fix the crash class that looks like a logic bug but is a memory bug.

## Sources (adopted baselines, not reinvented)

- n8nLab "Strengthen Your n8n Infrastructure for Maximum Performance" (2026):
  OOM is almost always infra/workflow-architecture, not n8n itself. Six layers,
  fix order: workflow architecture first, then queue/workers, DB, resources.
- n8n Blog "Production AI Playbook: Complex Agent Patterns" (2026): break past
  15-20 nodes into sub-workflows; each piece independently testable.
- "n8n Workflow Engineering with AI and Scalable Systems" (Automation
  Engineering Series Book 3, 2026): queues, workers, DevOps scaling patterns.

## 1. Triage ladder (in order, stop at first hit)

1. Read the crashed execution with `?includeData=true`. `NodeCrashedError` /
   `WorkflowCrashedError` + "may have run out of memory" = OOM until proven
   otherwise. Note crash latency: crash-in-milliseconds on a big graph = memory,
   crash-after-minutes on one node = that node's data volume.
2. Graph size: note the node total. Past ~15-20 nodes on one canvas = split candidate.
3. Data volume: which node holds the biggest items? JSON width x depth x item volume
   is the heap cost. A 150-field object through 20 nodes multiplies fast.
4. Host: is the main process also the executor? (`EXECUTIONS_MODE` != queue +
   sluggish editor under load = main process starving.)
5. Concurrency: `N8N_CONCURRENCY_PRODUCTION_LIMIT` unset (= unlimited) +
   parallel load = guaranteed OOM under spike.

## 2. Memory knobs (infra, cheapest first)

- `NODE_OPTIONS=--max-old-space-size=<~75% of container RAM>` (e.g. 1536MB in
  a 2GB container). Node.js must be told its ceiling or it eats the host.
- `N8N_CONCURRENCY_PRODUCTION_LIMIT=5..10` per worker. Unlimited default is
  the most common production OOM cause.
- Queue mode (`EXECUTIONS_MODE=queue` + Redis `maxmemory-policy noeviction` +
  2+ workers) separates editor/API from execution. Enable when: >5 concurrent
  heavy executions, sluggish editor, or sub-workflow fan-out at scale.
- Redis eviction must be `noeviction`: evicted queue keys = silently lost
  executions.

## 3. Data diet (workflow, fixes most single-graph OOMs)

1. Paginate everything: never hold 10k+ rows in memory; Split In Batches
   (500/batch), write, clear, loop. Flat memory footprint.
2. Strip early: Set/Edit-Fields node right after ingest drops unneeded columns
   before the other 20 nodes multiply them.
3. Route early: If-node discards invalid payloads BEFORE expensive sub-workflows
   or AI calls (saves workers + DB writes).
4. Scope Code nodes: `runOnceForEachItem`, no closures capturing big arrays
   across executions; chunk CPU-bound work (parallel branches help I/O, saturate
   CPU on compute).

## 4. Split-vs-leave decision (live graphs)

SPLIT when two or more hold: >20 nodes, sluggish editor on that canvas, one
section fails independently of the rest, logic is reused elsewhere, different
parts need different owners, or a section needs its own error workflow.
LEAVE when: graph is small, stable, rarely touched, and the crash was a
one-off spike (fix knobs/diet first; surgery on a stable earner needs a
staging proof, never a live edit).

## Worked case (this workspace, 2026-09-19)

`eng-router` (32 nodes, inactive) execution 4795 → `crashed` in 21ms,
`NodeCrashedError` "possible out-of-memory". Verdict per §4: SPLIT candidate
(size + independent sections), but NO live edit without owner approval and a
staging parity run first.

## Verification

After a fix: re-run the failing input, execution status `success`, heap flat
across 3 consecutive runs, editor responsive. Record the before/after in
`automation-known-issues-compass` §0.
