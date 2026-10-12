---
name: streaming-systems
description: "Applies Tyler Akidau's Streaming Systems to build correct stream/batch data pipelines: the event-time vs processing-time distinction, watermarks and late data, the Beam Model (what / where / when / how) with windowing and triggers, exactly-once and effective-once semantics, out-of-order handling, and the unifying view that batch is a special case of streaming. Use when the user says 'streaming pipeline', 'stream processing', 'watermark', 'event time', 'late data', 'windowing', 'exactly once', 'out-of-order events', 'Flink', 'Kafka Streams', 'batch vs stream', 'replay', 'lambda architecture', 'unbounded data', or when building any pipeline where events arrive late, out of order, or from unbounded sources. Pairs with: designing-event-driven-systems, data-analysis, distributed-systems-concepts-design, cloud-native-patterns, qdrant-ops."
---

# Streaming Systems

Akidau's book: streaming is not a niche — it is the general case, and batch is a
special case of it (bounded stream). The real difficulty is *time*: events carry
their own timestamps, arrive late and out of order, and pipelines must decide
when to commit results.

## When to use

- Building pipelines over unbounded/real-time data.
- Designing any aggregation that must handle late or out-of-order events.
- Choosing stream vs batch processing for a workload.

## The two clocks
- **Event time**: when the event actually happened (in the payload).
- **Processing time**: when the pipeline sees it.
- All correct pipelines must reason about event time, because processing time
  lies about causality and ordering. A time-based aggregation over event time
  needs a way to know when it is "safe" to emit — that is what a watermark does.

## Watermarks and late data
- A **watermark** is a bound: "everything with event time before W has been seen."
- Choose watermarking strategy: perfect (never wrong, never finishes for unbounded
  data), heuristic (finishes, sometimes marks too early), or an allowed lateness
  that buys more time for stragglers.
- Decide what happens to **late data**: drop, replay, or side-channel. Never
  silently merge late events into already-emitted windows without deciding the
  policy.

## The Beam model: what / where / when / how
1. **What** results are computed — the transformation/aggregation.
2. **Where** in event time results are grouped — the windowing (fixed, sliding,
   session).
3. **When** results are emitted — the trigger (on watermark advance, on a batch threshold, on
   processing time, or combinations) and the accumulation mode (discarding,
   accumulating, accumulating-and-retracting).
4. **How** refinements relate — how multiple emissions of a window combine.
Every real streaming system (Flink, Beam, Kafka Streams, Spark Structured
Streaming) is a concrete realization of these four knobs — when a design feels
hard, map it back to the four questions.

## Correctness semantics
- **At-least-once + dedupe**: safe default; make the downstream sink idempotent.
- **Exactly-once / effective-once**: requires transactional coordination or
  stateful dedup at the boundary. State exactly what each stage provides.
- The pipeline's end-to-end guarantee is the *weakest link*: an exactly-once
  pipeline writing to a non-idempotent sink is not exactly-once.
- **Reprocessing is a feature**: the ability to replay an input (bounded replay
  from a log) is how you recover from bugs — design for it, don't fight it.

## Practical rules
- Prefer event time for analytics; use processing time only for latency-bound
  monitoring.
- Keep state in the pipeline engine (managed, checkpointed), not in memory.
- Test with injected disorder and lateness — a pipeline that only passes on
  sorted input is not a streaming pipeline.
- Document the watermark policy, late-data policy, and delivery semantics per
  pipeline before shipping.

Pairs with: designing-event-driven-systems (event backbone), data-analysis
(aggregation design), distributed-systems-concepts-design (ordering), qdrant-ops
(streaming ingestion into vector stores).