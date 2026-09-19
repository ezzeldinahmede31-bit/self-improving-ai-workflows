---
name: architecture-primitives
description: "Catalog of reusable architectural primitives — boundaries, contracts, state machines, queues, caches, consistency models, and more. For each: what it is, when it's right, when it's WRONG. Use when selecting patterns for a design or evaluating whether a pattern fits."
---

# Architecture Primitives

An architect who knows many patterns is less useful than one who knows when each pattern is wrong.

For each primitive: what it is, when to use it, and when it will hurt you.

---

## Boundaries and Ownership

**What it is.** Drawing lines between components so each has a clear owner, clear interface, and can evolve independently.

**When it's right.** When different teams own different parts. When components have different scaling, deployment, or reliability requirements. When you need to limit blast radius.

**When it's wrong.** When the "boundary" creates more cross-boundary coordination than it prevents. When data that changes together is split across boundaries. When the team is small enough that communication overhead exceeds boundary value.

## Contracts and Interfaces

**What it is.** Explicit agreements between components about what they provide and expect — API schemas, message formats, SLAs, error codes.

**When it's right.** At every boundary. Between any components that evolve independently. When multiple consumers depend on the same provider.

**When it's wrong.** Premature contracts between components that are still being designed together. Overly rigid contracts that prevent necessary evolution. Contracts without versioning strategy.

## Source of Truth

**What it is.** For every piece of state, exactly one system is authoritative. All others are caches, replicas, or derived views.

**When it's right.** Always. Every system should be able to answer "where is the source of truth for X?"

**When it's wrong.** Never wrong as a concept — but wrong when applied as "one database for everything." Different data has different truth owners.

## Synchronous vs. Asynchronous Communication

**What it is.** Sync: caller waits for response. Async: caller sends message and continues.

**When sync is right.** When the caller genuinely cannot proceed without the response. User-facing request/response flows. Reads that must be consistent.

**When sync is wrong.** When the caller doesn't need the result to continue. When the called service is slow or unreliable. When you're creating temporal coupling between services that don't need it.

**When async is right.** When work can be deferred. When you need to absorb load spikes. When producer and consumer should be independently deployable and scalable.

**When async is wrong.** When you need an immediate, consistent response. When the added complexity of message delivery, ordering, and failure handling exceeds the benefit.

## State Machines

**What it is.** Modeling entities as having explicit states with defined transitions. An order is "placed → confirmed → shipped → delivered," not a bag of boolean flags.

**When it's right.** When an entity has a lifecycle with distinct phases. When invalid state transitions are a real failure mode. When you need to audit or replay state changes.

**When it's wrong.** When the entity's behavior doesn't meaningfully vary by state. When the state space is too large to enumerate. When you're adding a state machine to something that is really just a CRUD record.

## Queues and Buffering

**What it is.** Decoupling producers from consumers with an intermediate buffer. Smooths out rate differences and absorbs spikes.

**When it's right.** When producer rate exceeds consumer rate temporarily. When consumer failures shouldn't block producers. When you need to prioritize or reorder work.

**When it's wrong.** When the queue grows unboundedly (you've moved the problem, not solved it). When end-to-end latency matters and the queue adds unacceptable delay. When queue failure becomes a single point of failure worse than direct coupling.

## Caches

**What it is.** Storing computed or fetched results closer to the consumer to avoid repeated expensive operations.

**When it's right.** When reads vastly outnumber writes. When the source is slow and staleness is acceptable. When the working set fits in memory.

**When it's wrong.** When cache invalidation is harder than the performance problem it solves. When data changes frequently and staleness is unacceptable. When the cache becomes the de facto source of truth (and you lose the actual source). When you're caching to hide a fixable performance problem.

## Idempotency

**What it is.** Operations that produce the same result whether executed once or multiple times. "Set X to 5" is idempotent; "increment X" is not.

**When it's right.** Any operation that might be retried — API endpoints, message consumers, database migrations, deployment scripts. Critical for at-least-once delivery systems.

**When it's wrong.** Rarely wrong in principle, but the implementation cost varies. Adding idempotency keys to every endpoint when retries never happen is over-engineering.

## Retries and Backoff

**What it is.** Automatically retrying failed operations, with increasing delays between attempts to avoid thundering herds.

**When it's right.** For transient failures (network blips, temporary overload, lock contention). With idempotent operations. With jitter to prevent synchronized retry storms.

**When it's wrong.** For permanent failures (bad input, missing permissions, business rule violations). Without a circuit breaker — retrying a dead service at high rate makes everything worse. Without idempotency — retries can cause duplicate side effects.

## Backpressure

**What it is.** Signaling upstream when downstream is overloaded, so the system slows intake rather than dropping or crashing.

**When it's right.** In any pipeline where producers can outpace consumers. When dropping work is worse than slowing down. When you need graceful degradation under load.

**When it's wrong.** When the producer cannot slow down (external events, user requests that must be accepted). When backpressure propagates to the end user as unacceptable latency. In these cases, you need buffering or load shedding instead.

## Consistency Models

**What it is.** The guarantees a system provides about when writes become visible to reads. Strong consistency: reads always see the latest write. Eventual consistency: reads will eventually see the write.

**When strong consistency is right.** Financial transactions, inventory counts, anything where acting on stale data causes real harm.

**When eventual consistency is right.** Social feeds, analytics, search indexes, caches — where temporary staleness is tolerable and the performance/availability benefits are significant.

**The real question.** Not "which model?" but "which data needs which model?" Most systems need both.

## Observability

**What it is.** The ability to understand a system's internal state from its external outputs — logs, metrics, traces, health checks.

**When it's right.** Always. A system you cannot observe is a system you cannot operate.

**When it's wrong.** When observability becomes so expensive (storage, performance overhead, cognitive load) that it degrades the system it monitors. When you're collecting data nobody looks at. When alerting is so noisy that real signals are lost.

## Blast Radius Isolation

**What it is.** Designing so that failures in one component don't cascade to others. Bulkheads, circuit breakers, separate resource pools, failure domains.

**When it's right.** Between components with different reliability requirements. Around any component that depends on an external service. Around any component with a history of failures.

**When it's wrong.** When the isolation boundaries add more complexity than the failures they prevent. When the components are so tightly coupled that isolating them is pretending they're independent when they're not.
