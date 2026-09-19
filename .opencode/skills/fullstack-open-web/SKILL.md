---
name: fullstack-open-web
description: "Ships full-stack web apps end to end: React frontends, Node APIs, testing, and deployment. Use when the user says 'fullstack', 'React app', 'REST API', 'GraphQL', 'TypeScript', 'state management', 'E2E testing', 'CI/CD deploy', 'Fullstack Open', or when a web idea must become a running production app."
---

# Fullstack Open Web

Distilled from the University of Helsinki *Full Stack Open* track: one
JavaScript ecosystem from database to browser, with testing and deployment
as first-class citizens — not afterthoughts.

## Purpose

Deliver a working, tested, deployed web application: frontend, API,
persistence, auth, and pipeline, each with its quality bar.

## The stack (in build order)

1. **React frontend that stays sane.** Components + hooks; state where it
   belongs (local first, lifted only on evidence, server state via query
   caching not hand-rolled fetch). Side effects isolated in effects with
   cleanup. Forms controlled; validation mirrored server-side (client
   validation is UX, never security).
2. **Node/Express API with structure.** Routers per resource; middleware for
   cross-cutting (auth, logging, errors); validation at the boundary (every
   input typed and checked); proper status codes (201 created, 204 empty,
   400 client fault, 401 vs 403 distinguished).
3. **Persistence that means it.** Schema modeled from access patterns;
   migrations versioned and reversible; seed data for dev; backups tested by
   restore. No N+1 in list endpoints (join/eager-load by default).
4. **Auth done once, done right.** Hashed passwords (Argon2/bcrypt), short-
   lived tokens + refresh rotation, authorization checked per resource (not
   per route prefix), secrets in env/vault never in bundles.
5. **Testing pyramid, real.** Unit (logic), integration (API + DB), E2E
   (critical user journeys in a real browser). Coverage gates the pipeline;
   flaky tests quarantined same-day, never normalized.
6. **TypeScript + lint + pipeline.** Strict types at boundaries first, then
   inward; lint clean blocks merge; CI runs tests + build on every push;
   deploy is a pipeline artifact (same image dev->prod), with health checks
   and rollback practiced.

## Quality bars (each layer audited before ship)

- Frontend: no console errors, loading/error/empty states everywhere,
  accessible basics (labels, focus, contrast).
- API: contract documented (OpenAPI), rate-limited, paginated lists.
- Data: migration-tested, with a successful restore test on record.
- Pipeline: green main always; broken builds page the author, not the team.

## Verification

Ship review: demo the user journey live, show the pipeline green, show the
restore test log, and name the on-call for the first week. Missing any one
delays launch.

## Pairs with

- `api-design-patterns` (contract design), `impeccable`/`frontend-design`
  (UI quality), `continuous-delivery-pipeline` (shipping),
  `aumasson-serious-crypto` (auth/passwords), `oauth-oidc-jwt-automation-security-v2`.
