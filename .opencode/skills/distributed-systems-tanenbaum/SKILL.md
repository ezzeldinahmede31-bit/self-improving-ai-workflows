---
name: distributed-systems-tanenbaum
description: Applies Tanenbaum & Van Steen's Distributed Systems to the principles and recurring paradigms of distributed computing: communication (RPC, message-oriented), processes and threads in a distributed setting, naming, synchronization and clock handling, consistency and replication, fault tolerance, and the classic paradigms (distributed objects, web services, peer-to-peer). Use when the user says 'distributed systems', 'RPC', 'naming service', 'logical clocks', 'consistency', 'replication', 'fault tolerance', 'peer to peer', 'Tanenbaum Van Steen', or when designing a system that spans multiple machines.
---

# Distributed Systems: Principles and Paradigms (Tanenbaum & Van Steen)

This book organizes the distributed-systems design space into principles and recurring paradigms. This skill uses that structure to make architecture decisions explicit.

## Communication

- RPC and message passing are the two communication models; choose by the coupling you can tolerate.
- Name services translate names to locations; the naming scheme defines how endpoints are found.
- Interoperability requires a shared representation; the wire format is the contract.

## Synchronization and clocks

- Physical clocks drift; logical clocks impose an order on events without wall time.
- Mutual exclusion and leader election in a distributed setting need explicit algorithms with stated guarantees.
- Distributed transactions need a protocol (two-phase commit) and a failure model.

## Consistency and replication

- Replication improves availability and performance but creates consistency questions.
- Sequential consistency and linearizability differ in what concurrent observers may see; state which you provide.
- Eventual consistency is a real service guarantee; define the convergence properties.

## Fault tolerance

- Design for partial failure: a distributed system never fails all at once.
- Group membership, failure detection, and reliable broadcast are the building blocks.
- Choose the paradigm (objects, web services, peer-to-peer) by the distribution of responsibility.

## Pairs with
distributed-systems-concepts-design, database-replication-consensus, cloud-native-patterns, designing-distributed-systems, designing-event-driven-systems
