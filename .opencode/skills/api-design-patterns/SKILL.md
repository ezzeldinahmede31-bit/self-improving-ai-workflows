---
name: api-design-patterns
description: "Applies JJ Geewax's API Design Patterns to design professional, evolvable REST/HTTP APIs: resource-oriented design with the standard methods (get/list/create/update/delete), long-running operations, pagination, filtering, field masks, error models, idempotency, versioning, and backwards-compatibility strategy. Use when the user says 'design an API', 'API design patterns', 'resource-oriented API', 'standard methods', 'long-running operations', 'pagination design', 'field masks', 'idempotency key', 'how to version my API', 'backwards compatible API change', 'error model', 'retry policy', or when building an API that must last years without breaking clients. Pairs with: api-integration, zapier-system-cloner, domain-modeling-functional, proactive-spec-expander."
---

# API Design Patterns

Geewax's patterns make APIs consistent, extensible, and safe to evolve. The rules:
model resources, give every resource the same standard methods, and design for
change (additions are safe, changes to meaning are not).

## When to use

- Designing a new HTTP/REST API or SDK surface.
- Reviewing an existing API for consistency and evolvability.
- Adding pagination, versioning, long-running operations, or error handling to an
  existing service.

## The patterns

### 1. Resource-oriented design + standard methods
- Model the domain as resources (nouns) with stable identifiers; design with
  `get`, `list`, `create`, `update` (partial), `delete`, and `search` as the uniform
  verbs on each resource.
- Standard methods make the API learnable: one set of semantics applies everywhere.

### 2. List = pagination + filtering, always
- `list` returns a page of results plus a `nextPageToken` (opaque cursor), never
  unbounded result sets.
- Filtering uses a single structured query parameter; ordering is explicit.
- Pagination tokens keep clients stable as the dataset grows.

### 3. Long-running operations
- Any operation that may exceed a request timeout returns a resource representing
  the operation (id, state, progress), which the client polls.
- The operation resource carries the eventual result or error — never make the
  client guess.

### 4. Errors and idempotency
- Use a small, consistent error model (code + message + details), not ad-hoc error
  strings.
- Mutating operations are idempotent: a client-supplied request id lets retries be
  safe — retries must never create duplicates (see `zapier-system-cloner` parity
  thinking and the n8n precision gate D rules).

### 5. Versioning and evolution
- Backwards-compatible changes are the norm: adding fields/methods is safe; changing
  meaning or deleting is breaking.
- Version the API when breaking change is unavoidable; keep the old version alive
  with a documented migration path.
- Field masks let clients request only what they need — smaller payloads, less
  coupling.

## Verification
- Every resource exposes the standard methods; every list is paginated; every long
  operation is representable as a resource.
- Walk the client scenario: retry the same create twice with the same id — exactly
  one resource exists.
- Confirm the API doc states the error model and the versioning policy.

## Pairs with
- `api-integration` — event-driven/wiring patterns around the API surface.
- `zapier-system-cloner` — mapping third-party APIs onto n8n with the same semantics.
- `domain-modeling-functional` — domain types shaping the resource model.
- `proactive-spec-expander` — expanding an API brief into the full pattern set.