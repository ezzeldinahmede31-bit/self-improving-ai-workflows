---
name: live-workflow-surgery
description: "Change a live n8n workflow without breaking it: find seams, lock behavior with characterization parity runs, extract via the strangler pattern (new sub-workflow alongside, parallel run, cut over), and roll back on deviation. Use when a production graph must be split, refactored, or fixed while business-as-usual continues, or before touching any workflow with real executions. Pairs with n8n-oom-crash-recovery, n8n-subworkflow-modularizer, n8n-delivery-verification-gate, deploy-signoff-governance."
---

# Live Workflow Surgery

Touch production graphs the way surgeons operate: expose, isolate, verify.

## Sources (adopted baselines)

- "Working Effectively with Legacy Code" (Feathers): legacy = code without
  tests. First find SEAMS (places to split behavior without editing everything),
  then lock current behavior with CHARACTERIZATION tests (record what it DOES,
  not what it should do), then change in small covered steps.
- "Monolith to Microservices" (Newman, O'Reilly): STRANGLER FIG (grow the new
  beside the old, intercept, migrate piece by piece — never big-bang rewrite),
  BRANCH BY ABSTRACTION (new implementation behind the same interface, toggled),
  PARALLEL RUN (old and new side by side, compare before cutover).

## 1. Find the seams (read-only, zero risk)

On the live graph, mark candidate cut lines where data flow narrows: one
trigger fanning into lanes, health-checks vs business logic, formatting vs
sending. A seam is good when: inputs/outputs are explicit items, the section
has one job, failure inside it is independent of the rest. Prefer cutting where
an `executeWorkflow` call already exists — the seam is half-built.

## 2. Lock behavior first (characterization, not unit tests)

Before any edit: capture 3+ real executions (inputs + per-node outputs) as the
golden set. Export the workflow JSON to git. The rule from Feathers: you may
not change what you cannot replay. For n8n the golden set is pinned execution
data + the exported JSON version — the parity oracle for step 4.

## 3. Strangler extraction (one seam per cycle)

1. Build the new sub-workflow OUTSIDE the live graph (inactive, separate id).
2. Route via abstraction: point the seam's call at the new sub-workflow behind
   a flag the live graph already reads (settings field, Redis key, If-switch).
   Flag off = old path, flag on = new path. Deployment separated from release.
3. Parallel run: enable for a bounded window, diff new outputs against the
   golden set field by field. Any deviation = stop, diagnose, fix — never
   "close enough" on money/data paths.
4. Cut over: flip the flag, watch the first live executions against expected
   outputs, keep the old path reachable for one cycle.
5. Remove the old section only after a clean window. Transitional routing is
   temporary by design; schedule its deletion or it becomes permanent clutter.

## 4. Rollback (pre-written, not improvised)

Every cycle ships with: prior JSON version id, flag-off procedure (one edit),
owner, time estimate. No named restore point = no surgery (atomicity rule from
deploy-signoff-governance).

## Worked analysis (read-only, this workspace, 2026-09-19)

`eng-router` (32 nodes, inactive, schedule every 2 min): 1 trigger, health
section (Redis/Calendar probes, alert markers, Telegram), routing section (5
time/if gates), 6 lane calls ALREADY via executeWorkflow. Seams found: (a)
health block vs router block, (b) each lane call. Verdict: split-ready, but
the crash signature (21ms) points at DATA VOLUME (unbounded key listing +
Split Map To Items) as fier as graph size — apply the data diet BEFORE surgery.
NO live edit performed; this plan is the Tier-2 evidence packet input.

## Verification

Parity diff clean on golden set, first live executions match, old path removed
on schedule, incident-free window recorded in automation-known-issues-compass.
