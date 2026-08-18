---
name: web-api-design-love
description: Applies Leonard Richardson & Sam Ruby's RESTful Web Services ('web-api-design-love' — the pragmatic REST classic) to build HTTP APIs that treat the web as a platform — URI design, HTTP verbs and status codes, XML/JSON media types and extensibility, caching and conditional GET, authentication, and the design conversation that picks the right trade-offs for a service's audience. Complements RESTful Web APIs with the original field guide's concrete patterns for resources, collections, and large/slow operations. Use when the user says 'design a web service', 'REST web services', 'URI design', 'resource collections', 'conditional GET', 'ETag', 'RESTful Web Services Richardson Ruby', 'media type extensibility', 'web API design', or when building an HTTP service and needs the pragmatic patterns for collections, updates, and caching. Pairs with: restful-web-apis, api-design-patterns, api-versioning-compatibility, webhook-automation, n8n-node-configuration.
---
# Web API Design (Richardson & Ruby, RESTful Web Services)

Transfers the pragmatic field guide behind RESTful Web Services: treat the web as the platform, make each resource addressable, and pick the right HTTP mechanics per operation.

## When to use
- Designing collections, members, and their CRUD operations over HTTP.
- Choosing caching and conditional-request strategy to cut load.
- Deciding how verbose or strict a representation should be for the client audience.

## The mechanics
1. Address resources with URIs that name the concept; collections and members (e.g., an order within orders) form the natural hierarchy.
2. Map operations to verbs: GET reads, PUT creates by client-chosen URI or replaces, POST creates with server-chosen URI, DELETE removes, PATCH/HEAD/OPTIONS where they fit.
3. Use status codes as the contract: 2xx success, 4xx client error, 5xx server error; every response carries the code that the client will branch on.
4. Represent with media types and extend them deliberately; a schema change is a new representation, not a silent edit.
5. Cache with ETags and conditional GET so repeated reads skip the server; design for clients that revalidate.

## Large and slow work
- For big payloads or long operations, split the request into a job resource with its own status, or paginate collections with stable cursors.
- Keep writes idempotent where the client may retry (PUT, and DELETE-by-design).

## Verification discipline
- Exercise every verb and code path with a real client; verify cache headers and conditional requests actually skip work.
- Validate that a collection supports the standard operations before adding bespoke endpoints.
- Add a contract test that runs on every change and alerts on breaking drift.

## Pairs with
restful-web-apis, api-design-patterns, api-versioning-compatibility, webhook-automation, n8n-node-configuration.