---
name: system-type-distributed
description: "Foundational patterns for distributed systems — consensus, consistency models, replication, partitioning, clock synchronization, distributed transactions, and failure modes. Use when designing or evaluating any system that spans multiple nodes, processes, or failure domains."
---

# System Type: Distributed Systems

Foundational patterns, guarantees, and failure modes for systems that span multiple nodes.

---

## 1. Consistency Models

Most engineers say "consistent" when they mean five different things. Precision matters here because the guarantees determine what your application can and cannot assume.

### Linearizability

**What it guarantees.** Every operation appears to take effect instantaneously at some point between its invocation and completion. All processes observe the same ordering. If operation A completes before operation B begins, B sees A's effects.

**What it costs.** Requires coordination on every operation. In the presence of network partitions, a linearizable system must either become unavailable or violate the guarantee. Latency is bounded by the slowest participant in the quorum. Cross-datacenter linearizability is possible (Spanner does it) but requires specialized hardware (GPS + atomic clocks) and still adds measurable latency.

**When it's sufficient.** Leader election, distributed locks, compare-and-swap operations, unique constraint enforcement, fencing tokens. Anywhere a stale read causes a correctness violation, not just a user inconvenience.

**When it's overkill.** User profile reads, product catalog browsing, analytics dashboards, social feeds. Any read where showing data from 500ms ago is indistinguishable from "correct."

### Sequential Consistency

**What it guarantees.** All processes observe the same ordering of operations, and each process's operations appear in program order. Unlike linearizability, the global order doesn't need to respect real-time ordering — operation B can appear before operation A even if A completed first in wall-clock time.

**What it costs.** Less than linearizability (no real-time constraint) but still requires global ordering. Rarely offered as a standalone guarantee by modern systems — it sits in an awkward middle ground.

**When it matters.** Primarily a theoretical model. Useful for reasoning about memory models (Java Memory Model, C++ memory ordering) more than distributed storage systems.

### Causal Consistency

**What it guarantees.** If operation A causally precedes operation B (A happened before B, and B could have been influenced by A), then all processes observe A before B. Concurrent operations (neither caused the other) may be observed in different orders by different processes.

**What it costs.** Requires tracking causal dependencies — typically via vector clocks or explicit dependency metadata. More expensive than eventual consistency but significantly cheaper than linearizability. Can remain available during partitions (it's not constrained by CAP in the same way).

**When it's sufficient.** Comment threads (a reply must appear after the comment it replies to), collaborative editing (edits causally related to a cursor position), messaging (messages in a conversation appear in causal order). Any scenario where "this happened because of that" ordering matters but global total ordering doesn't.

### Eventual Consistency

**What it guarantees.** If no new updates are made, all replicas will eventually converge to the same state. That's it. No bound on how long "eventually" takes. No ordering guarantees during convergence. Different replicas may return different values for the same key at the same time.

**What it costs.** Cheapest to implement. Maximum availability. But your application must tolerate reading stale or inconsistent data. The real cost is in the application-level complexity required to handle inconsistency — retry logic, conflict resolution, reconciliation processes.

**When it's sufficient.** DNS propagation, CDN cache invalidation, eventually-consistent counters (like counts, not inventories), search index updates, social media feeds, recommendation engines.

**The dangerous middle.** Most systems advertising "eventual consistency" actually provide something slightly stronger — read-your-writes consistency, monotonic reads, or session consistency. Know exactly which variant your system provides. "Eventually consistent" without qualification is a statement too vague to build on.

### PACELC: The Practical Evolution of CAP

CAP theorem (Consistency, Availability, Partition tolerance — pick two) is useful as a mental model but misleading in practice. Partitions are not a choice; they happen. The real question is what you sacrifice when they do, and what you optimize for when they don't.

**PACELC states it clearly:** If there is a **P**artition, choose between **A**vailability and **C**onsistency. **E**lse (normal operation), choose between **L**atency and **C**onsistency.

| System | During Partition (PAC) | Normal Operation (ELC) |
|---|---|---|
| **Spanner** | Sacrifices availability (PC) | Sacrifices latency for consistency (EC) |
| **Cassandra** | Sacrifices consistency (PA) | Sacrifices consistency for latency (EL) |
| **DynamoDB** | Configurable per operation | Configurable per operation |
| **PostgreSQL (single node)** | N/A (no partition) | Consistent at the cost of single-node constraints |
| **CockroachDB** | Sacrifices availability (PC) | Sacrifices latency for consistency (EC) |

The insight: most design decisions are about the ELC tradeoff, not the PAC tradeoff. Partitions are rare. The latency vs consistency tradeoff affects every single request.

---

## 2. Consensus Protocols

Consensus is the mechanism by which distributed nodes agree on a single value or ordering of events. It's fundamental — and fundamentally expensive. Use it when you must; avoid it when you can.

### The FLP Impossibility Result

Before diving into protocols: Fischer, Lynch, and Paterson proved (1985) that in an asynchronous system where even one process can crash, no deterministic consensus protocol can guarantee termination. Every practical consensus protocol works around this by using timeouts, randomization, or partial synchrony assumptions. This is why consensus protocols have failure modes — they're engineering around an impossibility result, not solving a clean problem.

### Paxos (Conceptual)

**What it is.** The foundational consensus protocol (Lamport, 1989). A proposer proposes a value; acceptors vote; a value is chosen when a majority accepts. Multi-Paxos extends this to a sequence of values (a replicated log).

**Why it matters.** Every consensus protocol since is either a variation of Paxos or a reaction to its complexity. Google's Chubby, Spanner's replication layer, and many internal coordination systems use Paxos variants.

**Why it's hard.** The basic protocol is deceptively simple on paper. In practice: multi-decree Paxos requires leader election and log compaction. Reconfiguration (changing the set of acceptors) is a separate protocol. Recovery after crashes requires careful replay. The gap between "Paxos on a whiteboard" and "Paxos in production" is measured in years of engineering.

### Raft (Practical)

**What it is.** A consensus protocol designed to be understandable (Ongaro & Ousterhout, 2014). Decomposes consensus into leader election, log replication, and safety. Same guarantees as Multi-Paxos but with a clearer structure.

**How it works.**
1. **Leader election.** Nodes start as followers. If a follower receives no heartbeat within an election timeout, it becomes a candidate and requests votes. A candidate with a majority becomes leader. Only one leader per term.
2. **Log replication.** The leader appends entries to its log and replicates to followers. An entry is committed when a majority has persisted it. Committed entries are never lost (assuming no Byzantine failures).
3. **Safety.** A candidate can only win an election if its log is at least as up-to-date as a majority of the cluster. This ensures the new leader has all committed entries.

**Operational characteristics.**
- Typical cluster size: 3 (tolerates 1 failure) or 5 (tolerates 2). 7 is rare — the marginal availability gain doesn't justify the coordination cost.
- Leader handles all reads and writes (in basic Raft). This simplifies reasoning but means the leader is a throughput bottleneck.
- Follower reads (read from any node) can serve stale data. Linearizable reads require either reading from the leader after a heartbeat round or using a read index.

**Used in.** etcd, Consul, CockroachDB, TiKV, RethinkDB, InfluxDB.

### ZAB (ZooKeeper Atomic Broadcast)

**What it is.** The consensus protocol underlying Apache ZooKeeper. Similar to Raft in many ways (leader-based, log replication, majority quorums) but with a different recovery protocol and ordering guarantee.

**Key difference.** ZAB provides total order broadcast — all state changes are delivered in the same order to all replicas. This makes it suitable for coordination services where ordering is critical (leader election, distributed locks, configuration management).

**When to use ZooKeeper vs etcd vs Consul.** This is a deployment choice, not a protocol choice. All three provide consensus-backed coordination. etcd is the Kubernetes ecosystem standard. Consul adds service discovery and health checking. ZooKeeper is the Hadoop/Kafka ecosystem standard. Choose based on your existing infrastructure, not protocol nuances.

### Quorum-Based Decisions

The core of all these protocols: a decision requires agreement from a majority (quorum). In a cluster of N nodes:

- **Write quorum (W):** Number of nodes that must acknowledge a write.
- **Read quorum (R):** Number of nodes that must respond to a read.
- **Guarantee:** If W + R > N, every read quorum overlaps with every write quorum, so reads see the latest write.

Common configurations:
- **N=3, W=2, R=2:** Standard majority. Tolerates 1 failure for both reads and writes.
- **N=3, W=3, R=1:** Fast reads (any single node), but writes require all nodes (zero write fault tolerance). Useful for read-heavy workloads that can tolerate write unavailability.
- **N=5, W=3, R=3:** Tolerates 2 failures. Used when the cost of unavailability exceeds the cost of larger clusters.

### The Cost of Consensus

Consensus is expensive. Understand the cost before reaching for it:

- **Latency.** Every consensus round requires at minimum one network round trip to a majority. Cross-datacenter consensus adds cross-datacenter latency to every operation. A write to a 3-node Raft cluster in one datacenter: ~1ms. Across 3 datacenters: ~50-200ms depending on geography.
- **Availability during partitions.** A partitioned minority becomes unavailable. In a 3-node cluster, if 2 nodes are in datacenter A and 1 in datacenter B, a partition isolates datacenter B entirely.
- **Throughput.** The leader is a bottleneck. Throughput is bounded by the leader's ability to serialize, replicate, and commit entries. Multi-group Raft (sharding the consensus group) helps but adds complexity.

### When You Don't Need Consensus

Most systems don't need consensus for most operations. Before adding a consensus protocol, ask:

- **Can you use a single leader?** A single database primary with replication provides ordering without a consensus protocol. The tradeoff is a SPOF — but many systems tolerate this with fast failover.
- **Can you use idempotent operations?** If operations are idempotent and order doesn't matter, you can use eventual consistency with retries. No consensus needed.
- **Can you use CRDTs?** Conflict-free replicated data types (counters, sets, maps) converge without coordination. Excellent for counters, flags, and sets where merge semantics are well-defined.
- **Can you partition the problem?** If each key or entity has a single owner, that owner can make decisions unilaterally. Consensus is only needed to agree on ownership, not on every operation.

---

## 3. Replication Strategies

Replication serves two purposes: fault tolerance (survive node failures) and performance (serve reads from multiple locations). The strategy you choose determines your consistency guarantees, failure modes, and operational complexity.

### Single-Leader Replication

**How it works.** One node (the leader/primary) accepts all writes. It replicates writes to followers (secondaries/replicas). Reads can be served by the leader (consistent) or followers (possibly stale).

**Advantages.** Simple to reason about. No write conflicts — the leader serializes all writes. Strong consistency is straightforward (read from the leader). Well-supported by every major database.

**Disadvantages.** The leader is a write throughput bottleneck. Leader failure requires failover, which introduces an availability gap and a risk of data loss (unreplicated writes). All writes must flow through one region in a multi-region deployment.

**Replication lag.** Followers are always behind the leader by some amount. The lag is typically milliseconds under normal load, but can grow to seconds or minutes under high write throughput, follower resource pressure, or network congestion. Applications reading from followers must tolerate this.

**Failover risks.** When a leader fails:
1. A follower is promoted to leader.
2. If the old leader had unreplicated writes, those writes are lost unless the old leader recovers and reconciles.
3. Split-brain can occur if the old leader comes back and both it and the new leader accept writes. Fencing tokens or epoch numbers prevent this.
4. Clients connected to the old leader must discover and reconnect to the new leader. This is where client-side discovery or a proxy layer matters.

### Multi-Leader Replication

**How it works.** Multiple nodes accept writes (each is a leader for its region/partition). Leaders replicate to each other asynchronously.

**When to use.** Multi-datacenter writes where clients need low-latency writes to a local leader. Offline-capable clients (each client is effectively a leader that syncs when reconnected). Collaborative editing where multiple users modify the same data concurrently.

**The fundamental problem: conflicts.** Two leaders can accept conflicting writes to the same data simultaneously. You must have a conflict resolution strategy:

- **Last-Writer-Wins (LWW).** Use timestamps to pick the "latest" write. Simple but data-losing — the "earlier" write is silently discarded. Requires synchronized clocks (which you don't have — see Section 5). Acceptable only when losing some writes is tolerable (e.g., caching, session data).
- **Version vectors.** Track the causal history of each value. Detect concurrent writes (no causal relationship) vs sequential writes (one causally follows the other). Concurrent writes are flagged as conflicts for resolution. More precise than LWW but requires conflict resolution logic.
- **Application-level resolution.** Present both conflicting values to the application (or user) for resolution. CouchDB's "conflicting revisions" model. Most flexible but requires application-specific merge logic.
- **CRDTs.** Design data structures that merge automatically without conflicts. Works for counters, sets, registers, and maps with specific semantics. Cannot represent arbitrary application logic — only mathematically defined merge operations.

**Topology.** Leaders can replicate in various topologies: all-to-all (every leader sends to every other), circular (A→B→C→A), or star (one designated hub). All-to-all is the most resilient to individual node failures but creates more replication traffic.

### Leaderless Replication

**How it works.** Any node can accept reads and writes. No distinguished leader. Clients write to multiple nodes simultaneously. Reads query multiple nodes and resolve differences. (Dynamo-style systems: Cassandra, Riak, DynamoDB.)

**Quorum reads and writes.** With N replicas, write to W nodes and read from R nodes. If W + R > N, you're guaranteed to read the latest write (at least one node in the read quorum has the latest value). The client or a coordinator resolves discrepancies.

**Read repair and anti-entropy.** When a read detects stale data on some replicas, the client or coordinator can write the latest value back (read repair). Background anti-entropy processes continuously compare and reconcile replicas.

**Advantages.** No leader election, no failover. High availability — any individual node failure doesn't cause unavailability (as long as quorums are maintained). Write latency determined by the Wth-fastest node, not the slowest.

**Disadvantages.** Sloppy quorums can violate consistency guarantees (a node temporarily fills in for an unreachable node, creating a situation where W + R > N is technically satisfied but the quorum doesn't include the right nodes). Concurrent writes still require conflict resolution. Monitoring and debugging are harder — there's no single authoritative state to inspect.

### Synchronous vs Asynchronous Replication

**Synchronous.** The leader waits for the follower to confirm the write before acknowledging to the client. Guarantees durability — if the leader fails, the follower has the data. Cost: every write pays the latency of the slowest follower. If a follower is down, writes block.

**Asynchronous.** The leader acknowledges the write immediately and replicates to followers in the background. Lower latency, higher availability. Cost: data loss risk — if the leader fails before replication completes, acknowledged writes are lost.

**Semi-synchronous.** Synchronously replicate to one follower, asynchronously to the rest. Balances durability and latency — you get one confirmed copy beyond the leader without paying the latency of all followers. PostgreSQL's `synchronous_commit` with `synchronous_standby_names` implements this.

**The practical choice.** Most production systems use semi-synchronous replication for critical data and asynchronous replication for less critical data. Fully synchronous replication across datacenters is rare due to latency costs — it's reserved for systems where data loss is unacceptable and latency is secondary (financial ledgers, regulatory records).

---

## 4. Partitioning (Sharding)

When data exceeds the capacity of a single node — storage, write throughput, or read throughput — you partition it across multiple nodes. Every partitioning decision is a bet about your access patterns.

### Hash Partitioning

**How it works.** Apply a hash function to the partition key and assign the key to a node based on the hash value. Distributes data uniformly across partitions (assuming a good hash function and sufficient key cardinality).

**Advantages.** Even data distribution. No hot spots from sequential keys. Simple to implement.

**Disadvantages.** Destroys key ordering. Range queries across adjacent keys (e.g., "all orders from January") must scatter to all partitions. Adding or removing nodes requires remapping keys (unless using consistent hashing).

**When to use.** When access is primarily by exact key lookup. When your keys are not naturally sequential. When even distribution matters more than range query efficiency.

### Range Partitioning

**How it works.** Divide the key space into contiguous ranges, assigning each range to a node. Keys within a range are co-located.

**Advantages.** Range queries are efficient — all keys in a range live on the same node. Supports ordered access patterns naturally.

**Disadvantages.** Risk of hot spots — if recent data is most frequently accessed and keys are time-ordered, the latest partition absorbs disproportionate load. Requires a partition map or directory to know which ranges are on which nodes.

**When to use.** Time-series data with time-range queries. Sequential data with natural ordering (user IDs in ranges, alphabetical lookups). Any access pattern that benefits from co-located ranges.

### Partition Key Selection

The partition key determines data distribution, query efficiency, and hot spot risk. It is the single most consequential schema decision in a distributed system.

**Good partition keys:**
- High cardinality (many distinct values). A boolean is a terrible partition key — two partitions.
- Uniform distribution. User IDs are usually good. Country codes are bad (a few countries dominate).
- Aligned with query patterns. If 90% of queries filter by `tenant_id`, partition by `tenant_id`.

**Composite partition keys.** Use when a single key doesn't satisfy both distribution and query needs. Cassandra's `PRIMARY KEY ((tenant_id, month), event_time)` partitions by tenant and month (good distribution) and clusters by event time within each partition (efficient range queries within a month).

**Hot spot mitigation.** Even good partition keys can create hot spots. A celebrity's user_id in a social network receives disproportionate write traffic. Mitigations:
- Add a random suffix to hot keys, spreading writes across partitions (at the cost of reading from multiple partitions).
- Application-level rate limiting for hot entities.
- Split hot partitions dynamically (if the system supports it — DynamoDB adaptive capacity, Bigtable tablet splitting).

### Cross-Partition Queries and Transactions

Partitioning optimizes single-partition operations at the expense of cross-partition operations.

**Cross-partition queries.** A query that doesn't include the partition key must scatter to all partitions and gather results. This is expensive, high-latency, and doesn't scale linearly. Design your data model so that the most frequent queries hit a single partition.

**Cross-partition transactions.** Two-phase commit across partitions is possible but expensive (see Section 6). Many distributed databases support single-partition transactions natively but require 2PC for cross-partition transactions, which is slower and less available.

**Denormalization.** The standard response to cross-partition query problems: duplicate data so that each partition contains everything needed for its queries. This trades write amplification and consistency complexity for read performance. It's often the right trade in read-heavy systems.

### Consistent Hashing

**The problem.** Standard hash partitioning (`hash(key) mod N`) requires remapping nearly all keys when N changes (a node is added or removed).

**The solution.** Arrange the hash space in a ring. Each node is assigned positions on the ring (virtual nodes). Each key hashes to a position and is assigned to the next node clockwise on the ring. When a node is added or removed, only the keys between the new node and its predecessor are remapped — roughly 1/N of the total.

**Virtual nodes.** Each physical node gets multiple positions on the ring (virtual nodes). This smooths out distribution — without virtual nodes, a node assigned a large arc gets disproportionate data. 100-200 virtual nodes per physical node is typical.

**Used in.** Dynamo, Cassandra, Riak, memcached (client-side), Akka Cluster Sharding. CDN request routing. Load balancer backends.

### Rebalancing Strategies

When partitions become uneven (data growth, hot spots, node additions):

- **Fixed partition count.** Create many more partitions than nodes (e.g., 1,000 partitions for 10 nodes, 100 per node). When a node is added, transfer some partitions to it. No repartitioning of data, just reassignment of whole partitions. Used by Elasticsearch, Couchbase, Riak.
- **Dynamic splitting.** Start with fewer partitions. When a partition exceeds a size threshold, split it. When it shrinks, merge it. Used by HBase, Bigtable, CockroachDB.
- **Proportional to node count.** Each node gets a fixed number of partitions. When a new node joins, it splits a random selection of existing partitions and takes half. Used by Cassandra.

---

## 5. Clock Synchronization

Time in a distributed system is not what you think it is. There is no global clock. Every node has its own clock, and they disagree.

### Physical Clocks

**NTP (Network Time Protocol).** Synchronizes clocks to a reference source over the network. Typical accuracy: 1-10ms within a datacenter, 10-100ms across the internet. Under network congestion or misconfiguration, drift can reach seconds. NTP can also step the clock backward, which breaks any code that assumes monotonically increasing `gettimeofday()`.

**PTP (Precision Time Protocol).** Hardware-assisted time synchronization using dedicated network hardware. Accuracy: sub-microsecond within a datacenter. Requires hardware support (PTP-capable NICs, PTP-aware switches). Not available in cloud environments unless the provider supports it.

**The problem.** Physical clocks are always approximate. Two events on different machines with timestamps 1ms apart could have actually happened in either order (or simultaneously). Using physical clock timestamps for ordering is incorrect unless the uncertainty interval is smaller than the difference.

### Logical Clocks (Lamport Timestamps)

**What they are.** A counter that increments on each event. When a node sends a message, it attaches its counter. When a node receives a message, it sets its counter to `max(local, received) + 1`.

**What they guarantee.** If event A causally precedes event B, then `timestamp(A) < timestamp(B)`. The converse is not true — a higher timestamp doesn't mean causal precedence. Lamport timestamps establish a total order consistent with causality but cannot detect concurrency.

**When they're sufficient.** When you need a total ordering of events and concurrent events can be ordered arbitrarily. Log sequencing, unique ID generation (combined with node ID), mutual exclusion algorithms.

### Vector Clocks

**What they are.** Each node maintains a vector of counters, one per node. On a local event, increment your own counter. On sending, attach the vector. On receiving, take the component-wise max and increment your own counter.

**What they guarantee.** Can detect both causality and concurrency. `V(A) < V(B)` (every component of A ≤ corresponding component of B, with at least one strict inequality) means A causally precedes B. If neither V(A) < V(B) nor V(B) < V(A), then A and B are concurrent.

**The cost.** Vector size grows with the number of nodes. In a system with thousands of nodes, vectors become impractically large. Solutions: pruned vector clocks (discard entries for nodes not recently seen), dotted version vectors (more compact representation), or limit the number of nodes participating in vector clock tracking.

**When they're sufficient.** Conflict detection in leaderless replication (Riak, Dynamo). Causal consistency enforcement. Any scenario where distinguishing "concurrent" from "causally ordered" matters for correctness.

### Hybrid Logical Clocks (HLC)

**What they are.** Combine physical clock time with a logical counter. The physical component tracks real time (within NTP uncertainty). The logical counter breaks ties and ensures causality within uncertainty windows.

**Why they exist.** Lamport clocks lose all connection to real time. Physical clocks don't capture causality. HLC provides causality tracking while keeping timestamps correlated with real time, enabling meaningful time-based queries ("give me everything after 3:00 PM") that pure logical clocks cannot support.

**Used in.** CockroachDB, MongoDB (with caveats), various distributed databases that need "approximately real-time" timestamps with causal guarantees.

### TrueTime (Spanner's Approach)

**What it is.** Google's time API that returns an interval `[earliest, latest]` rather than a single timestamp. It guarantees that the true time is within this interval. The interval width is typically 1-7ms, achieved using GPS receivers and atomic clocks in each datacenter.

**How Spanner uses it.** When committing a transaction, Spanner waits until the TrueTime interval has passed (`commit_wait`). This guarantees that any later transaction on any node will have a strictly later timestamp. This enables global, externally consistent (linearizable) transactions using timestamps as the serialization order.

**Why most systems can't replicate this.** TrueTime requires GPS receivers and atomic clocks in every datacenter — hardware that cloud customers don't control. AWS, Azure, and GCP time services don't provide the same tight bounds. CockroachDB approximates TrueTime with NTP but must use larger uncertainty intervals (50-500ms), which means longer commit waits and higher tail latency. The gap between Spanner and everything else is hardware, not software.

### Why Wall-Clock Ordering Is Insufficient

The most common distributed systems bug: using `timestamp` columns with wall-clock time to determine event ordering across nodes. This fails because:

1. **Clock skew.** Node A's clock is 5ms ahead of Node B's. An event on B that happens 3ms after an event on A gets a timestamp 2ms earlier. The order is wrong.
2. **Clock drift.** Clocks drift at different rates. Even after NTP sync, they immediately begin diverging.
3. **NTP step adjustments.** NTP can jump a clock forward or backward, creating duplicate or missing timestamp ranges.
4. **Leap seconds.** 23:59:60 exists sometimes. Code that assumes 60 seconds per minute breaks.

**The rule.** Never use wall-clock timestamps to determine the order of events across machines unless you have bounded clock uncertainty and your correctness model accounts for the uncertainty interval.

---

## 6. Distributed Transactions

A distributed transaction spans multiple nodes, each with their own failure modes. The fundamental challenge: committing on some nodes and aborting on others leaves the system in an inconsistent state.

### Two-Phase Commit (2PC)

**Phase 1: Prepare.** The coordinator sends a prepare request to all participants. Each participant votes "yes" (I can commit) or "no" (I must abort). A "yes" vote is a promise — the participant must be able to commit even if it crashes and recovers.

**Phase 2: Commit/Abort.** If all participants voted "yes," the coordinator sends commit. If any voted "no," the coordinator sends abort. Each participant applies the decision.

**The coordinator as SPOF.** Between Phase 1 and Phase 2, participants are in a prepared state — they've promised to commit but haven't yet. If the coordinator crashes in this window:
- Participants holding locks cannot release them (they don't know the decision).
- They cannot unilaterally abort (they promised to commit if told to).
- They cannot unilaterally commit (the coordinator might have decided to abort).
- They're stuck. This is the "in-doubt" state, and it can hold locks for hours until the coordinator recovers.

**Performance.** 2PC requires at minimum 2 synchronous network round trips (prepare + commit). With disk fsyncs for durability at each step (coordinator and participants), this is slow — typical 2PC latencies are 10-50ms for local transactions, hundreds of milliseconds cross-datacenter.

**When to use.** When atomic cross-partition or cross-database consistency is genuinely required and the participating systems are under your control. Database-to-database consistency within a single organization. XA transactions between a database and a message broker (commit message send and database write atomically).

### Three-Phase Commit (3PC)

**The theory.** Adds a "pre-commit" phase between prepare and commit. This eliminates the blocking problem — if the coordinator fails, participants can determine the outcome by communicating with each other.

**The practice.** 3PC assumes reliable failure detection (you can tell the difference between a crashed node and a slow node). In an asynchronous network, you cannot reliably distinguish crash from delay. This means 3PC can still produce inconsistent outcomes under network partitions. No production database uses 3PC. It's a textbook curiosity.

### Saga Pattern

**What it is.** Break a distributed transaction into a sequence of local transactions, each with a compensating action. If step 3 fails, execute compensating actions for steps 2 and 1 (in reverse order).

**Example.** Book flight → Book hotel → Charge payment. If payment fails: cancel hotel booking → cancel flight booking.

**Choreography vs orchestration.**
- Choreography: Each service listens for events from the previous step and triggers the next. Decoupled but hard to monitor — the saga's state is distributed across event subscriptions.
- Orchestration: A central coordinator directs each step and handles compensations. Easier to debug and monitor. The coordinator is a coupling point but not a SPOF (it can persist its state and resume after crash).

**Critical design considerations:**
- **Compensating actions are not rollbacks.** A compensating action is a new forward action that semantically undoes the previous action. Canceling a hotel booking is not "un-booking" — it's creating a cancellation record, potentially triggering a refund process, updating availability. Compensating actions can themselves fail and need retry logic.
- **Isolation is lost.** Between saga steps, intermediate states are visible to other transactions. A flight booked in step 1 is visible to other users before the saga completes. This is the semantic difference from a true ACID transaction.
- **Idempotency is mandatory.** Each step and each compensation must be idempotent. Network retries can re-deliver step triggers. Without idempotency, you get double bookings or double refunds.

### When to Avoid Distributed Transactions Entirely

Ask these questions before adding distributed transaction machinery:

- **Can you redesign to avoid the distributed boundary?** If two pieces of data that must be consistent are in different services, maybe they should be in the same service. The microservice boundary was drawn wrong.
- **Can you use eventual consistency with reconciliation?** If "consistent within 5 minutes" is acceptable, skip the transaction machinery and run a periodic reconciliation job that detects and fixes inconsistencies.
- **Can you use the outbox pattern?** Write to the database and an outbox table in a single local transaction. A separate process reads the outbox and sends messages/events. This gives you atomic local commit + reliable message delivery without 2PC.
- **Is the consistency requirement real?** Many "must be atomic" requirements dissolve when you talk to the product owner. "What happens if the payment succeeds but the confirmation email doesn't send?" is usually "we retry the email" — not "we refund the payment."

---

## 7. Failure Detection

In a distributed system, you can't distinguish between a crashed node, a slow node, and a network partition. Every failure detection mechanism is making a probabilistic judgment that will sometimes be wrong.

### The Impossibility of Perfect Failure Detection

In an asynchronous system (one where messages can be delayed arbitrarily), it is impossible to build a perfect failure detector — one that is both:
- **Complete:** Every failed node is eventually detected.
- **Accurate:** No healthy node is ever falsely suspected.

Every practical failure detector sacrifices accuracy for completeness (it may falsely suspect healthy but slow nodes) or completeness for accuracy (it may take a long time to detect actual failures).

### Heartbeats

**How it works.** Nodes periodically send "I'm alive" messages. If a node misses K consecutive heartbeats (or doesn't respond within a timeout), it's considered failed.

**Configuration tradeoffs:**
- Short timeout (e.g., 1s): Fast detection but high false-positive rate during network congestion or GC pauses.
- Long timeout (e.g., 30s): Low false positives but slow detection — 30 seconds of serving errors before failover begins.
- Typical production values: 5-10 second timeouts with 2-3 missed heartbeats required.

**Failure modes of heartbeats:**
- GC pauses (Java, Go): A 10-second stop-the-world GC pause looks exactly like a crash.
- Network congestion: Heartbeats delayed beyond the timeout even though the node is healthy.
- Asymmetric failures: Node A can reach B, but B can't reach A. From A's perspective, B is alive. From B's perspective, A is dead. From C's perspective, both are alive.

### Phi-Accrual Failure Detector

**How it works.** Instead of a binary alive/dead decision, computes a "suspicion level" (phi) based on the statistical distribution of heartbeat arrival times. Adapts to the network conditions — a node that typically responds in 2ms gets suspected faster than one that typically responds in 200ms.

**Advantages.** Self-tuning. Adapts to changing network conditions. Produces a continuous suspicion level rather than a hard cutoff, letting applications make nuanced decisions.

**Used in.** Akka, Cassandra. Any system where the "right" timeout varies by node and changes over time.

### Gossip-Based Failure Detection

**How it works.** Nodes randomly share their knowledge of the cluster with each other ("I last heard from A at time T, from B at time T'..."). Failed node information propagates epidemically through the cluster. This distributes the detection load and avoids single-point-of-failure in the detector itself.

**Advantages.** No centralized health monitor. Scales to large clusters. Tolerant of partial network failures — information reaches all nodes through any connected path.

**Disadvantages.** Detection is not instant — information takes O(log N) gossip rounds to reach all nodes. For a 1,000-node cluster with 1-second gossip intervals, detection takes ~10 seconds to propagate everywhere.

**Used in.** Consul (SWIM protocol), Cassandra (gossip protocol), Serf, Memberlist.

### Timeouts: The Core Tradeoff

Every failure detection system ultimately reduces to a timeout decision. The tradeoff is fundamental:

**Too short (aggressive detection):**
- False positives: Healthy but slow nodes are declared dead.
- Unnecessary failovers: Promoting a new leader when the old one was just GC-pausing.
- Thrashing: Node is declared dead, removed from the cluster, recovers, rejoins, is declared dead again.
- Split-brain: Two nodes both believe the other is dead and both assume leadership.

**Too long (conservative detection):**
- Slow recovery: Users experience errors for the full timeout duration before failover begins.
- Resource waste: Requests continue to be routed to a dead node until it's detected.
- Queue buildup: Retries accumulate, causing a thundering herd when the node is finally replaced.

**No universal right answer.** Choose based on the cost of false positives vs the cost of slow detection. For a leader election where split-brain causes data corruption: long timeouts. For a stateless web server behind a load balancer: short timeouts (false positives just shift traffic, low cost).

---

## 8. Common Failure Modes

These are the failures that plague distributed systems in production. They are not edge cases — they are the normal operating conditions of a system at scale.

### Split Brain

**What it is.** Two or more nodes believe they are the leader simultaneously. Both accept writes, creating divergent state that must be reconciled (and often can't be without data loss).

**Common causes.** Network partition isolates the old leader but it remains operational. Failure detection timeout is longer than the time to elect a new leader. Clock skew causes a lease to be considered valid by the holder but expired by others.

**Prevention.** Fencing tokens: a monotonically increasing number assigned to each leader. Resources (databases, storage) reject operations from leaders with stale tokens. Epoch numbers in Raft serve this purpose. Quorum-based leases: a leader must renew its lease with a majority, ensuring that a partitioned leader loses its lease before a new one is elected.

### Network Partitions

**What they are.** Some nodes can communicate with each other but not with others. The system is split into disconnected components.

**What makes them hard.** A partition is indistinguishable from a slow network until enough time passes. Nodes inside each partition operate normally — they don't know they're partitioned. When the partition heals, divergent state must be reconciled.

**Handling strategies.**
- **CP systems (consistency over availability):** The minority partition rejects operations. Only the partition with a majority can proceed. Users connected to the minority partition see errors.
- **AP systems (availability over consistency):** Both partitions continue operating. State diverges. Reconciliation is required after the partition heals. Application must handle conflicts.
- **Explicit partition detection:** Monitor cross-partition health checks. When a partition is detected, switch to a degraded mode (read-only, cached data, queued writes) rather than serving potentially inconsistent data.

### Data Loss During Leader Failover

**Scenario.** Leader accepts writes, replicates asynchronously. Leader fails. Promoted follower is missing the last N writes. Those writes are lost.

**How common.** In any system with asynchronous replication, this is a normal failure mode, not an edge case. The window of data loss equals the replication lag at the moment of failure.

**Mitigations.** Semi-synchronous replication (at least one follower is synchronous). Application-level acknowledgment (don't tell the user "saved" until the data is on multiple nodes). Accepting the loss window and designing the application to tolerate it (retry logic, idempotent operations).

### Cascading Failures from Partial Connectivity

**Scenario.** Node A can reach B and C. B can reach A but not C. C can reach A but not B. This is not a clean partition — it's partial connectivity, and it breaks many consensus algorithms' assumptions.

**Consequences.** B and C disagree about cluster membership. A becomes a bottleneck for all cross-node communication. Heartbeat-based failure detection gives different results depending on which node you ask.

**Mitigations.** Use gossip-based failure detection that aggregates multiple nodes' views. Design health checks to test connectivity from multiple vantage points, not just from a monitoring server. Consider a node that has partial connectivity as unhealthy — it's better to remove it than to operate with an inconsistent network view.

### Clock Drift Causing Ordering Violations

**Scenario.** Two nodes accept writes with wall-clock timestamps. Node A's clock is 50ms ahead. An event on A at T=100 actually happened before an event on B at T=120, but the timestamps say the opposite. If LWW conflict resolution is used, the wrong write wins.

**Scale of the problem.** NTP-synced clocks in a single datacenter typically drift by 1-10ms. Across datacenters: 10-100ms. A VM migration can introduce clock jumps of hundreds of milliseconds. In cloud environments, clock drift is the norm, not the exception.

**Mitigations.** Don't use wall-clock timestamps for causality. Use logical clocks, version vectors, or hybrid logical clocks. If you must use physical time (for TTLs, expiry, scheduling), include an uncertainty interval and design the system to be correct when events fall within the uncertainty window.

### Byzantine Failures

**What they are.** A node behaves arbitrarily — sending incorrect data, lying about its state, or actively trying to disrupt the system. Contrasted with crash failures (a node stops responding) and omission failures (a node drops messages).

**When to care.** Public blockchains. Systems where nodes are operated by mutually distrusting parties. Military or aerospace systems where hardware radiation effects can flip bits. Financial systems subject to regulatory requirements about tamper resistance.

**When not to care.** Internal distributed systems within a single organization. If you control all the nodes, Byzantine fault tolerance adds enormous complexity for a threat model that's better addressed by access control, network security, and operational practices. A node sending garbage data is a bug, not a Byzantine failure — fix the bug.

### Inconsistency Windows During Partition Healing

**Scenario.** During a network partition, two partitions accepted writes. The partition heals. Now the system must reconcile two divergent histories.

**What goes wrong.** Automatic reconciliation (LWW, merge functions) may silently discard valid data. Application-specific reconciliation logic may not handle all conflict combinations. Users see data "appear" or "disappear" as the reconciled state differs from what either partition was showing.

**Mitigations.** Design for mergeable state (CRDTs). Log all writes during partition so reconciliation can inspect the full history, not just end states. Alert operators when partitions heal so they can monitor for reconciliation anomalies. If automatic reconciliation is impossible, queue conflicts for human resolution.

---

## 9. Anti-Patterns

**"CAP theorem says we must choose."** CAP is about partitions — specifically, what you sacrifice when a partition occurs. It is not a design menu where you pick two of three properties. Every system must handle partitions (they're not optional); the question is whether you sacrifice consistency or availability when one happens. Most design decisions are about the latency-consistency tradeoff during normal operation (the ELC side of PACELC), not the partition tradeoff. Citing CAP to justify eventual consistency without discussing partition behavior is cargo-cult reasoning.

**"Distributed monolith."** Microservices that must be deployed together, share a database, or fail as a unit. You've paid the full cost of distribution (network calls, partial failure, operational complexity) with none of the benefits (independent deployment, independent scaling, independent failure domains). If everything must be deployed together, make it a monolith and save yourself the network hops.

**"Consensus for everything."** Running every write through a consensus protocol when most operations don't need cross-node agreement. Consensus is for coordination — leader election, distributed locks, configuration changes, metadata operations. Data plane operations (reading a cached value, appending to a log, serving a static asset) should bypass consensus entirely. If your consensus cluster is a throughput bottleneck, you're probably routing data through it that doesn't need coordination.

**"Timestamps as ordering."** Using `System.currentTimeMillis()` or `time.time()` to determine the order of events across machines. This is wrong. It will produce incorrect orderings proportional to your clock skew, and you will not detect the errors because the data will look plausible. Use logical clocks, version vectors, or a sequencer service.

**"Network is reliable."** Designing without handling network failures, retries, timeouts, or partial connectivity. The network will drop packets, reorder messages, deliver duplicates, and partition. If your system hasn't been tested with network failure injection (Chaos Monkey, Toxiproxy, tc netem), it hasn't been tested.

**"Just add more replicas."** More replicas increase read capacity but do not increase write capacity (single-leader) or consistency guarantees. They increase replication lag, operational complexity, and the probability of at least one replica being behind. The correct response to write bottlenecks is partitioning, not replication.

**"Exactly-once delivery."** Claiming a message broker provides exactly-once delivery end-to-end. Brokers can provide at-most-once or at-least-once. Exactly-once semantics are achieved at the application level through at-least-once delivery combined with idempotent processing. Any system claiming exactly-once delivery is either (a) implementing idempotency internally and marketing it as a feature, or (b) wrong.

**"Global transactions for everything."** Using 2PC or XA transactions across services for every write. 2PC is slow (synchronous multi-round-trip), fragile (coordinator is SPOF), and reduces availability. Use it for the narrow set of operations that genuinely require cross-system atomicity. For everything else, use the outbox pattern, sagas, or eventual consistency with reconciliation.

**"Synchronous calls to all dependencies."** Service A synchronously calls B, which synchronously calls C, which calls D. The availability of A is the product of the availability of A, B, C, and D. If each is 99.9% available, the chain is 99.6% available. Longer chains are worse. Use asynchronous communication, caching, circuit breakers, and graceful degradation to break synchronous chains.

**"Treating all data the same."** Applying the same consistency, durability, and replication guarantees to every piece of data. User authentication tokens need strong consistency. Analytics event counts can be eventually consistent. Product catalog descriptions can be cached for minutes. Classifying data by its consistency and durability requirements — and applying different strategies to each class — is the single highest-leverage design decision in a distributed system.
