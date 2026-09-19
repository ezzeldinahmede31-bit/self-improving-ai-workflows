---
name: gourley-http-definitive
description: "Masters HTTP end to end: messages, caching, auth, and performance. Use when the user says 'HTTP caching', 'cache validators', 'ETag', 'conditional request', 'HTTP auth', 'cookies', 'proxies', 'content negotiation', 'HTTP/1.1 semantics', 'Gourley', or when the web misbehaves on the path linking client and server."
---

# Gourley HTTP Definitive Guide

Distilled from Gourley & Totty *HTTP: The Definitive Guide*: the web is
messages + caches + intermediaries — master the semantics once and every
API, CDN, and proxy problem becomes legible.

## Purpose

Debug and design anything HTTP: correct caching, auth, content negotiation,
and intermediary behavior — from first principles of the message format.

## The essentials (in debug order)

1. **Messages.** Start line + headers + body; methods as intent (GET safe/
   idempotent, PUT idempotent-not-safe, POST neither — design APIs to honor
   this); status codes as machine-readable contracts (2xx/3xx/4xx/5xx + the
   load-bearing specifics: 201+Location, 304, 401 vs 403, 409, 429+Retry-After).
2. **Caching (the money chapter).** Freshness (Expires/Cache-Control max-age,
   heuristic) vs validation (ETag/Last-Modified + If-None-Match → 304);
   private vs shared directives; Vary correctness (vary on what changes the
   representation or serve poisoned cache); invalidation discipline on
   writes. Most "stale data" bugs are cache-directive bugs — read the headers
   first.
3. **Intermediaries.** Proxies (forward/reverse), gateways, tunnels
   (CONNECT), CDNs as managed reverse proxies. X-Forwarded-* trust (only
   from YOUR edge), Via loops, and the rule: each intermediary must preserve
   end-to-end semantics unless explicitly transforming (and saying so).
4. **Identity and state.**    Auth schemes (Basic over TLS only, Digest challenge-response, Bearer tokens, cookies with Secure/HttpOnly/SameSite); session
   fixation/session hijack defenses; content negotiation (Accept* headers +
   server-driven vs agent-driven) done without breaking caches.
5. **Performance realities.** Persistent connections + pipelining limits
   (head-of-line blocking is why HTTP/2 multiplexes and HTTP/3 leaves TCP);
   range requests for resume/parallel fetch; compression (gzip/br) with
   cache-vary discipline. Know which HTTP version behavior you rely on —
   version surprises break assumptions silently.

## Debug protocol (same order every incident)

Reproduce with curl -v (see the exact bytes) → classify: message error?
cache error? intermediary error? auth error? → fix at the responsible layer
(origin, cache policy, proxy config) → regression test with the captured
exchange checked in.

## Verification

HTTP work ships with: captured request/response pairs for the fixed behavior,
cache headers justified per resource (freshness + validation story),
intermediary trust documented. "Works in my browser" without the bytes is
anecdote.

## Pairs with

- `high-performance-browser-networking` (modern transports),
  `web-security-browser-internals` (browser-side attacks),
  `api-design-patterns` (API semantics), `webhook-automation` (HTTP hooks).
