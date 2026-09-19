---
name: graph-databases-modeling
description: "Models and queries connected data: property graphs, traversals, and Cypher. Use when the user says 'graph database', 'Neo4j', 'Cypher', 'traversal', 'fraud ring', 'recommendations', 'knowledge graph', 'index-free adjacency', or when JOINs explode on relationships."
---

# Graph Databases Modeling

Distilled from Robinson/Webber/Eifrem *Graph Databases*: relationships are
data — store them as first-class citizens with index-free adjacency, and
traversals stay constant-time per hop no matter how large the graph grows.

## Purpose

Model highly-connected domains (fraud, identity, recommendations, networks,
lineage) so relationship queries are traversals, not exponential JOINs.

## The method

1. **Model as whiteboard.** Nodes (entities with labels + properties),
   relationships (typed, directed, with properties). If the domain expert
   draws circles and arrows, the model is already right — transcribe it,
   don't normalize it away. Relationship TYPES are the schema (design them
   like an API: precise verbs, stable meanings).
2. **Traverse, don't join.** Pattern matching (`(a:Person)-[:KNOWS*1..3]->(b)`)
   expresses multi-hop intent directly; each hop follows stored pointers
   (index-free adjacency) instead of scanning indexes per join. Depth +
   direction + type bounds keep traversals finite and fast.
3. **Design for traversal direction.** Relationships traversed both ways get
   modeled once (direction is query-time); super-nodes (millions of edges on
   one node: "all users in country X") get intermediate grouping nodes or
   time-bucketed edges — dense nodes are the graph performance cliff.
4. **Time and versioning.** Valid-time properties on relationships (since/
   until) instead of deleting history; bitemporal where audit demands.
   "Current graph" is a filtered view, matching the temporal discipline in
   `fowler-analysis-patterns`.
5. **Scale honestly.** Single-machine graphs go far (tens of billions of
   edges with pointer storage); sharding graphs splits relationships —
   partition by traversal locality (community/region), replicate reference
   data, accept cross-shard hops as measured costs, not surprises.

## Query discipline (Cypher-shaped, portable)

- Anchor on selective starts (indexed labels/properties), expand along
  typed relationships, aggregate at the end. PROFILE every production
  query: row growth per hop is the number to watch.
- Parameters always (plan cache + injection safety); UNWIND batches for bulk
  writes; APOC/procedures for algorithms (PageRank, Louvain, shortest paths)
  — don't hand-roll graph algorithms in queries.

## Verification

Model review: whiteboard photo attached, relationship-type catalog with
definitions, super-node analysis done, PROFILE output for hot queries, scale
story stated. A graph modeled like tables (foreign-key properties instead
of relationships) fails review.

## Pairs with

- `seven-databases-tour` (when graph wins),
  `fowler-analysis-patterns` (temporal modeling),
  `ir-vector-space-ranking` (hybrid graph+vector retrieval),
  `data-mining-concepts-techniques` (graph algorithms).
