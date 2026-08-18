---
name: integration-architecture-frameworks
description: Applies the standard integration-architecture frameworks (SOA Reference Architecture, TOGAF-style integration, EAI/ESB patterns, and the integration capability model) to design a coherent integration backbone — capability tiers (connectivity, transformation, routing, orchestration, security, governance), canonical data models, and the decision rules that choose ESB, microservices, event-driven, or API-led integration for a given flow. Use when the user says 'integration architecture', 'SOA reference architecture', 'TOGAF integration', 'canonical model', 'integration governance', 'API-led integration', 'integration capability', 'enterprise architecture integration', or when planning the overall integration strategy for an organization rather than a single flow. Pairs with: enterprise-integration-patterns, enterprise-service-bus, api-integration, agent-arch-system-design, data-intensive-application-design.
---
# Integration Architecture Frameworks

Transfers the enterprise integration-architecture frameworks (SOA RA, TOGAF-style, EAI/ESB, API-led) so an organization designs one coherent integration backbone instead of an ad-hoc pile of point-to-point flows.

## When to use
- Planning the overall integration strategy across many applications.
- Choosing between ESB, API-led, event-driven, and microservices integration per flow.
- Setting governance, canonical models, and security for all integrations.

## The capability model
1. Define integration capabilities explicitly: connectivity, transformation, routing, orchestration, security, and governance — each is a layer with its own tools and standards.
2. Adopt a canonical data model (a shared vocabulary and format) so systems do not translate pairwise; systems map to the canonical form once.
3. Route every flow through a decision rule: request-reply vs event, batch vs real-time, central broker vs direct, which determines the style.
4. Govern by contract: register every integration, version it, and review changes like code.

## Style selection
- API-led: expose reusable, business-capped APIs over systems; best for request-reply with many consumers.
- ESB/mediator: central routing and transformation; best for many-to-many protocol/schema mismatch.
- Event-driven: facts published to a backbone; best for decoupled real-time reaction.
- Microservices: small owned services with direct calls; best where ownership and independent deployability dominate.

## Verification discipline
- Prove the canonical model round-trips: map a message in and out of two systems and compare fields.
- Track integration inventory and alert on undocumented, point-to-point flows.
- Test governance by attempting a contract change and confirming the review gate blocks it.

## Pairs with
enterprise-integration-patterns, enterprise-service-bus, api-integration, agent-arch-system-design, data-intensive-application-design.