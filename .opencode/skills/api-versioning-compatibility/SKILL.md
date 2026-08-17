---
name: api-versioning-compatibility
description: Applies the versioning and backwards-compatibility chapter of API Design Patterns (Geewax): evolve an API without breaking existing clients — additive-only changes, field masks and default values for safe growth, explicit deprecation with sunset windows, and choosing a versioning strategy (URI, header, or content negotiation) that matches the contract. Use when the user says 'API versioning', 'version my API', 'backwards compatible', 'breaking change', 'deprecate a field', 'field masks', 'semver for APIs', 'v1 vs v2', 'additive change', 'remove an endpoint', 'compatibility policy', or when an API must keep working for old clients while it grows. Pairs with: api-design-patterns, api-long-running-operations, domain-modeling-functional, zapier-system-cloner.
---

# API Versioning and Compatibility

Transfers the versioning strategy from API Design Patterns (Geewax) to evolving APIs: change APIs safely, communicate deprecations, and keep old clients working while the contract grows.

## When to use
- Adding fields, endpoints, or behavior to a live API.
- Removing or renaming anything that clients depend on.
- Establishing a compatibility policy before the first breaking change is proposed.

## The compatibility-first rules
1. Additive changes are always compatible: new fields, new optional parameters, new endpoints.
2. Changes that break old clients require a deprecation window with a documented sunset date.
3. Every breaking change gets a clear migration path and a machine-readable signal in the response (a header or deprecation field).
4. Prefer additive growth; only version when a change cannot be made additively.

## Versioning strategies
- URI versioning (`/v1/...`): explicit, simple, but duplicates resources over time.
- Header or content-negotiation versioning: keeps the URL stable, clients select the contract.
- Choose one strategy and document it; mixing strategies confuses clients.

## Field growth mechanics
- New optional fields never change the semantics of existing ones.
- Defaults must be chosen so old clients that omit new fields get safe behavior.
- Field masks let clients request exactly the fields they want, so payload growth never breaks parsing.

## Verification discipline
- Maintain a contract test that asserts the old request shapes still succeed after each release.
- Run the new API against a recorded corpus of old client traffic.

## Pairs with
api-design-patterns, api-long-running-operations, domain-modeling-functional, zapier-system-cloner.