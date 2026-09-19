---
name: api-testing-contract-patterns
description: "API testing patterns distilled. Use when testing REST or GraphQL APIs, status contracts, schema validation, Postman collections, consumer-driven contracts with Pact."
---

# API Testing and Contract Patterns

## Purpose

Test APIs at the right layers: contract (schema/status), functional (behavior), consumer-driven (Pact), plus negative and versioning coverage.

## When to use

Use when the user says 'API testing', 'REST test', 'GraphQL test', 'Postman', 'contract test', 'Pact', 'schema validation', 'status code'.

## Steps

1. Assert the contract first: status codes, headers, JSON schema, error envelope.
2. Cover happy path + negative: auth, validation, pagination, idempotency, versioning.
3. Validate data, not just shape: types, ranges, enums, nullability.
4. Add consumer-driven contracts (Pact) for cross-team boundaries.
5. Run collections in CI with environment isolation and seeded data.

## Anti-patterns

- Only 200-OK happy-path checks.
- Asserting full volatile payloads (timestamps, IDs) instead of shapes + key fields.
- Shared mutable staging data causing order-dependent flakes.
- No contract test at service boundaries, only slow E2E.

## Example

Python (requests + jsonschema):

```python
resp = requests.get(f"{BASE}/orders/1", timeout=10)
assert resp.status_code == 200
jsonschema.validate(resp.json(), ORDER_SCHEMA)
```

JS (fetch + zod-style check):

```js
const r = await fetch(`${BASE}/orders/1`);
expect(r.status).toBe(200);
expect(await r.json()).toMatchObject({ id: 1 });
```

## Verification

Schema validated, negative cases green, Pact verified both sides, CI run hermetic and repeatable.

## Pairs-with

webapp-testing, end-to-end-workflow-testing, validation-gate-data-quality, retry-backoff-jitter.
