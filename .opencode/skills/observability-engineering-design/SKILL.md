---
name: observability-engineering-design
description: "Design systems that explain themselves: SLIs, tracing, cardinality discipline. Use when the user says 'can't debug prod', 'observability', 'distributed tracing', 'cardinality explosion', 'why is it slow in prod', 'المراقبة', or needs telemetry designed in, not bolted on."
---

# Observability Engineering Design

Distilled from Majors/Fong-Jones/Miranda *Observability Engineering*,
Google SRE monitoring chapters, *Distributed Systems Observability*
(Mastering), Honeycomb practices. Observability = ability to ask new
questions in prod without shipping new code.

## The protocol

1. **SLIs before dashboards.** User-visible goodness first (success
   rate, latency distribution), then the telemetry that proves it.
   Dashboards without SLIs are wallpaper.
2. **Trace the critical path.** Every request carries a trace ID across
   service boundaries; sample head-based for errors, tail-based for
   latency outliers. One slow hop must be findable in one query.
3. **Cardinality discipline.** High-cardinality fields (user ID,
   request ID) go in traces, never in metric labels. Metric labels
   stay bounded (service, endpoint, status, region). Cardinality
   explosion is a self-inflicted outage with a bill attached.
4. **Logs as events, wide not many.** One structured event per request
   with all context beats ten log lines to correlate. Debug by
   filtering, not by grepping.
5. **Probes that gate traffic.** Health endpoints distinguish liveness
   (restart me) from readiness (stop sending traffic). K8s restarts
   what lies about liveness and starves what lies about readiness.
6. **Debug-driven design.** For every dependency ask: when this fails
   at 3am, which single query finds it? If none exists, the design is
   not done. Pairs with `chaos-resilience-practice` detection times.

## Verification

Observability ships with: SLIs + SLOs, trace coverage of critical
paths, label-cardinality budget, one-event-per-request logging,
liveness/readiness split, named 3am query per dependency.

## Pairs with

- `sre-workbook-practices` (SLOs), `chaos-resilience-practice`
  (detection proof), `production-capacity-planning` (saturation
  signals), `system-design-production-blueprint` (phase 6),
  `kubernetes-operations` (probes).
