---
name: chaos-resilience-practice
description: "Prove resilience by breaking things on purpose: game days, fault injection, blast-radius control. Use when the user says 'chaos engineering', 'game day', 'fault injection', 'prove failover works', 'kill a node', 'اختبار الفشل', or needs evidence that the failure story is real, not documented."
---

# Chaos Resilience Practice

Distilled from Basiri et al *Chaos Engineering*, Rosenthal & Chamorro
*Chaos Engineering* (O'Reilly), Nygard *Release It!*, Google SRE
Workbook (diRT), *Site Reliability Engineering* incident lore. Unexercised
failover is a rumor.

## The protocol

1. **Steady-state hypothesis.** Define normal first: SLOs, error rate,
   p99, queue depth. No hypothesis = no experiment, just vandalism.
2. **Blast radius on paper.** One AZ before one region; staging-shaped
   before prod; 1% traffic before 100%. Every experiment names its
   abort condition and its rollback (one command, tested).
3. **The ladder (never skip rungs).** Kill a pod -> kill a node ->
   blackhole an AZ -> partition the network -> expire certs -> lose
   the primary DB -> lose a region. Each rung needs the lower rung's
   evidence attached.
4. **Game day.** People + runbook + timer: inject, observe detection
   time, follow the runbook, record every deviation. The runbook is
   the patient — the system is the excuse.
5. **Close the loop.** Every surprise becomes: a fix, a monitor, or a
   runbook line. Untriaged surprises are how the same outage bills
   twice. Track mean-time-to-detect separately from mean-time-to-fix.

## Stable patterns under test (Release It! core)

- Timeouts on every call, circuit breakers with half-open probes,
  bulkheads per dependency, backpressure instead of queues-that-grow,
  fail-fast + let-it-crash supervision, steady-state health that
  actually gates traffic.

## Verification

Resilience ships with: steady-state metrics, experiment ladder with
evidence per rung, abort + rollback per experiment, game-day notes
with detection/fix times, surprise backlog at zero. Docs without
drills = rumor.

## Pairs with

- `system-design-production-blueprint` (phase 6 failure story),
  `sre-workbook-practices` (SLOs/error budgets),
  `release-it-production-hardening` (stability patterns),
  `production-capacity-planning` (failure-domain math),
  `observability-engineering-design` (detection).
