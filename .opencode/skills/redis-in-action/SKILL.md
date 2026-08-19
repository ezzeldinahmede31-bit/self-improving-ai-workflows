---
name: redis-in-action
description: Applies Josiah Carlson's Redis in Action to building real features on Redis: the data structures (strings, hashes, lists, sets, sorted sets) and their use cases, expiration and caching, pub/sub, transactions, persistence (snapshot and append-only file), replication, and scripting, with the patterns that make Redis fast. Use when the user says 'redis', 'sorted set', 'redis cache', 'redis pub sub', 'redis persistence', 'redis replication', 'leaderboard', 'rate limiter redis', 'Carlson redis', or when a feature maps naturally onto a Redis data structure.
---

# Redis in Action (Josiah L. Carlson)

Redis in Action shows how the Redis data structures solve real problems with speed. This skill applies that structure-first thinking to caches, queues, and counters.

## The data structures

- Strings, hashes, lists, sets, and sorted sets each solve a class of problem; name the structure before the code.
- Sorted sets power leaderboards, ranged scoring, and time-ordered feeds.
- Hashes keep related fields together; lists act as queues; sets handle membership and uniqueness.

## Caching and expiration

- Expiration bounds memory; set a TTL that matches the data's usefulness.
- Cache-aside requires an invalidation policy; stale data is a design decision.
- Cache the hot keys, not everything; the hit ratio tells you if the cache earns its memory.

## Pub/sub and scripting

- Pub/sub delivers messages to subscribers; it is fire-and-forget, not a durable queue.
- Lua scripts run atomically on the server, combining steps without round trips.
- The scripting model protects invariants that multiple operations would break.

## Persistence and replication

- RDB snapshots and the append-only file trade durability against performance; choose by the recovery requirement.
- Replication gives read scaling and failover; the replica lag is a real signal.
- A cache loses nothing when it restarts; a store must plan for recovery.

## Pairs with
database-internals-engines, database-reliability-engineering, building-data-heavy-applications, rate-limit-and-cost-guard, state-machine-persistence
