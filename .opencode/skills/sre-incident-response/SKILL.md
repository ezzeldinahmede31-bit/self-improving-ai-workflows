---
name: sre-incident-response
description: "Run automation incidents like Google SRE: roles, stop-the-bleeding first, structured troubleshooting, blameless postmortem that feeds the known-issues catalog, and overload/cascade defenses. Use when an execution crashes, a workflow degrades, alerts fire, or after any outage to convert it into durable prevention. Pairs with automation-known-issues-compass, n8n-debugging-official, deploy-signoff-governance, stability-patterns-production."
---

# SRE Incident Response for Automation

Incidents are unplanned investments — collect the return in prevention.

## Sources (adopted baselines)

- "Site Reliability Engineering" (Google, O'Reilly, 2e 2026): on-call as a
  tool not a burden, emergency response (stop bleeding before root-causing),
  incident management roles, blameless postmortem culture, outage tracking,
  testing for reliability, overload and cascading-failure handling.

## 1. Roles (even solo, name them per incident)

Commander (decides, owns the clock), Responder (hands on graph/logs), Scribe
(notes timeline + actions). Solo = rotate hats explicitly so decisions do not
get lost in doing. Page with severity: S1 money/data loss, S2 degraded, S3
cosmetic/flaky.

## 2. Respond (bleeding first, curiosity later)

1. Stop the bleeding: deactivate the hot workflow, narrow the trigger, or flip
   the seam flag to the safe path. Graceful degradation beats heroics.
2. Structured troubleshooting: timeline (what changed recently?), narrow by
   halves (which section first fails?), one hypothesis at a time, write down
   each disproof. Adrenaline-driven random edits are forbidden.
3. Stabilize: confirm steady state restored (success executions flowing,
   latency normal) before declaring all-clear.

## 3. Postmortem (blameless, mandatory for S1/S2)

Template: summary, impact (executions affected, window), timeline, root cause
(ask why five times past the proximate trigger), what went well, action items
with ONE owner each. No names in the cause column — process failed, not people.
Every action item lands somewhere executable: a gate rule, a skill section, a
workflow fix, or a monitoring alert. An action item with no home is theater.

## 4. Catalog feed (this workspace's outage tracker)

Each closed incident appends: one row to automation-known-issues-compass §0
(symptom → cause → fix) and one line to `memory/n8n_error_patterns.md`. The
fleet never pays for the same incident twice — that is the whole return on
the investment.

## 5. Overload and cascade guards

Fast triggers on slow lanes need queues in the middle; alert on queue depth,
not just failures. Cascading failure plan per graph: which lane sheds first,
which alert fires once, where the bulkhead holds. Test with the spike input
before the spike finds you.

## Worked case (2026-09-19)

eng-router 4795 crash handled per §2 (read-only triage, no live touch since
inactive): root cause hypothesis = data volume (unbounded listing), recorded
in compass + error patterns per §4. Next §3 action items: cap listing (owner:
you, Tier-2), add timeouts, parity-golden capture before any split.

## Verification

Postmortem filed, action items homed, catalog rows added, re-occurrence
monitor armed (alert on the same signature). An incident with no catalog row
is an unpaid bill.
