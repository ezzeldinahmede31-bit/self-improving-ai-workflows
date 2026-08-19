---
name: sre-workbook
description: Applies The Site Reliability Engineering Workbook (Beyer et al.) to actually running SRE: building SLOs from SLIs, designing and operating alerting, on-call, incident response, postmortem, and capacity planning practices, and running reliability experiments, with concrete exercises instead of theory. Use when the user says 'SRE workbook', 'build an SLO', 'SLI', 'alerting', 'on call', 'incident response', 'postmortem', 'capacity planning', 'reliability experiment', 'Beyer SRE', or when SRE practices must be implemented, not just described.
---

# The Site Reliability Engineering Workbook (Beyer, Murphy, Rensin, Kawahara, Thorne)

The Workbook turns the SRE book into hands-on practice: measure, alert, respond, and improve. This skill applies those exercises to a real service.

## SLIs and SLOs

- An SLI is a measurable signal of reliability; choose the signal the users actually feel.
- An SLO is a target with a time window; the error budget is the headroom.
- Build the SLO from the SLI honestly; the metric must be computable from what you collect.

## Alerting and on-call

- Alert on symptoms users feel, not on every anomaly; each alert must be actionable.
- A page requires a runbook or an owner; alerts without an action are noise.
- Rotations and escalation define who responds; keep the paging policy documented.

## Incident response and postmortems

- Incidents have roles (incident commander, comms, responders) and a timeline.
- Postmortems are blameless: find the system cause, not the human fault.
- Every postmortem yields action items; track them until they ship.

## Capacity and experiments

- Capacity planning projects the load and sizes the service before it saturates.
- Reliability experiments (chaos-style) verify the system behaves when a piece fails.
- The measurement loop is the whole discipline: SLO, budget, alert, respond, improve.

## Pairs with
sre-reliability-engineering, continuous-delivery-pipeline, practice-of-cloud-system-administration, database-reliability-engineering, root-cause-post-mortem-analyzer
