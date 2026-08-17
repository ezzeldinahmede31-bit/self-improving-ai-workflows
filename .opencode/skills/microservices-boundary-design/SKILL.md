---
name: microservices-boundary-design
description: "Applies Sam Newman's Building Microservices to split automation and backends into independently deployable services: finding service boundaries by business capability and subdomain (not by team structure or table names), one database per service, owning the deployment pipeline per service, and avoiding the distributed monolith. Honest rule: if you cannot independently deploy it, it is not a microservice. Use when the user says 'microservices', 'service boundary', 'split the monolith', 'distributed monolith', 'one database per service', 'independent deployment', 'Sam Newman', 'decompose this', 'domain-driven split', or when a single big workflow/service should become several. Pairs with: domain-driven-design-strategic, cloud-native-patterns, data-intensive-application-design, devops-handbook-flow."
---
# Microservices Boundary Design (Building Microservices - Newman)

Newman's core: a microservice is a small, autonomous service that works WITHIN a bounded context, owned by one team, independently deployable. Size matters less than INDEPENDENT DEPLOYABILITY and a clean boundary. The distributed monolith is the cardinal sin.

## Finding Boundaries (the right way)

1. **Business capability first** - split by what the business does (orders, customers, shipping), matching DDD bounded contexts.
2. **Subdomain second** - core, supporting, generic subdomains get different service depth.
3. **Data ownership defines the boundary** - each service owns its data; there is ONE database per service. Sharing a DB across services = the death of the boundary.
4. **Deployment independence is the test** - a service is real only if it can be deployed without deploying anything else.
5. **Communication is explicit** - over HTTP/API, async messaging, or events - never by reaching into another service's database.

## Boundary Anti-patterns (severity)

- **A1 - Distributed monolith** (HIGH): Many services that must all be deployed together to work. Fix: merge into fewer real services; independent deployability returns.
- **A2 - Shared database** (HIGH): Two services reading/writing the same tables. Fix: one owner per table; other service uses the API.
- **A3 - Boundary by tech/table name** (HIGH): 'users' service because there is a users table. Fix: boundary by business capability.
- **A4 - Chatty services** (MEDIUM): A call that fans out to dozens of services for one business operation. Fix: co-locate or aggregate at the boundary.
- **A5 - Undefined ownership** (MEDIUM): No clear team/service owns a data domain. Fix: assign explicit ownership.

## Service Design Checklist

- [ ] Each service maps to a business capability or bounded context
- [ ] One database per service; no shared tables
- [ ] Each service is independently deployable (prove it with the pipeline)
- [ ] Cross-service calls are explicit (API/events), never DB access
- [ ] Every service has its own deployment pipeline and rollback
- [ ] Team ownership of each service is explicit

## When NOT to use microservices (honest)

- Small team, small domain, one deployable: a monolith with clean modules is often the RIGHT call. Microservices add operational cost; they buy independent scaling and team autonomy. If neither is needed, do not pay the cost.
- Newman's advice: start as a modular monolith; extract services as the real boundary and deployability need appears.

## Verification

For each claimed service: confirm it deploys independently (pipeline runs standalone) and owns its data wholly. Run the build gates and require READY_FOR_DEPLOYMENT.
