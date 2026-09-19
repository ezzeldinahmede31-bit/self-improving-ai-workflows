---
name: rest-assured-patterns
description: "REST Assured patterns distilled. Use when testing Java APIs, given-when-then specs, schema validation, auth flows, fluent assertions."
---

# REST Assured Patterns

## Purpose

Test REST APIs fluently in Java: given-when-then specs, schema validation, auth flows, reusable request specs.

## When to use

Use when the user says 'REST Assured', 'Java API test', 'given when then API', 'JSON schema validation Java'.

## Steps

1. Centralize base URI, auth, and logging in request specifications.
2. Write specs as given (setup), when (call), then (assert status plus body).
3. Validate bodies against JSON schemas plus key business fields.
4. Cover auth flows: login, refresh, expiry, forbidden versus unauthorized.
5. Separate contract specs (fast, per commit) from flow specs (nightly).

## Anti-patterns

- Base URIs and secrets pasted in every test (use env-provided config, never inline secrets).
- Asserting status only with no body checks.
- Order-dependent specs sharing server state.
- Ignoring JSON schema drift across versions.

## Example

```java
given().auth().oauth2(token())
  .when().get("/orders/1")
  .then().statusCode(200)
  .body("id", equalTo(1));
```

## Verification

Specs centralized, schemas validated, auth matrix covered, contract versus flow split honored.

## Pairs-with

api-testing-contract-patterns, junit5-enterprise-patterns, test-data-management, graphql-advanced-testing.
