---
name: ddd-tactical-aggregates
description: "Applies Vaughn Vernon's Implementing Domain-Driven Design tactical patterns to code and n8n automation: Aggregates with invariant-enforcing consistency boundaries, Value Objects over Entity fetishism, Domain Events for decoupled side effects, Repositories as collection metaphors, and Factories for complex construction. Guards against the classic aggregate pitfalls (god aggregates, lazy loading across boundaries, transactional overreach). Use when the user says 'aggregate', 'value object', 'domain event', 'repository', 'factory', 'invariant', 'tactical DDD', 'Vernon', 'consistency boundary', 'write a domain model', or when state mutations must stay consistent. Pairs with: domain-driven-design-strategic, domain-modeling-functional, state-machine-persistence, database-internals-engines."
---
# Tactical DDD (Implementing Domain-Driven Design - Vernon)

Vaughn Vernon's tactical patterns turn strategic DDD into concrete code shapes. The center of gravity is the AGGREGATE: a cluster of objects treated as one unit with one transaction boundary.

## The Aggregate Rules (Vernon's 4 rules)

1. **Protect invariants inside the boundary** - the aggregate alone is responsible for its internal consistency.
2. **Reference other aggregates only by identity (ID)** - never hold a direct object reference to another aggregate.
3. **Update other aggregates via events or asynchronously** - do not mutate another aggregate's state synchronously.
4. **One aggregate per transaction** - a transaction commits one aggregate's state. 'Two aggregates in one transaction' is a modeling error.

## Tactical Element Decision Guide

| Element | When to use | Anti-pattern to avoid |
|---|---|---|
| Value Object | Immutable attribute cluster with equality by value (Money{amount,currency}) | Mutable 'entity-ifying' a value |
| Entity | Has identity and a lifecycle through state changes | Adding identity where only value matters |
| Aggregate | A consistency boundary with invariants | The 'god aggregate' holding the whole model |
| Domain Event | A fact that happened, past tense, published for decoupling | Firing events for every getter call |
| Repository | A collection metaphor for retrieving aggregates | Repository with query methods that leak storage |
| Factory | Complex construction of aggregates | Constructors with ten positional args |

## Aggregate Design Checklist

- [ ] Invariants are named and enforced inside the aggregate, not by callers
- [ ] The aggregate exposes behavior (methods), not naked state
- [ ] Cross-aggregate references are by ID only
- [ ] Side effects on other aggregates go through domain events, not synchronous mutation
- [ ] Each transaction updates exactly one aggregate
- [ ] Value Objects are immutable and compared by value
- [ ] Event names are past tense and business-meaningful ('OrderPlaced', never 'DataChanged')

## Common Pitfalls (severity)

- **P1 - God Aggregate** (HIGH): One aggregate owns everything and every transaction touches it. Fix: split by true invariants.
- **P2 - Direct cross-aggregate reference** (HIGH): Holding an object ref to another aggregate. Fix: reference by ID.
- **P3 - Transaction overreach** (HIGH): Updating several aggregates in one transaction 'for safety'. Fix: one aggregate per transaction + events.
- **P4 - Anemic model** (MEDIUM): All data, no behavior - services do everything. Fix: move behavior into the aggregate.
- **P5 - Lazy loading across boundary** (MEDIUM): Aggregate pulls in another aggregate's data on access. Fix: load by ID, in the calling context.
- **P6 - Entity for a value** (LOW): Giving an ID to something that is really a value. Fix: make it a Value Object.

## Verification

Verify aggregates by writing a test that asserts invariants hold after every operation, and confirm the workflow's write paths touch one aggregate per transaction. Run the standard build gates and require READY_FOR_DEPLOYMENT.
