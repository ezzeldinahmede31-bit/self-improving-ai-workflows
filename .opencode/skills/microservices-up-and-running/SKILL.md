---
name: microservices-up-and-running
description: Applies Mitra and Nadareishvili's Microservices Up and Running to design small, independently deployable services: identify service boundaries by business capability, design contracts first, own the data behind each service, and evolve a monolith with the strangler pattern. Covers the operational side too - observability, deployment pipelines, and failure isolation. Use when the user says 'design microservices', 'split this into services', or 'how should services talk to each other'.
---
# microservices-up-and-running

Mitra and Nadareishvili teach microservices as a strategy, not a toolkit: a service is a small, focused unit that can be built, deployed, and scaled on its own. Use this skill to decide whether microservices fit, find honest boundaries, and operate the result without building a distributed monolith.

## Core principles
- Start with a monolith and a clear seam; microservices are justified by independent deployability and team ownership, not by fashion.
- Each service owns one business capability and the data that capability needs.
- A service boundary is a contract, so the interface (API, events, schema) is the first thing designed.
- Services communicate over well-defined contracts; internal implementation details never leak across the boundary.
- Failure is local: a slow or broken upstream must degrade gracefully, never take the whole system down.
- Every service needs its own deployment pipeline, observability, and runbook from day one.

## Key patterns
- Capability-first decomposition: name the business capability, then give it a service, never the reverse.
- Contract-first design: document the API or event schema before writing implementation code.
- Strangler pattern: incrementally replace monolith pieces service by service, routing traffic as each piece lands.
- Choreography or orchestration for cross-service flows, chosen deliberately with timeouts and compensation in mind.
- Database per service, with the shared-database hazards (joins, transactions, locking) treated as a migration risk.
- Service mesh or gateway only when cross-cutting concerns justify the extra moving parts.

## Applying this to n8n/automation/code
- Model each n8n subworkflow as a microservice: a typed contract (Define Below inputs), one responsibility, and its own error boundary.
- Run shared helpers as standalone subworkflows consumed by many flows, so a change lands in one place.
- Keep cross-workflow flows event-driven: emit facts into a queue and let subscribers react, instead of chaining deep call trees.
- Give every main workflow a health check and a retry/timeout posture so one slow execution cannot stall others.
- Version contracts when a subworkflow input changes shape, so old callers keep working.

## Hard rules
- Never share a database schema across services without an explicit ownership decision.
- Never let a service reach into another service's internal storage.
- Always define the contract before wiring the implementation.
- Never deploy a service without monitoring, alerting, and a rollback path.

## Pairs with
microservices-boundary-design, monolith-to-microservices, cloud-native-patterns, enterprise-integration-patterns, agent-arch-system-design
