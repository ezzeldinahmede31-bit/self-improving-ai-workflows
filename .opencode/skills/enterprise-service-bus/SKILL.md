---
name: enterprise-service-bus
description: Applies David Chappell's Enterprise Service Bus to integrate heterogeneous systems with a mediation layer — routing, transformation, protocol bridging, and reliable messaging in one broker — rather than point-to-point spaghetti. Covers when an ESB earns its keep (many systems, many protocols, evolving contracts), when it becomes an anti-pattern (a brittle hub), and how to build the bus with message queues, service containers, and monitoring. Use when the user says 'enterprise service bus', 'ESB', 'message broker', 'integration hub', 'routing and transformation', 'protocol bridging', 'system integration', 'Chappell ESB', 'soa integration', or when connecting many legacy and modern systems and needs a central mediation strategy instead of direct calls. Pairs with: enterprise-integration-patterns, integration-architecture-frameworks, api-integration, webhook-automation, n8n-subworkflow-modularizer, designing-event-driven-systems.
---
# Enterprise Service Bus (Chappell)

Transfers David Chappell's ESB blueprint so integration between heterogeneous systems runs through a mediation layer that routes, transforms, and bridges — while flagging the hub anti-pattern honestly.

## When to use
- Integrating many systems that speak different protocols and schemas.
- Centralizing routing, transformation, and reliability instead of hand-wiring every pair of systems.
- Deciding whether a broker is worth the operational cost versus direct integration.

## The bus pattern
1. Mediate, do not just relay: the bus owns routing, message transformation, and protocol conversion so endpoints stay decoupled.
2. Model every integration as a message flow on the bus, with a contract for each service endpoint.
3. Use reliable, async messaging (queues, topics) where delivery matters; sync request-reply only when the interaction demands it.
4. Keep services unaware of each other; the bus changes routes without touching endpoints.

## When an ESB hurts
- One hub is a single point of failure and a scalability ceiling; if a bus becomes a bottleneck or a god-object of tangled rules, decompose it or move to direct, contract-first integration.
- Small integrations with two stable systems do not need a bus; use it when mediation genuinely multiplies value.

## Verification discipline
- Prove each route end-to-end with sample messages before going live.
- Monitor queue depth, dead-letter rate, and per-route latency; a silent drop is the worst failure mode.
- Keep an integration contract registry and test changes against it.

## Pairs with
enterprise-integration-patterns, integration-architecture-frameworks, api-integration, webhook-automation, n8n-subworkflow-modularizer, designing-event-driven-systems.