---
name: designing-distributed-systems
description: Applies Brendan Burns' Designing Distributed Systems to building practical distributed applications with patterns: sidecars, ambassador and adapter containers, replicated and sharded services, leader election, scatter-gather, functions and event-driven designs, and the ownership pattern — patterns that compose on Kubernetes and similar platforms. Use when the user says 'designing distributed systems', 'sidecar', 'ambassador pattern', 'replicated service', 'sharded service', 'leader election', 'scatter gather', 'event driven design', 'Brendan Burns', 'kubernetes patterns', or when building a distributed application from proven patterns.
---

# Designing Distributed Systems (Brendan Burns)

Burns collects the patterns that real distributed systems are built from. This skill applies them as building blocks that compose into a working system.

## Container patterns

- The sidecar extends a container with auxiliary behavior (logging, proxying, config) beside the main process.
- The ambassador pattern fronts a container to normalize external access (proxies, retries, TLS).
- The adapter pattern normalizes output, making diverse containers present a uniform interface.

## Service patterns

- Replicated services scale reads and provide redundancy behind a load balancer.
- Sharded services partition state so each shard is small; the sharding key decides the split.
- Leader election picks one node for work that must not be parallel.

## Coordination patterns

- Scatter-gather fans a request out and merges the answers; the merge step sets the result shape.
- Work queues and event-driven design decouple producers from consumers.
- Ownership: each entity in the system has exactly one owner; ambiguity is a failure.

## Composition

- Patterns compose; a system is a graph of replicated, sharded, coordinated pieces.
- State must live somewhere durable; keep stateless layers in front of stateful cores.
- Design for partial failure at every layer; the platform restarts what it can.

## Pairs with
distributed-systems-concepts-design, cloud-native-patterns, kubernetes-operations, designing-event-driven-systems, agent-arch-system-design
