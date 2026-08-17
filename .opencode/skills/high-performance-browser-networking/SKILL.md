---
name: high-performance-browser-networking
description: "Applies Ilya Grigorik's High Performance Browser Networking to build fast web experiences: the full client-server path (TCP/TLS handshakes, HTTP/1.1 vs HTTP/2 vs HTTP/3, WebSockets, server-sent events), the critical rendering path and browser optimizations (preconnect, prefetch, preload, resource hints), asset delivery (caching, compression, CDN/edge), and the mobile/network reality (latency, bandwidth, RTT on cellular). Use when the user says 'make my website fast', 'why is my page slow', 'HTTP/2', 'HTTP/3', 'TLS handshake', 'TCP slow start', 'preconnect', 'preload', 'critical rendering path', 'performance budget', 'CDN', 'caching strategy', 'web performance', 'latency', 'RTT', or when optimizing any web app's load time and network behavior. Pairs with: computer-systems-programmers-perspective, tcp-ip-illustrated, impeccable, persistent-browser-automation, systems-performance-profiling."
---

# High Performance Browser Networking

Grigorik's core lesson: **latency is the bottleneck, not bandwidth.** On modern
networks the round-trip time (RTT) dominates — every extra network round trip
adds a fixed delay regardless of how much bandwidth you have. Fast web apps are
built by minimizing round trips and making the best use of each one.

## When to use

- Auditing or improving web page/API performance.
- Choosing protocols or transport for a real-time feature.
- Setting performance budgets and caching/CDN strategy.

## The transport layer reality
- **TCP** establishes connections with a multi-RTT handshake and ramps up via
  **slow start** — new connections are expensive and start slow. Reuse connections,
  don't open new ones per request.
- **TLS** adds another handshake (1-2 RTTs). Use session resumption/0-RTT where
  allowed; the cryptographic cost is minor compared to the round trips.
- **HTTP/1.1** has head-of-line blocking and connection limits — one file per
  connection at a time. **HTTP/2** multiplexes many streams over one connection
  (removing most of the blocking, but a lost packet still stalls the stream).
  **HTTP/3/QUIC** moves to UDP with per-stream independence — best for lossy
  mobile networks.
- **WebSockets**: persistent bidirectional channel for interactive features; use
  for real-time messaging, not as a general transport. **Server-Sent Events**
  (SSE) is a simpler, retry-friendly one-way push over HTTP.

## Making pages fast

### The critical path
- The browser must parse HTML, block on CSS, run JS, and render — measure the
  **critical rendering path** (what blocks first paint). Order, size, and
  deferral of CSS/JS change perceived speed more than total bytes.
- **Performance budget**: set a maximum for time-to-first-paint and load on a
  mid-range mobile connection; treat regressions as bugs.

### Reduce round trips
- **Preconnect / dns-prefetch / preload / prefetch**: hint the browser to start
  work (DNS, TCP, TLS) early for origins and resources you know you will need.
  Do not overuse — each hint has a cost.
- Inline or preload critical CSS/JS; defer the rest. **Lazy-load** below-the-fold
  and non-critical assets.
- Bundle and compress: fewer, smaller requests beat many large ones (within the
  cache story — see caching).

### Cache and edge
- Make caching explicit: cache headers, immutable hashed filenames for long-lived
  assets, and a correct staleness/revalidation policy (ETag, max-age). A cache
  hit skips the network entirely.
- Push static assets and static generation to a **CDN/edge** close to users —
  RTT to the user is cut dramatically; APIs can follow with edge functions.
- For APIs: use connection reuse, compression, and (where data permits) streaming
  so time-to-first-byte and total transfer stay low.

## The mobile reality
- Mobile networks add latency spikes and packet loss; assume high RTT and
  variability. Design for degraded networks (retry with backoff, offline
  tolerance) and test under throttling — a feature that works on fiber but breaks
  on 3G is not done.

Pairs with: tcp-ip-illustrated (protocol mechanics underneath), computer-systems-
programmers-perspective (hardware reality), impeccable (UI polish/perception),
systems-performance-profiling (measurement discipline).