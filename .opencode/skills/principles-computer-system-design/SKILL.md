---
name: principles-computer-system-design
description: Applies Saltzer & Kaashoek's Principles of Computer System Design to design systems that behave: the fundamental principles (modularity, abstraction, naming, caching, concurrency, persistence), the techniques that implement them (client-server, virtualization, recoverability), and the recurring trade-offs, with a focus on keeping the design simple enough to reason about. Use when the user says 'system design principles', 'modularity', 'abstraction', 'naming', 'caching', 'client server', 'virtualization', 'recoverability', 'Saltzer Kaashoek', 'design for simplicity', or when a system's architecture must be principled, not ad hoc.
---

# Principles of Computer System Design (Saltzer & Kaashoek)

Saltzer & Kaashoek collects the enduring principles behind systems that work, and the trade-offs each implies. This skill applies those principles to any architecture decision.

## Principles over patterns

- Modularity and abstraction hide detail so each part can be reasoned about alone.
- Naming is the glue of systems; every resource needs a name, a lookup, and a revocation path.
- Caching trades correctness cost for speed; the invalidation policy is where the risk lives.

## Concurrency and persistence

- Concurrency multiplies capability and complexity; state the shared invariants before threads touch them.
- Persistence is the memory that outlives a run; durable storage changes what the system can recover.
- Transactions give atomic, durable, isolated units; the guarantees must be explicit.

## Client-server and virtualization

- Client-server separates responsibility across a boundary; the interface is the contract.
- Virtualization multiplexes resources behind a uniform interface; it is the same idea as modularity applied to hardware.
- Recoverability means the system returns to a correct state after failure; design the recovery path early.

## The simplicity discipline

- A system that cannot be understood cannot be made correct; prefer the simple design that meets the requirement.
- Each added mechanism must pay for itself in capability or clarity.
- Document the design trade-offs; the next engineer inherits the decision, not the argument.

## Pairs with
agent-arch-system-design, sicp-abstraction-and-interpretation, zero-trust-modular-decomposer, distributed-systems-concepts-design, tradeoff-and-postmortem-documenter
