---
name: release-it-production-hardening
description: "Applies Michael Nygard's Release It! to make production systems survive their own success and their own failures: stability patterns (Circuit Breaker, Bulkhead, Timeout, Fail Fast, Steady State, Handshaking, Decoupling, Load Shedding), integration point defense, cascading-failure prevention, and the anti-patterns of fragile production (integration points, chain reactions, cascading failures). Ensures an automation or service does not collapse under load spikes, slow dependencies, or partial failures. Use when the user says 'Release It', 'circuit breaker', 'bulkhead', 'fail fast', 'steady state', 'cascading failure', 'stability patterns', 'integration point', 'load shedding', 'Nygard', 'harden production', 'why does my system fall over', or when a workflow must survive real-world chaos. Pairs with: cloud-native-patterns, n8n-error-boundary-architect, rate-limit-and-cost-guard, systems-performance-profiling."
---
# Production Hardening (Release It! - Nygard)

Nygard's core: systems fail in production, and the failures are PREDICTABLE patterns. The goal is stability - a system that keeps serving through load spikes, slow dependencies, and partial failures - through named stability patterns, not hope.

## The Stability Patterns (defense playbook)

### Circuit Breaker
- When a dependency fails repeatedly, OPEN the circuit: stop calling it for a while, serve a fallback, then try a small probe to close it again.
- Rule: never hammer a failing dependency - every call you make to it is a timeout you could spend serving something else.
- n8n: retry-on-fail is NOT a circuit breaker. Use a state node / external circuit that trips and falls back.

### Bulkhead (isolation)
- Partition resources so one tenant/feature cannot starve the rest. Separate thread pools, queues, or workers per consumer.
- Rule: a single misbehaving caller must not exhaust the shared pool.

### Timeout
- Every outbound call has a timeout. An integration that hangs forever is a denial-of-service against your own system.
- Rule: 'no timeout' is not an option; it is a self-inflicted outage.

### Fail Fast
- Fail loudly and immediately when preconditions are not met, so the failure is cheap and obvious - never keep processing on a broken foundation.

### Steady State
- Systems must be leak-free under constant load: no memory/queue/connection growth over time. Monitor for linear growth.

### Handshaking / Decoupling / Load Shedding
- Handshake: verify capacity before sending a big workload.
- Decouple: do not let a batch job block interactive requests (async, queues).
- Load shedding: when overloaded, serve a degraded response (or a 'busy' reply) instead of collapsing.

## The Anti-patterns (what kills production systems)

- **Integration point fragility** (HIGH): External calls that block and hang. Fix: timeout + circuit breaker + fallback.
- **Chain reactions** (HIGH): One failure fans out because every system retries into a congested pool. Fix: circuit breakers + backoff, never synchronized stampedes.
- **Cascading failures** (HIGH): System A's overload passes to B, to C, and back. Fix: bulkheads + load shedding at every hop.
- **Users causing the load** (MEDIUM): Every retry a frustrated user makes multiplies the load. Fix: fast, friendly failure responses; idempotent retries.

## Hardening Checklist (pre-deploy)

- [ ] Every outbound call has a timeout
- [ ] Every integration has a circuit breaker (trip, fallback, probe)
- [ ] Consumers are partitioned (bulkhead) so one tenant cannot starve all
- [ ] Fail-fast guards exist on preconditions
- [ ] Steady-state verified: no linear resource growth under sustained load
- [ ] Load-shedding path exists for overload (degraded response, not death)
- [ ] Retries use backoff; no synchronized retry stampedes

## Violations (severity)

- **V1 - No timeout on an integration** (HIGH): One hang = whole system stalls. Fix: timeout always.
- **V2 - Retry stampede** (HIGH): All callers retry together after a failure. Fix: jittered backoff + circuit breaker.
- **V3 - No circuit breaker** (HIGH): Repeated calls to a dying dependency. Fix: trip and fall back.
- **V4 - Shared pool exhaustion** (HIGH): One tenant's spike starves everyone. Fix: bulkheads.
- **V5 - Unbounded growth** (MEDIUM): Queues/memory grow under steady load. Fix: steady-state checks, bounded queues.
- **V6 - No degraded mode** (MEDIUM): Overload means total failure instead of a busy/deprecated response. Fix: load shedding.

## Verification

Test the failure path: dependency down -> timeout fires -> circuit trips -> fallback serves -> recovery probe closes. Run the build gates and require READY_FOR_DEPLOYMENT.
