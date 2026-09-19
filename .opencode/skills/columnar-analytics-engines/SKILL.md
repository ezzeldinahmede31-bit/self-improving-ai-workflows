---
name: columnar-analytics-engines
description: "Runs analytical queries fast on columnar stores: compression, vectorization, and late materialization. Use when the user says 'columnar database', 'C-Store', 'Vertica', 'ClickHouse', 'DuckDB', 'compression encoding', 'vectorized execution', 'late materialization', or when OLAP scans must fly."
---

# Columnar Analytics Engines

Distilled from the C-Store/Vertica/MonetDB lineage (Stonebraker et al.):
row stores serve transactions; analytics wants columns — compressed,
scanned in vectors, assembled late.

## Purpose

Design and query columnar systems so full-table scans become memory-speed
operations instead of I/O-bound crawls.

## The four wins (each is an order of magnitude when it applies)

1. **Column layout.** Store each column contiguously: scans read only needed
   attributes (a 100-column table queried for 3 columns reads 3% of the
   data). Sort key / projection design IS the physical design — choose by
   query patterns, not by source schema.
2. **Compression that queries.** Sorted/run-length, dictionary, bit-packing,
   delta, LZ variants — picked per column distribution. Operate DIRECTLY on
   compressed data where possible (decompress only at output); compression
   ratio and scan speed are the same decision.
3. **Vectorized execution.** Process batches (vectors of ~1K values) through
   tight loops instead of per-tuple iterators: cache-friendly, SIMD-able,
   branch-predictable. The Volcano tax disappears.
4. **Late materialization.** Carry positions (row IDs) through joins/filters,
   fetch full rows only for survivors. Selective queries avoid touching most
   bytes entirely. Zone maps/min-max indexes prune whole blocks before scans.

## Workload honesty

- Columnar wins: scans, aggregations, selective filters over wide tables.
- Columnar loses: point lookups/updates (writes go to a row-oriented WOS /
  delta store, merged out later — know your engine's merge policy).
- Small data fits anywhere; columnar earns its keep past memory scale or
  under concurrency.

## Verification

Analytics review ships with: projection/sort design justified by queries,
encoding per high-volume column, a benchmark showing scan pruning working
(EXPLAIN with block elimination), and the write-path story (WOS/delta +
merge cadence). "It is columnar so it is fast" is rejected as analysis.

## Pairs with

- `redbook-db-architecture` (engine structure),
  `kimball-dimensional-modeling` (what sits on top),
  `systems-performance-profiling` (measuring scans),
  `python-for-data-analysis` (local OLAP practice).
