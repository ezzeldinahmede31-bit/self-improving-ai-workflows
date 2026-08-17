---
name: database-replication-consensus
description: Applies Alex Petrov's Database Internals treatment of replication and distributed consensus: leader-based vs leaderless replication, quorum systems and their trade-offs, replication lag and its consequences, and the Raft/Paxos consensus protocol mechanics (term, quorum, log replication, safety). Use when the user says 'replication', 'replica lag', 'leader election', 'quorum', 'read-after-write consistency', 'Raft', 'Paxos', 'consensus', 'split brain', 'multi-leader', 'synchronous vs asynchronous replication', 'write concern', 'distributed database design', or when a system must keep multiple copies consistent and survive node failures. Pairs with: database-internals-engines, state-machine-persistence, agent-arch-system-design, cloud-native-patterns.
---

# Database Replication and Consensus

Transfers Petrov's Database Internals knowledge of replication and consensus to production systems: choose a replication topology that matches the consistency and availability needs, reason about quorums, and understand exactly what Raft and Paxos do — and what they do not.

## When to use
- Designing multi-node storage that must survive node loss.
- Choosing the replication topology — leader-based, multi-leader, or leaderless.
- Reasoning about replication lag and stale reads.
- Implementing or evaluating a consensus layer (Raft/Paxos).

## Replication topology selection
1. Leader-based: single write path, easy ordering, linearizable reads from the leader; the follower lag bounds read-your-writes behavior.
2. Multi-leader: cross-datacenter writes with conflict resolution requirements; conflicts are inevitable, so a resolution policy is mandatory.
3. Leaderless: quorum writes/reads (W + R > N) tolerate node loss; the trade-off is weaker ordering guarantees.

## Quorum reasoning
- A write quorum W and read quorum R with W + R > N guarantee one or more nodes hold the newest version, so reads never return entirely stale data.
- Choosing W and R is an availability-latency trade; document the failure mode when quorums cannot be met.

## Consensus (Raft/Paxos)
- Raft: terms and log replication with majority commit; safety rests on the Leader Completeness invariant — a committed entry always survives in a newer term.
- Paxos: the Prepare/Promise and Accept/Accepted rounds; quorum intersection guarantees a single chosen value.
- Consensus orders events and guarantees agreement, but it is not a substitute for application-level idempotency and retries.

## Verification discipline
- Simulate node failure and network partition; assert the system still reads/writes per the declared quorum.
- Measure replication lag under load and verify the read path honors it.

## Pairs with
database-internals-engines, state-machine-persistence, agent-arch-system-design, cloud-native-patterns.