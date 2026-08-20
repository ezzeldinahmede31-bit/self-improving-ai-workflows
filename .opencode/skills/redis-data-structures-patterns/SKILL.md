---
name: redis-data-structures-patterns
description: Applies the data-structure recipes of Redis in Action (Josiah Carlson) to build real features on Redis: strings, hashes, lists, sets, and sorted sets matched to use cases such as caching, queues, leaderboards, rate limiting, and counters, plus expiration, pub/sub, persistence, and the atomicity rules that keep operations correct. Use when the user says 'Redis', 'sorted set', 'leaderboard', 'Redis cache', 'Redis queue', 'rate limiter Redis', 'pub sub', 'Redis persistence', 'Redis transactions', 'Carlson Redis', or when a feature maps naturally onto a Redis structure.
---

# Redis in Action: Data Structures and Patterns

Redis wins because each data structure is a ready-made answer to a recurring problem. Carlson's Redis in Action shows how to choose the right structure for a feature, keep the operations atomic, and make the data survive a restart. This skill encodes that mapping so a feature is built on Redis the way its designers intended.

## The Core Structures
- Strings hold any byte string and drive simple counters, tokens, and small caches; they support atomic increment for tally-style counters.
- Hashes hold a map of fields on one key and are ideal for a row-like object you update field by field.
- Lists are ordered sequences with push and pop on both ends — a natural queue or a bounded history.
- Sets are unordered unique collections with membership tests, unions, and intersections; use them for tags, friends, and deduplication.

## Sorted Sets for Rankings
- A sorted set pairs a member with a score and keeps the members ordered by score.
- Leaderboards, top-N queries, and priority queues are all native reads: fetch by rank or by score range in one call.
- Update a member's score atomically to move it in the ranking without a read-modify-write race.
- Use sorted sets whenever the ordering is the point of the data, not just the storage.

## Caching, Queues, and Rate Limiting
- Cache hot results under a key with an expiration so the data refreshes and evicts itself.
- Build a reliable work queue with list push/pop, plus a delayed or retry list for failed work.
- Rate limiting maps to a fixed-window or sliding-window counter stored per key with expiration, using atomic increments.
- Keep each operation atomic (INCR, LPUSH, ZADD, SETEX) so concurrent clients do not corrupt shared state.
- Treat Redis as a cache or a fast store, never as the only system of record unless the persistence guarantees match the requirement.

## Expiration, Pub/Sub, and Persistence
- Expiration (EXPIRE, TTL, SETEX) is the automatic eviction mechanism for caches, sessions, and one-time tokens.
- Pub/Sub delivers messages to subscribed channels in near real time; it is fire-and-forget, so durable queues need the list pattern instead.
- Persistence offers snapshots and append-only logs; choose the mode by how much data loss a restart may accept.
- Transactions (MULTI/EXEC) queue commands to run atomically as a group — the right tool for a multi-step update that must not interleave.
- Design keys with a consistent prefix and a naming convention so the key space stays navigable and evictable in slices.

## Pairs with
redis-in-action, building-data-heavy-applications, state-machine-persistence, rate-limit-and-cost-guard, enterprise-integration-patterns
