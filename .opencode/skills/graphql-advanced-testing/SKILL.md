---
name: graphql-advanced-testing
description: "Advanced GraphQL testing distilled. Use when testing GraphQL schemas, queries, mutations, fragments, error paths, N-plus-1 guards."
---

# GraphQL Advanced Testing

## Purpose

Test GraphQL APIs beyond happy queries: schema conformance, fragment reuse, mutation side effects, error extensions, depth and complexity limits.

## When to use

Use when the user says 'GraphQL test', 'schema test', 'mutation test', 'fragment', 'GraphQL errors', 'query depth'.

## Steps

1. Validate the served schema against the checked-in schema file.
2. Test queries for shape plus data correctness with fragments.
3. Test mutations for side effects and idempotency keys where offered.
4. Assert error paths: `errors` entries with codes, `data` nullability per spec.
5. Probe depth, complexity, and rate limits with oversized queries.

## Anti-patterns

- Asserting full introspection dumps as snapshots.
- Testing through HTTP status only (GraphQL errors ride on 200).
- Mutations tested without verifying persisted side effects.
- No depth limiting while exposing the endpoint publicly.

## Example

Python:

```python
r = gql("{ order(id: 1) { id total } }")
assert "errors" not in r
assert r["data"]["order"]["id"] == 1
```

## Verification

Schema diff clean, fragments exercised, error codes asserted, abuse queries limited.

## Pairs-with

api-testing-contract-patterns, rest-assured-patterns, grpc-contract-testing, security-testing-owasp-fuzz.
