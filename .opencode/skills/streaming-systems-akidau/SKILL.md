---
name: streaming-systems-akidau
description: Applies Tyler Akidau, Slava Chernyak, and Reuven Lax's Streaming Systems to build correct stream/batch data pipelines: the event-time vs processing-time distinction, watermarks and late data, the Beam Model (what / where / when / how) with windowing and triggers, exactly-once and effective-once semantics, out-of-order handling, and the unifying view that batch is a special case of streaming. Use when the user says 'streaming pipeline', 'stream processing', 'watermark', 'event time', 'late data', 'windowing', 'exactly once', 'out-of-order events', 'Flink', 'Kafka Streams', 'batch vs stream', 'replay', 'lambda architecture', 'unbounded data', or when building any pipeline where events arrive late, out of order, or from unbounded sources. Pairs with: designing-event-driven-systems, data-analysis, distributed-systems-concepts-design, cloud-native-patterns, qdrant-ops.
---

# Streaming Systems (Akidau, Chernyak, Lax) Skill

## Core Philosophy: Batch is a Special Case of Streaming

> The Beam Model unifies batch and streaming: **What** (transformation), **Where** (windowing), **When** (triggers), **How** (accumulation). Streaming handles unbounded data with correctness; batch is just bounded streaming.

**Two Time Domains (Critical Distinction):**
| Domain | Definition | Challenge |
|--------|------------|-----------|
| **Event Time** | When the event actually occurred | Out-of-order, late data, completeness |
| **Processing Time** | When the event is processed | Simple, but **wrong** for event-time correctness |

**Never use processing time for event-time logic** — leads to incorrect results when data is late.

---

## The Beam Model: Four Questions

| Question | Concept | Streaming Answer |
|----------|---------|------------------|
| **What** | Transformation | PTransform (map, filter, GroupByKey, Combine) |
| **Where** | Windowing | Fixed, sliding, session, custom windows |
| **When** | Triggers | Watermark-based, processing-time, element-count, composite |
| **How** | Accumulation | Discarding, accumulating, accumulating & retracting |

---

## Watermarks: The Heart of Event-Time Correctness

**Definition**: Monotonically increasing timestamp = "I've processed all events with timestamp < watermark"

| Watermark Type | Guarantee | Latency | Use Case |
|----------------|-----------|---------|----------|
| **Perfect** | No late events ever | High (wait for stragglers) | Known-finite sources, tests |
| **Heuristic** | Allows late events | Low (bounded wait) | Production (Kafka, Pub/Sub, Kinesis) |

### Watermark Propagation in Pipelines
```
Source → [Transform 1] → [Transform 2] → ... → Sink
WM: t₁      WM: min(t₁, t₁')    WM: min(t₁', t₂')   ...
```
- Each stage's output WM = min(input WMs, event times of non-late elements)
- **Windowing adds delay**: Tumbling window of size W → next stage WM lags by W
- **Processing-time WMs** track system delays separately

---

## Windowing: Bounded Chunks from Unbounded Streams

| Window Type | Definition | Trigger | Use Case |
|-------------|------------|---------|----------|
| **Tumbling** | Fixed, non-overlapping intervals | Watermark passes end | Hourly aggregates, daily rollups |
| **Sliding** | Fixed length, fixed offset | Watermark passes end | Moving averages, 5-min every 1-min |
| **Session** | Activity gaps define boundaries | Gap timeout + watermark | User sessions, burst detection |
| **Custom** | Arbitrary grouping (key, predicate) | User-defined | Business-specific grouping |

### Window Completeness & Late Data
```
Event Time ─────────────────────────────────────────>
WM(t=10) ───────────────────────────>   (window [0,10) closes)
Late Event (t=8) arrives at processing time t=15
├── Allowed lateness: 5 min → included (retraction emitted)
└── Beyond allowed lateness → dropped / sent to DLQ
```

---

## Triggers: When to Materialize Results

| Trigger Type | Fires When | Latency vs Completeness |
|--------------|------------|-------------------------|
| **Watermark** | WM passes window end | Complete, higher latency |
| **Processing-time** | Wall-clock interval | Low latency, possibly incomplete |
| **Element count** | N elements in window | Tunable |
| **Composite** | AND/OR of above | Custom trade-offs |
| **Early + Late** | Speculative early + final | Best of both |

---

## Exactly-Once Semantics

| Level | Definition | Implementation |
|-------|------------|----------------|
| **At-least-once** | Every record processed ≥1 time | Default (retries on failure) |
| **Effectively-once** | Output = exactly-once (idempotent sinks) | Idempotent writes + transactional sources |
| **Exactly-once** | End-to-end, no duplicates anywhere | Distributed transactions (Two-phase commit) |

**Practical path**: Effective-once via:
1. **Transactional sources** (Kafka transactions, Kinesis checkpointing)
2. **Idempotent sinks** (upsert with keys, deduplication)
3. **Deterministic processing** (no non-deterministic functions)

---

## Lambda vs Kappa Architecture

| Architecture | Structure | Problem |
|--------------|-----------|---------|
| **Lambda** | Batch layer + Speed layer + Serving layer | Dual pipeline maintenance, consistency |
| **Kappa** | **Single streaming pipeline** (replay for reprocessing) | Simpler, unified logic |

**Kappa wins when**: Streaming system achieves correctness + replay capability (Beam, Flink, Kafka Streams, Spark Structured Streaming).

---

## Out-of-Order Handling Checklist

For any streaming pipeline:
- [ ] **Event-time** used for all windowing/aggregation
- [ ] **Watermark strategy** defined (heuristic with allowed lateness)
- [ ] **Allowed lateness** configured per window (e.g., 10 min)
- [ ] **Late data handling**: Retractions emitted / side output to DLQ
- [ ] **Monitoring**: Watermark latency, event-time lag, late event rate
- [ ] **Exactly-once**: Transactional source + idempotent sink

---

## Decision Framework

| Requirement | Beam Model Answer |
|-------------|-------------------|
| "Aggregate per user per hour" | **What**: CombinePerKey(Sum) • **Where**: FixedWindow(1h) • **When**: Watermark • **How**: Accumulating |
| "Moving average 5min/1min" | **Where**: SlidingWindow(5m, 1m) |
| "User sessions (30min gap)" | **Where**: Sessions(30min gap) |
| "Detect fraud in real-time" | **When**: Processing-time trigger (low latency) + event-time correction |
| "Reprocess last 30 days" | Kappa: replay from source with same pipeline |
| "Exactly-once billing" | Transactional Kafka source + idempotent DB upsert |

---

## Platform Mapping (Concept → Implementation)

| Concept | Apache Beam | Apache Flink | Kafka Streams | Spark Structured Streaming |
|---------|-------------|--------------|---------------|----------------------------|
| PTransform | Native | DataStream API | KStream/KTable | DataFrame API |
| Windowing | Window.into() | WindowAssigner | Windowed<KStream> | window() |
| Watermark | WithWatermarks() | WatermarkStrategy | TimestampExtractor | watermark() |
| Triggers | Trigger.once() | Trigger | Suppressed/emit | trigger() |
| Exactly-once | Portable runner | Checkpointing + Kafka transactions | EOS (exactly-once semantics) | ForeachBatch + idempotent write |

---

## Anti-Patterns to Avoid

- ❌ **Processing-time windows for event-time logic** (wrong results with late data)
- ❌ **No watermarks** (windows never close, memory grows unbounded)
- ❌ **No allowed lateness** (drops all late data silently)
- ❌ **Lambda architecture** (dual pipeline drift)
- ❌ **Non-deterministic UDFs** (breaks exactly-once replay)
- ❌ **Unbounded state without TTL** (OOM on key cardinality)
- ❌ **Ignoring watermark lag monitoring** (silent correctness failures)

---

## Trigger Phrases

`streaming pipeline`, `stream processing`, `watermark`, `event time`, `late data`, `windowing`, `exactly once`, `out-of-order events`, `Flink`, `Kafka Streams`, `batch vs stream`, `replay`, `lambda architecture`, `unbounded data`

---

## Pairings

- `designing-event-driven-systems` — event-driven architecture patterns
- `data-analysis` — statistical validation of streaming results
- `distributed-systems-concepts-design` — Coulouris' distributed theory
- `cloud-native-patterns` — resilience in streaming
- `qdrant-ops` — vector search as streaming sink