---
name: sre-reliability-engineering
description: "Applies Google's Site Reliability Engineering (SRE) to automation and services: define SLIs (real measured indicators), set SLOs (targets), manage an error budget (the allowable downtime that balances reliability vs feature velocity), eliminate toil through automation, run blameless post-mortems, and use monitoring with meaningful alerts (no alert fatigue). Encodes the SRE mindset: reliability is a product decision with a budget, not an engineering aspiration. Use when the user says 'SRE', 'SLI', 'SLO', 'error budget', 'toil', 'blameless post-mortem', 'alert fatigue', 'reliability target', 'nine nines', 'monitoring strategy', 'site reliability', or when a service must balance new features with staying up. Pairs with: data-intensive-application-design, continuous-delivery-pipeline, release-it-production-hardening, root-cause-post-mortem-analyzer."
---
# Site Reliability Engineering (SRE - Google)

SRE's core shift: reliability is a PRODUCT DECISION managed with a budget. You do not maximize uptime - you set a target (SLO), measure it with real signals (SLI), and spend the error budget on feature velocity. Toil is the enemy; automation is the cure.

## The SLI / SLO / Error Budget model

### SLI (Service Level Indicator) - the real measurement
- A measurable ratio, usually 'good events / total events' over a window.
- Examples: availability (successful requests / total), latency (requests under threshold / total), throughput, durability, correctness.
- Rule: define 'good' precisely before you measure. Vague SLIs produce useless targets.

### SLO (Service Level Objective) - the target
- A target on the SLI with a window: '99.9% availability over 30 days', '95th percentile latency under 300ms'.
- The SLO is what you PROMISE; everything below it is unacceptable, above it is surplus.

### Error Budget = 100% - SLO
- The allowable proportion of failures. 99.9% SLO = 0.1% error budget (about 43 minutes per month).
- The budget is SPENDABLE: when the budget is full, launch features; when it is exhausted, STOP releasing and fix reliability first.
- This converts 'reliability vs velocity' from a fight into a measured trade-off.

## Toil (the SRE enemy)

Toil = manual, repetitive, automatable work with no enduring value: manual restarts, hand-written reports, copy-paste configs, ticket shuffling.
- Rule: if it is toil, AUTOMATE it. If automation is cheaper than one more manual run, automate now.
- Aim: toil under 50% of time; SRE teams engineer, they do not shovel.

## Blameless Post-Mortems

- The goal is the SYSTEM's failure, never the person's. Remove 'who' from the findings.
- Every incident gets: timeline, root cause, contributing factors, actions (fixes), and a follow-up to verify the fix.
- Blame kills the truth. Truth is the only thing that prevents recurrence.

## Monitoring and Alerts (no alert fatigue)

- Alerts must be page-worthy: an alert that does not require action is noise.
- Prefer SLO-based alerting (error-budget burn alerts) over threshold spam.
- Dashboards for humans, alerts for decisions.

## Checklist (pre-deploy for any service)

- [ ] SLI defined with a precise 'good' criterion
- [ ] SLO target set with a window
- [ ] Error budget computed and tied to a release rule
- [ ] Toil inventory made; top toil automated
- [ ] Post-mortem template blameless by construction
- [ ] Alerts page only on actionable conditions

## Violations (severity)

- **V1 - No SLO** (HIGH): Uptime promises with no measured target. Fix: define SLI + SLO first.
- **V2 - Alert fatigue** (HIGH): Paging on every anomaly. Fix: SLO-burn alerting, actionable pages only.
- **V3 - Toil accepted as normal** (MEDIUM): Manual steps repeated weekly. Fix: automate each one.
- **V4 - Blame culture** (MEDIUM): Post-mortems name people. Fix: make them blameless.
- **V5 - Error budget ignored** (MEDIUM): Releasing while burning the budget. Fix: gate releases on remaining budget.

## Verification

For any delivered service, produce its SLI, SLO, error budget, and one blameless post-mortem template. Run the build gates and require READY_FOR_DEPLOYMENT.
