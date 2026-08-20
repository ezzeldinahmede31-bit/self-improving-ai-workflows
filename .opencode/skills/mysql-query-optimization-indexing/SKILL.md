---
name: mysql-query-optimization-indexing
description: Applies the indexing and query-optimization chapters of High Performance MySQL (Schwartz, Zaitsev, Tkachov) to make queries fast: choosing the right index structure for the access path, composite index column order, covering indexes, reading EXPLAIN, and the query anti-patterns that force full table scans. Use when the user says 'slow query', 'mysql index', 'composite index', 'covering index', 'EXPLAIN', 'query plan', 'optimizer', 'index order', 'how to make this query fast', 'High Performance MySQL', or when a query must be diagnosed and made efficient.
---

# High Performance MySQL: Indexing and Query Optimization

The single largest performance lever in MySQL is the index. High Performance MySQL treats indexing as a design activity — match the index to the access path the query actually needs — and turns query analysis into a reading of EXPLAIN. This skill encodes that decision procedure for slow-query diagnosis and index design.

## Index Structure Choices
- Understand the three index types: B-tree (general-purpose, ordered lookups and ranges), hash (equality only, in-memory and MEMORY tables), and full-text (text search).
- A B-tree index supports prefix lookups, range scans, and ordered access, which is why it is the default for most workloads.
- Match the index to the operation: equality, range, sort, and covering reads each want a slightly different structure.
- Do not index every column; each index costs writes, so index what the queries actually filter on.

## Composite Indexes
- A composite index on multiple columns helps only if the query uses a leftmost prefix of the columns.
- Order the columns by cardinality and by the query's equality-versus-range needs: put equality columns first, range columns last.
- A composite index can serve several query shapes if the leading columns are shared; plan the set of indexes as a whole.
- Adding a column to an index to make it a covering index is often cheaper than creating a second index.

## Covering Indexes and EXPLAIN
- A covering index satisfies the query from the index alone, skipping a read of the data row.
- Read EXPLAIN for the access type: ref and range are good, ALL is a full scan, and Using index means covering.
- When EXPLAIN shows Using temporary or Using filesort, the query needs an index that provides the ordering or grouping.
- Confirm with a benchmark, not a guess: change the index and measure the same query under a realistic load.

## Query Anti-Patterns
- Avoid functions or arithmetic on indexed columns in the WHERE clause; they disable index use on that column.
- Avoid leading wildcards like LIKE with a prefix wildcard, which cannot use the index.
- Beware type mismatches and implicit casts that force a scan even when a good index exists.
- Select only the columns needed; a narrower result set reduces I/O and improves index coverage.
- Watch OR conditions that span two different indexed paths — the optimizer may fall back to a scan.

## Pairs with
high-performance-mysql, database-management-systems, database-internals-engines, systems-performance-profiling, postgresql-up-and-running
