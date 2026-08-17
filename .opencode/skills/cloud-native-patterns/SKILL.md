---
name: cloud-native-patterns
description: "Applies Cornelia Davis' Cloud Native Patterns to design applications that fully exploit cloud environments: stateless and stateful design, event-driven architecture, messaging, elasticity and resilience patterns (circuit breaker, retries, backoff, graceful degradation), observability, and the organizational/technical alignment the cloud demands. Use when the user says 'cloud native', 'design for the cloud', 'event-driven', 'resilience patterns', 'circuit breaker', 'graceful degradation', 'elastic scaling', '12-factor', 'stateful in the cloud', 'messaging patterns', 'cloud architecture', or when an application must behave well under load spikes and partial failures. Pairs with: agent-arch-system-design, n8n-subworkflow-modularizer, kubernetes-operations, evolutionary-architecture."
---

# Cloud Native Patterns

Davis' book: cloud environments give you elasticity (scale on demand), but that only
helps if the application is designed for it — disposable instances, event-driven
wiring, and resilience as a first-class property.

## When to use

- Designing a new service for a cloud platform.
- Refactoring a monolith into cloud-friendly pieces.
- Reviewing whether an application will actually survive a scale-out or a node loss.

## The patterns

### 1. Disposable, stateless-first
- Design instances as cattle: no unique state on a single instance. Keep sessions
  and durable data outside the process (DB, cache, object store).
- Where state must live, make it explicit and externalized (see
  `state-machine-persistence`), so any instance can serve any request.

### 2. Event-driven wiring
- Components communicate through events/messages rather than direct synchronous
  calls where decoupling pays: producers publish, consumers subscribe, the broker
  absorbs spikes.
- Choose the model deliberately: queues (one consumer per message) vs topics
  (fan-out), and exactly-once vs at-least-once delivery semantics for each link.

### 3. Elasticity
- Scale horizontally on measured demand with a safe min/max and cooldowns; design
  for load that appears and disappears quickly.
- Avoid anything that breaks under scale-out (in-process locks, sticky single-writer
  assumptions, local disk state).

### 4. Resilience patterns
- **Timeouts + bounded retries with exponential backoff** on every outbound call.
- **Circuit breaker**: stop hammering a failing dependency, fail fast, and recover
  gracefully.
- **Bulkheads**: isolate failure domains so one dependency's outage does not
  cascade.
- **Graceful degradation**: when a dependency is down, serve a reduced response
  instead of an error — never a full outage for a partial cause.
- **Health endpoints + liveness/readiness**: so the orchestrator knows when to
  restart or stop sending traffic.

### 5. Observability
- Logs, structured metrics, and traces from every component; correlate requests
  across services (correlation ids).
- Alert on symptoms users feel (error rate, latency), not just machine health.

## Verification
- Kill one instance: traffic keeps flowing (the disposal test).
- Point a dependency at a failing state: the circuit breaker opens and the system
  degrades, not crashes.
- Double the load: the system scales out to the target and back without manual
  intervention.

## Pairs with
- `agent-arch-system-design` — the system-level architecture.
- `n8n-subworkflow-modularizer` — the same modularity discipline for workflows.
- `kubernetes-operations` — the runtime that executes these patterns.
- `evolutionary-architecture` — fitness functions that guard the patterns.