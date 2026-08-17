---
name: accelerate-dora-metrics
description: "Applies Forsgren, Humble & Kim's Accelerate to measure and improve software delivery performance using the DORA metrics: Deployment Frequency, Lead Time for Changes, Change Failure Rate, and Mean Time to Restore (MTTR). Connects the four metrics to the capability 'clusters' (continuous delivery, architecture, product, lean, culture) and identifies elite vs low performers with honest, measured data - never vibes. Use when the user says 'DORA metrics', 'deployment frequency', 'lead time', 'change failure rate', 'MTTR', 'Accelerate', 'elite performers', 'devops performance', 'Forsgren', 'measure delivery', 'how fast is our team really', or when delivery speed must be measured and improved. Pairs with: continuous-delivery-pipeline, devops-handbook-flow, self-benchmark-runner, sre-reliability-engineering."
---
# DORA Metrics (Accelerate - Forsgren, Humble & Kim)

Accelerate proved with data (over 4 years of surveys) that software delivery performance reduces to FOUR metrics, and that elite performers are not a personality type - they are a set of capabilities any team can adopt. The skill: measure the four, then adopt the capabilities that move them.

## The Four DORA Metrics

| Metric | Definition | Elite benchmark |
|---|---|---|
| Deployment Frequency | How frequently code reaches production | On-demand (multiple per day) |
| Lead Time for Changes | Time from commit to production | Less than one day |
| Change Failure Rate | Share of deployments causing failure | 0-15% |
| Mean Time to Restore (MTTR) | Time to recover from a failed deployment | Less than one hour |

Key insight: speed and stability are NOT a trade-off - elite teams ship more often AND fail less. The metrics move together when the underlying capabilities improve.

## The Capability Clusters (what actually drives the metrics)

1. **Continuous Delivery**: small batches, trunk-based development (short-lived branches), deployment pipeline, automated tests. Drives deploy frequency and lead time.
2. **Architecture**: loosely coupled, testable, independently deployable services. Enables small-batch shipping.
3. **Product & Process**: customer feedback loops, work in small batches, visual management.
4. **Lean & Monitoring**: telemetry on systems, proactive monitoring, limit of WIP.
5. **Culture**: trust, blameless post-mortems, no fear of failure. A team that cannot fail safely cannot ship fast.

## Measuring (honest, no vibes)

- Measure the four metrics on REAL data (deploy logs, commit-to-deploy timestamps, incident records), not surveys of feelings.
- Track a rolling window (e.g. last 30 days) and a trend line - one snapshot lies.
- Label the performer tier (Elite / High / Medium / Low) from the four measured values.

## Improvement Priority (start here)

1. If lead time is days or deploy frequency is weekly: small batches + trunk-based + pipeline automation first.
2. If change failure rate is high: automated tests + staging parity before more frequency.
3. If MTTR is long: rollback automation + monitoring + blameless culture.
4. Never ask a team to deploy more often while their failure rate is high - fix the safety net first.

## Violations (severity)

- **V1 - Metrics without data** (HIGH): 'We ship fast' with no measured lead time. Fix: instrument the pipeline.
- **V2 - Speed over stability** (HIGH): More deploys while failure rate rises. Fix: fix the safety net; the metrics move together.
- **V3 - Long-lived branches** (MEDIUM): Branches that live for weeks inflate lead time and failure rate. Fix: trunk-based, small batches.
- **V4 - Culture of blame** (MEDIUM): No blameless post-mortems -> MTTR and failure rate stay high. Fix: culture capability.
- **V5 - Single snapshot** (LOW): One week of data called a trend. Fix: rolling window + trend.

## Checklist

- [ ] Four metrics measured on real data
- [ ] Rolling window + trend tracked
- [ ] Performer tier labeled honestly
- [ ] Improvement starts from the weakest metric's capability
- [ ] Safety net (tests, parity, rollback) precedes any frequency push

## Verification

Produce a DORA snapshot with the four measured values and a tier label. Run the build gates and require READY_FOR_DEPLOYMENT.
