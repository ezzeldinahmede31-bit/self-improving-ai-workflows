---
name: loop-batch-pagination
description: "Processes large datasets via bounded loops, cursor pagination, sized batches. Use for big data."
---

# Loops, Batching, and Pagination

Big data breaks naive fetch-all.

## Workflow
1. Choose pagination: cursor / page token (never unbounded).
2. Size batches to slowest consumer limits.
3. Persist resume point after each batch.
4. Cap iterations defensively.

## Core Rules
- Aggregate results explicitly.

## Pairs with
- `geewax-pagination-filtering-masks`, `building-data-heavy-applications`, `api-design-patterns`
