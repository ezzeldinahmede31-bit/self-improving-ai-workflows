---
name: restful-web-apis
description: Applies Richardson & Amundsen's RESTful Web APIs to design APIs around resources and their representations — the maturity model from plain HTTP to hypermedia, URI design, media types and content negotiation, HTTP verbs and status codes, caching, versioning, security, and evolvability. Use when the user says 'REST API design', 'design a RESTful API', 'REST maturity model', 'hypermedia', 'HATEOAS', 'content negotiation', 'media type', 'HTTP status codes', 'REST vs RPC', 'API evolvability', 'Richardson REST', 'design web APIs', or when building an HTTP API that must be usable by diverse clients and survive change. Pairs with: api-design-patterns, web-api-design-love, api-integration, webhook-automation, api-versioning-compatibility, n8n-node-configuration.
---
# RESTful Web APIs (Richardson & Amundsen)

Transfers the REST discipline so HTTP APIs are designed around resources and representations rather than remote procedure calls, keeping them simple, cacheable, and evolvable.

## When to use
- Designing any HTTP API meant for third parties, browsers, or long-lived integration.
- Reviewing an existing endpoint style for REST conformance and evolvability.
- Choosing how to model an operation: as a resource action or as a sub-resource.

## The discipline
1. Model the domain as resources; a resource is a concept with a name and a set of representations, not a table or a function.
2. Use the HTTP verbs honestly: GET for safe reads, POST for creation, PUT for full replacement, PATCH for partial update, DELETE for removal; use status codes precisely.
3. Represent resources with media types; prefer structured, self-describing payloads and use content negotiation to evolve formats.
4. Add hypermedia (links) so clients navigate the API from responses instead of hardcoding URLs; this is what makes the API evolvable.
5. Cache aggressively on GET with ETags and cache headers; design for idempotency on writes.

## Evolvability and security
- Additive changes are safe; renaming resources or changing semantics breaks clients, so deprecate with a sunset window instead.
- Secure every endpoint: authentication, authorization per resource, input validation, and rate limiting.

## Verification discipline
- Test with a real HTTP client and verify verbs, codes, and headers; check cache behavior.
- Verify a client can reach a resource using only links from the root.
- Keep a contract test suite that runs on every change to catch breaking drift.

## Pairs with
api-design-patterns, web-api-design-love, api-integration, webhook-automation, api-versioning-compatibility, n8n-node-configuration.