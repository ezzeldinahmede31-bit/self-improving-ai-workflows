---
name: production-microservices-standards
description: "Run microservices as a standardized fleet: paved roads, contracts, testing, rollout. Use when the user says 'microservices standards', 'service maturity', 'paved road', 'service template', 'microservices pitfalls', 'standardize services', or needs 50 services to behave like one system."
---

# Production Microservices Standards

Distilled from Fowler *Production-Ready Microservices* (standardization
across an org), Smith *Microservices AntiPatterns and Pitfalls*, Balalaie
*Tao of Microservices*, Newman *Building Microservices* + *Monolith to
Microservices*. One bespoke snowflake service is charming; fifty is an
outage maze.

## The standard (every service, no exceptions)

1. **Paved road template.** New service in one command: CI pipeline,
   Dockerfile, health/readiness probes, structured logging, trace
   propagation, metrics, dashboards, alerts, runbook skeleton, cost
   tags. Custom setups need written justification.
2. **Contract discipline.** Versioned APIs/events, backward-compatible
   changes only, consumer-driven contract tests, schema registry for
   events. Breaking change = new version + migration window, never a
   surprise. Pairs with `api-versioning-compatibility`.
3. **Data ownership.** One service owns each entity; others read via
   API or replicated events, never the DB. Shared database = distributed
   monolith with extra latency. Pairs with `monolith-database-decomposition`.
4. **Testing ladder.** Unit -> contract -> component-in-container ->
   staging journey tests -> prod canary analysis. No service skips a
   rung because it is 'too small'.
5. **Rollout safety.** Blue-green or canary with automatic rollback on
   SLO burn, feature flags for behavior, DB migrations expand-then-
   contract. Deploy Friday only when the ladder above is green.
6. **Antipattern watch.** Distributed monolith (chatty sync calls),
   shared libraries as coupling vectors, mega-service hiding the
   monolith, inconsistent timeouts/retries per service (standardize
   via `distributed-systems-field-manual`), missing ownership
   (every service names an owner + on-call).

## Verification

Fleet ships with: template adoption %, contract-test coverage, data
ownership map, testing ladder evidence, canary + auto-rollback proof,
antipattern sweep with owners per finding. Exceptions get expiry dates.

## Pairs with

- `microservices-boundary-design` (boundaries),
  `monolith-to-microservices` (extraction),
  `monolith-database-decomposition` (data ownership),
  `distributed-systems-field-manual` (standard resilience),
  `observability-engineering-design` (standard telemetry),
  `finops-cost-architecture` (per-service cost),
  `api-versioning-compatibility` (contracts).
