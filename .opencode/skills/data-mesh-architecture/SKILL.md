---
name: data-mesh-architecture
description: "Applies Zhamak Dehghani's Data Mesh to decentralize data ownership at enterprise scale: the four principles — domain-oriented data ownership, data as a product, the self-serve data platform, and federated computational governance — plus the data-contract discipline and the operational reality that data mesh is an organizational and architectural change, not a tool. Use when the user says 'data mesh', 'domain ownership of data', 'data as a product', 'self-serve data platform', 'federated governance', 'data contract', 'decentralize our data platform', 'data mesh architecture', or when a central data team is the bottleneck. Pairs with: domain-driven-design-strategic, fundamentals-of-data-engineering, designing-event-driven-systems, software-architecture-hard-parts, enterprise-integration-patterns."
---

# Data Mesh Architecture

The premise: as an organization grows, a central data team becomes the
bottleneck — everyone waits for the hub. Data mesh flips the model: the domain
teams that own the source of the data also own the data products built from it.

## When to use

- When a centralized data platform cannot keep up with domain teams.
- When data quality is poor because ownership is ambiguous.
- When choosing an organizational model for a data platform (monolith vs mesh).

## The four principles

1. **Domain-oriented ownership** — each business domain owns the data for its
   operational scope (map domains via `domain-driven-design-strategic`).
2. **Data as a product** — every domain exposes its data as a product with an
   owner, an SLO, a documented contract, and a known cost; treat consumers as
   customers.
3. **Self-serve data platform** — a platform team builds the internal tooling
   (pipeline scaffolding, storage, catalog) so domains can produce and consume
   without waiting.
4. **Federated computational governance** — standardization lives in the platform
   and in contracts, not in a central committee that reviews every change.

## Data contracts (the load-bearing piece)

- A contract names the schema, the semantics of each field, and the availability
  promise of the data product.
- Consumers bind to the contract; producers can change internals freely while the
  contract holds.
- Break changes through versioning with migration windows (see
  `api-versioning-compatibility`).

## When NOT to use data mesh

- Small teams or a single domain: the coordination overhead exceeds the benefit. A
  centralized platform is the honest answer at small scale.
- No platform capability yet: shipping ownership without self-serve tooling just
  exports the bottleneck to domains.

## Practical rules

- Start with one domain proving the pattern, then expand.
- Make the platform do the heavy lifting so a domain can ship a data product in
  days, not quarters.
- Treat governance as code in the platform (validation, cataloging, contract
  checks), not as process.

Pairs with: domain-driven-design-strategic (finding domains),
fundamentals-of-data-engineering (lifecycle), designing-event-driven-systems
(event products), software-architecture-hard-parts (decentralization trade-offs),
enterprise-integration-patterns (interfaces).