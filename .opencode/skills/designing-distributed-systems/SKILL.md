---
name: designing-distributed-systems
description: Applies Brendan Burns' Designing Distributed Systems to building practical distributed applications with patterns: sidecars, ambassador and adapter containers, replicated and sharded services, leader election, scatter-gather, functions and event-driven designs, and the ownership pattern — patterns that compose on Kubernetes and similar platforms. Use when the user says 'designing distributed systems', 'sidecar', 'ambassador pattern', 'replicated service', 'sharded service', 'leader election', 'scatter gather', 'event driven design', 'Brendan Burns', 'kubernetes patterns', or when building a distributed application from proven patterns. Pairs with: enterprise-integration-patterns, cloud-native-patterns, distributed-systems-concepts-design, kubernetes-operations, streaming-systems-akidau.
---

# Designing Distributed Systems (Brendan Burns) Skill

## Core Philosophy: Patterns Over Diagrams

> "A distributed system is easy to reduce to boxes and arrows and lose the point." — Burns builds from **composable patterns** with known costs, not abstract diagrams.

**Three Pattern Categories:**
1. **Single-Node** (container composition): Sidecar, Ambassador, Adapter
2. **Multi-Node Serving**: Replicated, Sharded, Scatter/Gather
3. **Batch/Event**: Work Queues, Event-Driven, FaaS, Ownership Election

---

## Single-Node Patterns (Container Composition)

| Pattern | Structure | Purpose | When to Use |
|---------|-----------|---------|-------------|
| **Sidecar** | App + helper in same Pod | Cross-cutting concerns (logging, metrics, TLS, config) | Extend app without code changes |
| **Ambassador** | App + proxy in same Pod | Service mesh integration, SSL termination, retries | Network-level concerns |
| **Adapter** | App + transformer in same Pod | Standardize output format (legacy → standard) | Interface normalization |

**Key Principle**: Each container has single responsibility; composition = reuse.

---

## Multi-Node Serving Patterns

### Replicated Load-Balanced Services (Baseline)
```
Client → Load Balancer → [Instance 1, Instance 2, Instance N]
```
- **Stateless** required (state external: DB, cache, object store)
- **Horizontal scaling**: Add replicas for throughput
- **Health checks**: Liveness (restart) + Readiness (traffic)
- **Rolling updates**: maxSurge / maxUnavailable

### Sharded Services (Data/Traffic Partitioning)
```
Client → Router (shard key) → [Shard 1, Shard 2, Shard N]
```
- **Sharding key**: User ID, tenant, geographic region
- **Consistent hashing** for minimal reshuffle on scale
- **Challenges**: Cross-shard queries, rebalancing, hot shards
- **When**: Single node can't hold data or handle request rate

### Scatter/Gather (Parallel Query Fan-out)
```
Client → Scatter → [Worker 1, Worker 2, ...] → Gather → Aggregate → Client
```
- **Use case**: Search, analytics, fan-out to multiple backends
- **Latency**: max(worker_latencies) + aggregation
- **Timeouts**: Critical — slowest worker bounds response
- **Partial failure**: Return partial results with metadata

---

## Batch & Event-Driven Patterns

### Work Queue (Producer-Consumer)
```
Producer → Queue → [Worker 1, Worker 2, ...] → Result Store
```
- **Queue smooths**: Different rates between stages
- **Workers scale independently** of producers
- **Patterns**: Task queue, priority queue, delayed queue
- **Exactly-once**: Idempotency keys + deduplication

### Event-Driven Workflows (Pub/Sub)
```
Publisher → Topic → [Subscriber A, Subscriber B, ...]
```
- **Decoupled**: Publishers don't know subscribers
- **At-least-once** default; exactly-once needs idempotency
- **Event schema**: Versioned, backward compatible
- **DLQ**: Dead letter queue for failed processing

### Function-as-a-Service (FaaS)
```
Event → Trigger → Function (stateless, short-lived) → Response
```
- **Event sources**: HTTP, queue, schedule, DB change, storage
- **Cold start**: Latency penalty on first invoke
- **Limits**: Time (15min), memory, payload size
- **Use case**: Sporadic, event-driven, variable load

---

## Coordination & Ownership

### Leader Election
```
[Candidate 1, Candidate 2, ...] → etcd/ZooKeeper → Leader + Followers
```
- **Lease-based**: Leader renews TTL; expiry = new election
- **Use case**: Single writer, coordinator, scheduler
- **Split-brain prevention**: Quorum required (Raft/Paxos)

### Distributed Locks
```
Client → Lock Service (etcd/Consul) → Acquire/Release
```
- **TTL + renewal** prevents deadlock on crash
- **Fencing tokens** for storage-level protection

---

## Team Responsibility Model

| Component | Owning Team | On-Call | SLA |
|-----------|-------------|---------|-----|
| Auth Service | Identity Team | Identity Team | 99.9% |
| Payment API | Payments Team | Payments Team | 99.99% |
| Search Index | Search Team | Search Team | 99.5% |

**Rule**: At 3 AM, you must know exactly who to page. Responsibility table = ownership + escalation.

---

## Decision Framework

| Requirement | Pattern Choice |
|-------------|----------------|
| Add logging/metrics/TLS without code change | **Sidecar** |
| Service mesh, mTLS, retry policies | **Ambassador** |
| Legacy output → standard format | **Adapter** |
| Stateless scaling, high availability | **Replicated Service** |
| Data too large for one node | **Sharded Service** |
| Parallel search/analytics across partitions | **Scatter/Gather** |
| Async decoupling, variable load | **Work Queue** |
| Event notification, multiple consumers | **Pub/Sub** |
| Sporadic event-driven tasks | **FaaS** |
| Single coordinator needed | **Leader Election** |

---

## Anti-Patterns to Avoid

- ❌ **God container**: App + DB + cache + logging in one
- ❌ **Distributed monolith**: Microservices with synchronous chains
- ❌ **Shared database**: Services coupled via schema
- ❌ **No health checks**: Load balancer sends to dead pods
- ❌ **Synchronous chains**: A→B→C→D (cascading failures)
- ❌ **Implicit ownership**: "Someone will fix it"
- ❌ **Scatter/Gather without timeout**: Slowest worker hangs request

---

## Kubernetes Mapping

| Pattern | K8s Resources |
|---------|---------------|
| Sidecar/Ambassador/Adapter | Multi-container Pod |
| Replicated Service | Deployment + Service (ClusterIP/LoadBalancer) |
| Sharded Service | StatefulSet + headless Service + custom router |
| Scatter/Gather | Job/CronJob + parallelism + aggregation |
| Work Queue | Deployment (consumers) + external queue (Redis/Rabbit/Kafka) |
| Event-Driven | Knative Eventing, Kafka, NATS, CloudEvents |
| FaaS | Knative Serving, OpenFaaS, AWS Lambda (via KEDA) |
| Leader Election | Lease resource, etcd, or operator pattern |

---

## Trigger Phrases

`designing distributed systems`, `sidecar`, `ambassador pattern`, `replicated service`, `sharded service`, `leader election`, `scatter gather`, `event driven design`, `Brendan Burns`, `kubernetes patterns`

---

## Pairings

- `enterprise-integration-patterns` — messaging patterns (Hohpe & Woolf)
- `cloud-native-patterns` — Cornelia Davis' resilience patterns
- `distributed-systems-concepts-design` — Coulouris' theory
- `kubernetes-operations` — Beda/Hightower/Burns' K8s practice
- `streaming-systems-akidau` — stream processing patterns