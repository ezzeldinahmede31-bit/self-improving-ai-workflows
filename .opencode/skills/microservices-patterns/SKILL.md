---
name: microservices-patterns
description: Applies Chris Richardson's Microservices Patterns to design, build, and operate microservices with proven solutions to the hard problems — service decomposition, inter-service communication, transaction management via sagas and compensating actions, the database-per-service model with eventual consistency, API gateway, service discovery, configuration management, observability, and deployment patterns (blue-green, canary, strangler). Use when the user says 'microservices', 'saga', 'API gateway', 'service discovery', 'database per service', 'eventual consistency', 'strangler fig', 'Richardson microservices', 'circuit breaker', 'config server', 'service mesh', or when splitting a system into independently deployable services and needs the pattern for each pain point. Pairs with: microservices-boundary-design, monolith-to-microservices, cloud-native-patterns, api-design-patterns, designing-event-driven-systems.
---
# Microservices Patterns (Richardson)

Transfers Chris Richardson's pattern catalog so every hard microservice decision — transactions, data ownership, discovery, gateway, deployment — has a proven answer instead of a hand-rolled guess.

## When to use
- Designing a new microservice system or decomposing a monolith into services.
- Solving the classic pain points: cross-service transactions, service discovery, API routing, config, observability.
- Choosing deployment and rollback strategy per service.

## The core decisions
1. Decompose by business capability or subdomain; each service owns its data (database-per-service).
2. Communicate via API or messaging; do not share a database across services.
3. Handle multi-service transactions with a saga (choreographed or orchestrated) and compensating actions, accepting eventual consistency instead of 2PC.
4. Front the services with an API gateway that routes, authenticates, and aggregates; register services with a discovery mechanism so instances come and go safely.
5. Centralize configuration and make it environment-aware; push observability (logs, metrics, traces) as a first-class concern.

## Deployment and resilience
- Deploy each service independently with blue-green or canary releases and a fast rollback.
- Protect inter-service calls with timeouts, retries, and circuit breakers so one service's failure does not cascade.

## Verification discipline
- Prove a saga's compensating path with a fault-injection test, not just the happy path.
- Test discovery failover: kill an instance and confirm traffic reroutes.
- Monitor per-service SLOs and trace the full request path across services.

## Pairs with
microservices-boundary-design, monolith-to-microservices, cloud-native-patterns, api-design-patterns, designing-event-driven-systems.