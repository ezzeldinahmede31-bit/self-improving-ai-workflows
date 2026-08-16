# Scorecard And Decision Gates

Use this when comparing candidates, replacing existing code, deciding build versus buy, or assigning confidence.

## Confidence Gates

Classify every serious candidate before recommending it:

- `HIGH`: verified primary sources, clear feature fit, usable integration path, active maintenance, acceptable license/cost/security posture.
- `MEDIUM`: likely fit, but one or two material unknowns remain such as pricing edge cases, migration effort, missing trial evidence, or unclear API depth.
- `LOW`: weak source evidence, stale project, unclear feature parity, risky lock-in, unsupported auth/export, or major unknowns.

Do not recommend a `LOW` confidence option as the primary path. Keep it in risks or rejected alternatives when relevant.

## Evaluation Criteria

Evaluate each serious candidate on:

- Functional fit: how directly it solves the user's workflow.
- Integration: API, webhooks, SDKs, iframe/embed, OAuth/OIDC/SAML, SCIM, export/import, admin automation.
- Ownership: open source, source-available, paid SaaS, license, data portability, lock-in.
- Operations: Docker/Compose availability, deployment complexity, backups, upgrades, scaling, observability.
- Product maturity: recent releases, active maintainers, docs quality, community, issue velocity, ecosystem.
- Cost/benefit: free tier, self-host cost, paid plans, per-seat/per-usage traps, enterprise-only features.
- Security/privacy: auth model, secret handling, tenant isolation, audit logs, compliance needs when relevant.
- Build avoidance: what custom code remains after integration, and whether that code is worth building.

When the solution runs as a separate hosted system, or when the user needs to integrate it into an existing app, give extra attention to standard integration surfaces: REST/GraphQL APIs, outbound webhooks, OAuth 2.0 or OpenID Connect, embeddable UI, admin/provisioning automation, and reliable export paths.

## Weighted Scorecard

Use this default weighting when a scorecard helps. Adjust only when the user's context demands it.

| Criterion | Weight |
| --- | ---: |
| Functional fit | 35% |
| Integration and technical fit | 20% |
| Operations and maintainability | 10% |
| Security, privacy, and compliance | 10% |
| Maturity and vendor/project health | 10% |
| Cost and pricing model | 10% |
| Lock-in and exit path | 5% |

Score finalists from 1-5 per criterion. Treat the score as decision support, not the decision itself. Call out any criterion that should override the total.

## Replacement Safety

When replacing custom code, a current dependency, or a planned custom feature with an existing solution:

- Map the current or proposed behavior to the candidate's API, workflow, or configuration surface.
- Preserve public interfaces unless the user explicitly accepts a migration.
- Prefer native platform APIs and existing project dependencies before adding new packages or SaaS.
- Skip replacement when feature parity is below roughly 80%, when the code is domain-specific business logic, or when the remaining glue code is more complex than the original.
- Check maintenance activity, license compatibility, security advisories, export paths, and deprecation history.
- Estimate effort realistically: `S` under 1 hour, `M` 1-4 hours, `L` over 4 hours.

Do not invent support for APIs, webhooks, OAuth, pricing, or licenses. If source evidence is weak, label it as unverified.
