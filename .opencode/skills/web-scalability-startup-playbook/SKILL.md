---
name: web-scalability-startup-playbook
description: "Scale a web product 0 to millions without rewrites: stateless app, read replicas, cache layers, CDN, async queues, sharding. Use when the user says 'الموقع بيقع تحت الضغط', 'scale the website', 'millions of users', 'startup scaling', 'from 1 server to millions', 'traffic spike', or needs the staged 0-to-scale playbook."
---

# Web Scalability Startup Playbook

Distilled from Ejsmont *Web Scalability for Startup Engineers*, Abbott
*Scalability Rules* (50 principles), Abbott & Fisher *Art of Scalability*
(people/process/tech), Souders *High Performance Web Sites*, Grigorik
*High Performance Browser Networking*. Staged growth — each stage buys
10x headroom, no rewrites.

## The stages (never skip one)

1. **One box.** Monolith + single DB. Add request logging + basic
   metrics NOW (you cannot scale what you never measured). Serve
   statics from disk; set cache headers.
2. **Stateless + LB.** Sessions out of process, two app boxes behind a
   load balancer, health checks. First 10x. Axis X
   (`akf-scalability-cube`).
3. **Read scaling.** Read replicas, cache-aside (Redis) for hot reads,
   CDN for geography + statics. 95% cache hit turns 10K DB QPS into
   500. Measure hit ratio per key prefix.
4. **Write scaling.** Queues for anything async (email, thumbnails,
   webhooks), DB connection pooling, batch writes. Peak minus capacity
   times duration = required queue depth.
5. **Data partitioning.** Shard by key when one DB cannot hold the
   working set or write rate. Shard-key discipline + rebalancing story
   first (`ddia-replication-partitioning`, AKF Z axis).
6. **Edge + async everything.** Full-page cache where valid, event
   flows for cross-domain updates, multi-region reads. Every stage
   re-names the NEXT bottleneck — write it down.

## The 50-rules greatest hits

- Clone before you split; split reads from writes; cache at every
  layer with explicit TTLs; async beats faster sync; throttle at the
  edge, not the core; no single point without written acceptance;
  load-test the stage you are IN, not the one you left.

## Verification

Scaling plan ships with: current stage named, bottleneck evidence with
numbers, the ONE next move + its prerequisite, predicted next
bottleneck, rollback story. A plan without measured numbers is a wish.

## Pairs with

- `akf-scalability-cube` (axes), `alex-xu-system-design` (estimation),
  `system-design-production-blueprint` (full design),
  `production-capacity-planning` (sizing math),
  `systems-performance-profiling` (finding the bottleneck),
  `high-performance-browser-networking` (edge latency).
