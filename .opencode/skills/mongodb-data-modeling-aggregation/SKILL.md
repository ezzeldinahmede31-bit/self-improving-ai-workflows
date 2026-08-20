---
name: mongodb-data-modeling-aggregation
description: Applies the modeling and aggregation guidance of MongoDB: The Definitive Guide (Chodorow) to design document schemas and query patterns: embedding versus referencing by access pattern, the aggregation pipeline stages (match, group, project, sort, unwind), and when a document model beats a relational one. Use when the user says 'MongoDB schema', 'embed or reference', 'document model', 'aggregation pipeline', 'match group project', 'unwind', 'MongoDB index', 'design a Mongo collection', 'Chodorow', or when modeling data for a document database.
---

# MongoDB: The Definitive Guide — Modeling and Aggregation

MongoDB rewards a different modeling instinct than relational databases: you design the document shape for the way the application reads and writes the data, not for a normalized schema. Chodorow's guide grounds that instinct in access-pattern analysis and in the aggregation pipeline that turns documents into reports. This skill encodes both.

## Embed Versus Reference
- Embed documents when the data is read and written together and never needs to stand alone.
- Reference (store an ObjectId) when the data is shared across many parents, or when the child has its own lifecycle.
- The deciding question is the access pattern: one query should retrieve the whole object the application renders.
- Embedding removes joins; referencing keeps duplication low but requires an application-level lookup or a join.

## Designing for Access Patterns
- Model for the queries you actually run, then index for those queries; do not model for hypothetical reads.
- Keep the working set of hot documents in memory by sizing documents to the workload, not to neatness.
- Use arrays when the cardinality is bounded and the array is read whole; avoid unbounded arrays that grow without bound.
- Prefer denormalized summary fields (like a comment tally on the parent) when the write pattern makes them cheap to maintain.

## The Aggregation Pipeline
- The pipeline transforms a collection through ordered stages: match filters, group aggregates, project reshapes, sort orders, unwind flattens arrays.
- Push filtering as early as possible with match so later stages see fewer documents.
- Group is where tallies and summaries happen; it can also accumulate arrays of child values for later processing.
- Unwind turns one document with an array into many documents, enabling per-element analysis.
- Lookup performs a left outer join across collections when referencing was the modeling choice.

## Indexing and Querying
- Index the fields that match, sort, and group on; a compound index can cover several stages at once.
- Prefix order matters: match fields first, then sort fields, matching the leftmost-prefix rule.
- Avoid indexing every field; each index adds write cost and storage.
- Verify with explain that the query uses the intended index before tuning further.
- Choose a document model over a relational one when the access is read-mostly and the data is naturally hierarchical.

## Pairs with
mongodb-definitive-guide, database-internals-engines, fundamentals-of-data-engineering, data-intensive-application-design, python-for-data-analysis
