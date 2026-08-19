---
name: designing-web-apis
description: Applies Jin, Sahni & Shevat's Designing Web APIs to building APIs developers will love: the API design workflow (from use case to contract), resources and endpoints, HTTP methods and status codes, authentication and authorization, versioning, pagination and error handling, and the SDKs, documentation, and developer experience that make an API a product. Use when the user says 'designing web APIs', 'API design workflow', 'design an API developers will love', 'resource design', 'authentication for APIs', 'API versioning', 'developer experience', 'Jin Sahni Shevat', or when a web API must be designed as a product, not an endpoint dump.
---

# Designing Web APIs (Brenda Jin, Saurabh Sahni, Amir Shevat)

Designing Web APIs treats an API as a product for developers. This skill applies the full workflow from use case to contract to developer experience.

## Design from use cases

- Start from the developer's use case; the API shape follows the workflow it enables.
- Design resources and endpoints before implementation; the contract is the deliverable.
- Involve the consumers early; a prototype API on paper beats a wrong shipped one.

## HTTP and resources

- Resources are named by nouns; methods (GET, POST, PUT, PATCH, DELETE) are the verbs.
- Status codes communicate success and failure precisely; the body carries the detail.
- Pagination, filtering, and field selection keep large collections usable.

## Authentication and versioning

- Choose the auth model by the audience: tokens, API keys, OAuth, and their scopes.
- Versioning protects consumers from breaking changes; keep the old contract working while the new one grows.
- Errors are part of the contract: a consistent error format saves every consumer.

## Developer experience

- Documentation, SDKs, and examples are part of the API; the experience decides adoption.
- A developer portal with a live playground reduces friction dramatically.
- Listen to the API's consumers; the roadmap follows their pain.

## Pairs with
api-design-patterns, restful-web-apis, api-versioning-compatibility, api-long-running-operations, prompt-engineering-llm-apps
