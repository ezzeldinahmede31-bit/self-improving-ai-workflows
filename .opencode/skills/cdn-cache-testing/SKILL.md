---
name: cdn-cache-testing
description: "CDN and cache testing distilled. Use when testing cache hits, invalidation, TTLs, edge behavior, stale-while-revalidate."
---

# CDN Cache Testing

## Purpose

Prove caching behaves: hit ratios, TTL correctness, invalidation paths, edge versus origin consistency, stale-serving policy.

## When to use

Use when the user says 'CDN test', 'cache hit', 'invalidation', 'TTL', 'edge cache', 'stale while revalidate', 'cache purge'.

## Steps

1. Assert cache headers (age, hit/miss markers) per asset class.
2. Test TTL expiry plus early invalidation on deploy.
3. Verify purge paths reach all edges before traffic shifts.
4. Check stale-serving policy during origin outages.
5. Load through the edge to confirm offload ratios hold.

## Anti-patterns

- Personalized content cached and served across users.
- Purges assumed instant without verification.
- No TTL review, so stale content lingers for days.
- Testing origin only and declaring CDN coverage.

## Example

```python
r1 = get("/static/app.js"); r2 = get("/static/app.js")
assert r2.headers.get("x-cache") == "HIT"
```

## Verification

Headers asserted per class, invalidation verified post-deploy, stale policy proven, offload measured.

## Pairs-with

frontend-perf-testing, high-performance-browser-networking, performance-testing-k6-jmeter, webhook-automation.
