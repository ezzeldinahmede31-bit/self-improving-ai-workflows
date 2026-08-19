---
name: mongodb-definitive-guide
description: Applies Chodorow's The Definitive Guide to MongoDB to building with the document database: the document model, CRUD operations and the query language, indexing, aggregation, replication and sharding for scale, and administration, with the operational realities of running MongoDB. Use when the user says 'MongoDB', 'document database', 'mongod', 'MongoDB aggregation', 'MongoDB index', 'sharding', 'replica set', 'Chodorow', 'NoSQL document store', or when a document model is the right fit and must be operated well.
---

# The Definitive Guide to MongoDB (Kristina Chodorow)

The Definitive Guide covers MongoDB from the document model through scaling. This skill applies it so the document database is used for what it is good at.

## The document model

- Documents embed related data instead of joining; design the document shape for the read pattern.
- The dynamic schema is a feature and a risk: version documents or enforce structure in code.
- Choose embed versus reference by access: read together, embed; shared and updated, reference.

## Queries and aggregation

- The query language filters, sorts, and projects on fields within documents.
- The aggregation pipeline stages transform documents; each stage is one operation.
- Design indexes for the query shape; the planner chooses by the available indexes.

## Replication and sharding

- Replica sets provide high availability; a majority elects the primary.
- Sharding distributes data by a shard key; choose the key so writes spread and reads stay local.
- The shard key is fixed at collection creation; choose it with the long-term pattern in mind.

## Administration

- Monitor memory, disk, and the replication lag; the metrics tell the health story.
- Backups and restore drills are mandatory; test them on a schedule.
- Cap the document size for sane I/O; the wire format and indexes pay per document.

## Pairs with
data-intensive-application-design, vector-databases-similarity-search, database-reliability-engineering, database-internals-engines, building-data-heavy-applications
