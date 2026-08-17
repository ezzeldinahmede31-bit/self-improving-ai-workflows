---
name: distributed-systems-concepts-design
description: "Applies Coulouris' Distributed Systems: Concepts and Design to architect reliable distributed systems: communication (RPC, message passing, publish-subscribe), clock synchronization and logical clocks, global state, mutual exclusion, election, transaction models, replication and consistency (linearizability vs eventual, quorums), and consensus (Paxos/Raft/Zab) with their impossibility results (FLP, CAP). Use when the user says 'distributed system', 'is my system consistent', 'replication lag', 'quorum', 'consensus', 'Raft', 'Paxos', 'logical clocks', 'vector clock', 'two-phase commit', 'failover', 'leader election', 'split brain', 'idempotency across replicas', or when designing a service that spans multiple nodes and must agree on ordering and state. Pairs with: database-internals-engines, cloud-native-patterns, state-machine-persistence, agent-arch-system-design, streaming-systems."
---

# Distributed Systems: Concepts and Design

Coulouris' textbook: distributed systems are collections of autonomous computers
that appear to users as a single coherent system. Every hard problem here is about
shared state, ordering, and partial failure — not about speed.

## When to use

- Designing or reviewing any multi-node service (microservices, databases, caches,
  queues, control planes).
- Choosing consistency, replication, or consensus mechanisms.
- Debugging anomalies caused by partial failure or clocks.

## The three hard pillars

1. **Partial failure is normal.** Assume any node, link, or process can fail at any
   moment and that you will not always be told. Design every interaction for a
   timeout, a retry, or an unknown outcome — idempotency is how you make retries safe.
2. **No global clock.** Nodes disagree on time; ordering must come from the system,
   not from wall clocks. Use logical clocks (Lamport) to order causally related
   events and vector clocks to detect concurrency and missing updates.
3. **There is no free consistency.** Replication gives availability and fault
   tolerance, but the more you replicate, the harder it is to stay linearizable.
   Choose the consistency model explicitly and know what each one promises.

## Communication
- RPC (remote procedure call): make the call look local but plan for failure —
  exactly-once is unattainable in general; provide at-least-once + idempotency or
  at-most-once semantics and state which.
- Message passing / queues / publish-subscribe: decouple producers from consumers,
  absorb bursts, but introduce asynchronous semantics and ordering questions.
- Choose synchronous (request-reply) where consistency matters, asynchronous where
  decoupling and throughput win.

## Consistency models (pick and document)
- **Linearizability**: single-node illusion — strongest, most expensive.
- **Sequential consistency**: operations appear in some order, same order for all.
- **Causal consistency**: causally related ops ordered, concurrent ops may differ.
- **Eventual consistency**: replicas converge given enough quiet time.
- Name the model each endpoint provides; never claim "strong consistency" without
  stating which reads/writes are covered.

## Replication, quorums, and consensus
- Leader-based replication: single writer orders writes, followers apply. Failover
  needs an election and risks split-brain without a quorum rule.
- Quorum (majority) reads/writes trade consistency for availability; tune the
  read/write quorum sizes to the guarantee you need.
- Consensus (Paxos, Raft, Zab) gives a safe replicated log for the metadata plane:
  one leader at a time, a majority that agrees, and a committed prefix that never
  changes. Raft favors understandability; Paxos is more general.
- FLP: consensus is impossible under async networks with a single faulty process —
  real systems (Raft, Zab) use timeouts and leader terms to work around it.
- CAP: during a partition you choose consistency or availability; document which
  side each component favors.

## Transactions and global state
- Two-phase commit coordinates multi-node transactions but blocks on coordinator
  failure — prefer sagas/compensation or single-node transactions when possible.
- Capture global snapshots for checkpointing and debugging (e.g., consistent
  cut algorithms) so distributed state can be inspected without stopping the world.

## Verification checklist
- Every call: timeout + retry + idempotency key.
- Every stateful node: is its ordering mechanism explicit (logical clock, term,
  monotonic counter)?
- Every replication path: consistency model named + quorum/leader mechanism stated.
- Failure injection: kill a node, a network link, a disk — does the system recover
  or violate a promised guarantee?

Pairs with: database-internals-engines (consensus mechanics), cloud-native-patterns
(deployment semantics), state-machine-persistence (durable state), streaming-systems
(ordering at scale).