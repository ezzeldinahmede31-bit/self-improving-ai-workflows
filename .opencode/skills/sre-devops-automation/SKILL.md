---
name: sre-devops-automation
description: Applies Google's Site Reliability Engineering (SRE) and The DevOps Handbook to automation and services: define SLIs (real measured indicators), set SLOs (targets), manage an error budget (the allowable downtime that balances reliability vs feature velocity), eliminate toil through automation, run blameless post-mortems, and use monitoring with meaningful alerts (no alert fatigue). Encodes the SRE mindset: reliability is a product decision with a budget, not an engineering aspiration. DevOps adds: the Three Ways (flow, feedback, continual learning), value stream mapping, deployment pipeline automation, small-batch deployments with fast rollback, monitoring and alerting as feedback, and the cultural practices that make automation stick. Use when the user says 'SRE', 'SLI', 'SLO', 'error budget', 'toil', 'blameless post-mortem', 'alert fatigue', 'reliability target', 'nine nines', 'monitoring strategy', 'site reliability', 'devops', 'continuous delivery', 'deployment pipeline', 'value stream', 'reduce lead time', 'small batches', 'canary deploy', 'feature flags', 'monitoring feedback', 'blameless postmortem', 'DevOps Handbook', 'three ways', or when delivery is slow or broken by hand-offs. Pairs with: data-intensive-application-design, continuous-delivery-pipeline, release-it-production-hardening, root-cause-post-mortem-analyzer.
---

# SRE + DevOps Automation Skill

## Core Philosophy: Two Sides of One Coin

> **SRE** = Concrete implementation of **DevOps** philosophy
> - DevOps: "What" (principles, culture, CALMS)
> - SRE: "How" (specific practices, error budgets, SLOs)

Both share: measurement, collaboration, automation, blameless culture.

---

## SRE: The Google Way (Ch 1-10 SRE Book)

### Tenet 1: Operations is a Software Problem
- Hire software engineers for operations
- 50% cap on operational work (tickets, on-call, manual tasks)
- Remaining 50% = development (automation, tooling, reliability improvements)
- Goal: systems that are **automatic**, not just automated

### Tenet 2: SLOs & Error Budgets

| Concept | Definition | Example |
|---------|------------|---------|
| **SLI** | Service Level Indicator — measured behavior | Request latency < 200ms |
| **SLO** | Service Level Objective — target for SLI | 99% of requests < 200ms over 30 days |
| **Error Budget** | 1 - SLO = allowable failure | 1% error budget = 7.2 hrs downtime/month |

**Decision rule**: Error budget consumed → freeze feature releases, invest in reliability.

### Tenet 3: Eliminate Toil
**Toil** = manual, repetitive, automatable, produces no enduring value, scales linearly with service.

| Toil | Not Toil |
|------|----------|
| Manual deployments | Designing deployment automation |
| Ticket-driven restarts | Building self-healing systems |
| Log grep for alerts | Writing alerting rules |

**Target**: < 2 events per 8-12hr on-call shift.

### Tenet 4: Monitoring & Alerting

**Golden Signals** (must monitor):
1. **Latency** — time to service request
2. **Traffic** — requests/sec, active users
3. **Errors** — rate of failed requests
4. **Saturation** — resource utilization (% capacity)

**Alerting principles**:
- Alert on **symptoms** (user-visible), not causes
- No human interpretation needed — software decides
- Route to human only when action required
- Page fatigue = broken alerting

### Tenet 5: Incident Response & Postmortems

| Phase | SRE Practice |
|-------|--------------|
| **Detection** | Monitoring → alert → page |
| **Response** | MTTR focus; runbook-driven |
| **Resolution** | Restore service first, root-cause later |
| **Postmortem** | **Blameless** — what happened, why, how prevent; assign actions |

**Postmortem for all significant incidents** (even non-paging ones = monitoring gaps).

### Tenet 6: Change Management
- Progressive rollouts (canary, blue-green)
- Fast rollback (< 5 min)
- Change approval = automated gates, not human gates

### Tenet 7: Capacity Planning
- Demand forecasting + provisioning headroom
- Performance = capacity at target latency
- Efficiency = cost per unit of work

---

## DevOps: The Three Ways (The DevOps Handbook)

### First Way: Flow (Left to Right)
| Principle | Practice |
|-----------|----------|
| **Small batches** | Single-piece flow, limit WIP |
| **Reduce lead time** | Commit → production in minutes |
| **Quality at source** | Stop the line on defects |
| **Value stream mapping** | Visualize wait vs active time |

**Goal**: Decrease time to production while increasing quality/reliability.

### Second Way: Feedback (Right to Left)
| Principle | Practice |
|-----------|----------|
| **Fast feedback** | Automated tests, telemetry everywhere |
| **Telemetry** | System-level + usage-level + business-level |
| **Swarm problems** | Cross-team collaboration on incidents |
| **Embed knowledge** | Fix process, not just symptom |

### Third Way: Continual Learning
| Principle | Practice |
|-----------|----------|
| **Experiment** | Hypothesis → measure → learn |
| **Cross-training** | Developers learn ops, ops learn dev |
| **Psychological safety** | Blameless culture, learning from failure |
| **Generalists over specialists** | T-shaped skills |

---

## Unified Automation Practices

### Deployment Pipeline (Both)
```
Commit → Build → Unit Test → Integration Test → Staging → Canary → Production
              ↓               ↓                    ↓
           Quality Gates  Quality Gates        Quality Gates
```

### Monitoring Stack (Both)
| Layer | What | Tools |
|-------|------|-------|
| **Infrastructure** | CPU, memory, disk, network | Prometheus, node_exporter |
| **Application** | Latency, errors, throughput | OpenTelemetry, APM |
| **Business** | Conversions, revenue, active users | Custom, BI |
| **SLO** | Error budget burn rate | Custom, SLO burn alerts |

### Incident Response (Both)
1. **Detect** — automated alerting on SLO breach
2. **Triage** — severity, impact, owner
3. **Resolve** — runbook + expertise
4. **Learn** — blameless postmortem → action items → automation

---

## Decision Checklist for Any Automation

Before automating, verify:
1. **SLI defined** for the service being automated?
2. **SLO agreed** with stakeholders (not "100% uptime")?
3. **Error budget** tracked and visible?
4. **Toil identified** and prioritized for elimination?
4. **Monitoring** covers golden signals?
5. **Alerting** on symptoms, no human interpretation?
6. **Runbooks** exist for common failures?
7. **Postmortem process** established and followed?
8. **Deployment** automated with progressive rollout?
9. **Rollback** tested and < 5 minutes?
10. **Value stream** mapped — wait time vs active time known?

---

## Anti-Patterns to Avoid

- ❌ "We need 99.999% availability" (no error budget = no feature velocity)
- ❌ Alerting on CPU > 80% (cause, not symptom)
- ❌ Manual runbooks that aren't automated
- ❌ Postmortems that assign blame ("who broke it")
- ❌ Deployments requiring manual approval gates
- ❌ No monitoring on business metrics
- ❌ Treating SRE as "ops with a fancy title"
- ❌ DevOps = "Devs do ops" without platform support

---

## Trigger Phrases

`SRE`, `SLI`, `SLO`, `error budget`, `toil`, `blameless post-mortem`, `alert fatigue`, `reliability target`, `nine nines`, `monitoring strategy`, `site reliability`, `devops`, `continuous delivery`, `deployment pipeline`, `value stream`, `reduce lead time`, `small batches`, `canary deploy`, `feature flags`, `monitoring feedback`, `blameless postmortem`, `DevOps Handbook`, `three ways`

---

## Pairings

- `data-intensive-application-design` — reliability at data layer
- `continuous-delivery-pipeline` — deployment automation
- `release-it-production-hardening` — stability patterns
- `root-cause-post-mortem-analyzer` — incident analysis