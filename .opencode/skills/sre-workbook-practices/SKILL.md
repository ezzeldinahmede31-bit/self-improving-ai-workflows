---
name: sre-workbook-practices
description: Applies The Site Reliability Workbook (Beyer et al.) to operating automation reliably: every service is defined by its SLIs and SLOs, governed by an error budget, and improved through blameless postmortems. Covers SLO construction, error-budget policy, on-call, toil elimination, and capacity planning. Use when the user says 'define an SLO', 'run an on-call rotation', or 'eliminate toil'.
---
# sre-workbook-practices

The Site Reliability Workbook is the hands-on companion to Google's SRE approach: it turns reliability into a measurable, budgeted, and improvable property of every service. Use this skill to give the automation stack the same operational discipline as a production service.

## Core principles
- Reliability is a product decision: an SLO is the target you promise, and an error budget is the room left to ship features and take risk.
- SLIs must be measurable indicators of user-visible behavior, collected honestly over a rolling window.
- Error-budget burn alerts, not raw downtime alerts, drive paging; only page when the budget is being consumed.
- Toil is work that is manual, repetitive, automatable, and non-essential; the goal is to eliminate it, not to heroic it.
- Postmortems are blameless and action-driven: fix the system and the process, never the person.
- Capacity planning starts from real demand data and predicted growth, not from guesses.
- Measurement precedes improvement: you can only manage reliability you can actually observe.

## Key patterns
- Define SLIs from the user's perspective: availability, latency, throughput, and durability of the workflow's output.
- Tiered SLOs: align the target with the consumer, giving the critical path a tighter budget than a reporting side-effect.
- Error-budget policy: when the budget is exhausted, freeze risky releases until it refills.
- A weekly on-call rotation with a written schedule, an incident command structure, and a time limit on paging.
- A toil ledger: keep track of manual steps and target automating each one.
- Burn-rate alerting: page fast on a high burn rate and slow on a low one.
- Rolling windows for SLI evaluation keep the signal fresh and the alerting honest.

## Applying this to n8n/automation/code
- Give every delivered workflow explicit SLIs (execution success rate, end-to-end latency, freshness of scheduled runs) and an SLO.
- Use the error budget as the gate: a workflow that exceeds its budget goes to triage, not to more retries.
- Automate the on-call: alert only on budget burn and route to Telegram with the failing execution linked.
- Log recurring manual fixes as toil and turn each one into an n8n workflow or an Error Trigger handler.
- Publish an SLO dashboard so every workflow owner sees budget consumption before it is gone.
- Run a blameless review after every SLO breach and wire the action items back into the workflow.

## Hard rules
- Never page on a symptom without a burn-rate tie to the budget.
- Never skip the blameless postmortem when an SLO breach happens.
- Never accept a manual step that repeats weekly; schedule its automation.
- Always collect SLI data before promising an SLO.
- Never let a workflow with a burned budget keep shipping risky changes.

## Pairs with
sre-reliability-engineering, accelerate-dora-metrics, continuous-delivery-pipeline, release-it-production-hardening, devops-handbook-flow
