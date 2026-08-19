---
name: fundamentals-database-systems
description: Applies Elmasri & Navathe's Fundamentals of Database Systems to the full database lifecycle: conceptual and logical design (ER and the extended model), relational mapping, normalization, SQL and relational algebra, object and XML models, transactions and concurrency, and databases on the web. Use when the user says 'fundamentals of database systems', 'ER model', 'extended ER', 'database design process', 'relational mapping', 'normal forms', 'Elmasri Navathe', 'database lifecycle', or when designing a database from requirements through schema.
---

# Fundamentals of Database Systems (Elmasri & Navathe)

Elmasri & Navathe is the comprehensive text on designing and modeling databases. This skill applies its structured design process from requirements to a working schema.

## Conceptual design

- Start with the requirements and build an ER or extended-ER model; the model is the shared understanding.
- Entities, attributes, relationships, and their cardinalities capture the rules of the domain.
- Resolve design choices (attributes versus entities, specialization versus generalization) explicitly.

## Logical mapping

- Map the conceptual model to a relational schema by fixed rules; each entity becomes a relation, each relationship a key or a relation.
- Choose primary keys that are stable and unique; foreign keys encode references.
- The mapping preserves the constraints; document which rules the mapping enforces.

## Normalization

- Normalization removes anomalies: update, insertion, and deletion problems caused by redundancy.
- Identify the normal form each relation achieves and the dependency that blocks the next level.
- Decompose losslessly: the join of the parts must reproduce the original exactly.

## Transactions and the web

- Transactions give atomicity and isolation; concurrency control makes them safe to overlap.
- Web and distributed databases add latency, replication, and consistency questions.
- Match the data model (relational, object, XML, NoSQL) to the actual access pattern.

## Pairs with
database-system-concepts, database-internals-engines, database-management-systems, data-intensive-application-design, domain-modeling-functional
