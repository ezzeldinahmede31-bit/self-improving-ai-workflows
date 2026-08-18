---
name: building-data-heavy-applications
description: "Encodes the engineering standards for building applications that handle large data volumes reliably: batching and streaming input, pagination and cursors, caching layers, backpressure and rate control, idempotent writes, retry and timeout discipline, and data observability — the patterns that keep a data-heavy service stable under load. Use when the user says 'handle large data', 'batch processing', 'pagination', 'cursor', 'cache the results', 'backpressure', 'idempotent write', 'retry policy', 'data-heavy application', 'process millions of rows', 'rate limiting a pipeline', or when a service must process big volumes without collapsing. Pairs with: data-intensive-application-design, rate-limit-and-cost-guard, release-it-production-hardening, state-machine-persistence, enterprise-integration-patterns."
---

# Building Data-Heavy Applications

The premise: applications that process large data volumes fail not from one big
mistake but from many small ones — unbounded memory, one-shot pagination,
duplicated writes, and silent retries. This skill encodes the defensive patterns.

## When to use

- Any service that ingests or transforms large volumes of data.
- Adding caching, batching, pagination, or retries to an existing path.
- Auditing a data-heavy pipeline for the classic failure modes.

## The core patterns

1. **Batch, do not loop one-by-one** — round-trips are the enemy; batch reads and
   writes to the underlying store (see `database-internals-engines`).
2. **Paginate with cursors, not offsets** — offsets drift when data changes;
   cursor/keyset pagination is stable and fast.
3. **Cache with discipline** — cache only what is expensive and read-many; set
   TTLs and invalidation; treat the cache as an optimization, never the source of
   truth.
4. **Apply backpressure** — a consumer that cannot keep up must push back or
   buffer, not silently drop; cap in-flight work.
5. **Make writes idempotent** — every write carries a client-generated key; a
   retried write must not duplicate (see `state-machine-persistence`).
6. **Bound retries** — retry with exponential backoff plus jitter; stop after a
   ceiling; route to a dead-letter path, never retry forever.
7. **Set timeouts everywhere** — every external call gets a timeout; slow
   dependencies must fail fast, not hang the caller (see
   `release-it-production-hardening`).

## Observability for data paths

- Track row/event volume per step, latency percentiles, and error rates; a volume
  drop is often the first signal of breakage.
- Log a correlation ID that threads through the whole path so one request is
  traceable across steps.
- Alert on freshness and on quality, not only on exceptions (see
  `data-pipelines-pocket-reference`).

## Capacity thinking

- Size for the peak, not the average; load-test the write path with realistic data
  sizes.
- Understand the storage engine's write amplification and memory behavior before
  promising throughput (see `database-internals-engines`,
  `computer-systems-programmers-perspective`).

Pairs with: data-intensive-application-design (trade-offs),
rate-limit-and-cost-guard (cost ceilings), release-it-production-hardening
(stability), state-machine-persistence (idempotency), enterprise-integration-
patterns (messaging).