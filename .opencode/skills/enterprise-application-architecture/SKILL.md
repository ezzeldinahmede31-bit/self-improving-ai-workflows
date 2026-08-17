---
name: enterprise-application-architecture
description: "Applies Martin Fowler's Patterns of Enterprise Application Architecture (PoEAA) to automation and service code: the Layered Architecture, Domain Model vs Transaction Script vs Table Module, Identity Field, Unit of Work, Repository, Lazy Load, and the service layer. Guides choosing the right architecture shape for the problem size and avoiding the data-mapper-and-repository-everywhere anti-pattern for small systems. Use when the user says 'PoEAA', 'enterprise architecture', 'layered architecture', 'transaction script', 'domain model', 'unit of work', 'repository', 'identity field', 'lazy load', 'service layer', 'Fowler enterprise patterns', or when structuring a service or data pipeline. Pairs with: domain-modeling-functional, ddd-tactical-aggregates, api-design-patterns, database-internals-engines."
---
# Enterprise Application Architecture (PoEAA - Fowler)

Fowler's catalog answers one question first: WHICH architecture shape fits this problem size? The patterns exist to be chosen, not to be mandatory. Over-applying the full stack to a 3-table app is itself an anti-pattern.

## The Architecture Selection Guide (Fowler's core advice)

| Problem size | Recommended architecture | Why |
|---|---|---|
| Small, procedural logic | Transaction Script | Straight line of logic per use case |
| Rich business rules | Domain Model | Rules live with the data they govern |
| Simple data over a relational schema | Table Module | One class per table, no mapper complexity |
| Complex mapping needed | Data Mapper + Repository | Decouples domain from storage |
| Multi-context or large team | Layered (Service > Domain > Data) | Clear dependency direction |

## Key Patterns (decision rules)

### Identity Field & Identity Map
- Every entity needs a stable ID field; use an Identity Map to avoid loading the same row twice in one request.
- Error: keying entities by mutable business attributes (email changes break identity).

### Unit of Work
- Collect changes during a request, commit them all at once, in one transaction.
- Error: saving to the database after every single mutation (N+1 writes, partial states).

### Repository
- A collection metaphor over storage: `find`, `add`, `remove` with the domain's vocabulary.
- Error: a repository exposing SQL or query objects - that is the Data Mapper's job leaking.

### Lazy Load
- Load a property only when first accessed.
- Error: lazy loading in a batch loop (N+1 queries). Use eager/batch fetch for lists.

### Service Layer
- Defines an application boundary and transaction boundary; keeps domain logic out of the UI/webhook layer.
- In n8n: the sub-workflow interface is the service layer; webhook nodes never contain business rules.

## Architecture Selection Checklist

- [ ] Architecture chosen from the size table - not 'the enterprise stack because we are enterprise'
- [ ] Layering is explicit and dependency direction is inward
- [ ] One Unit of Work per request, one commit
- [ ] Repositories expose domain vocabulary, not SQL
- [ ] Identity fields are stable and independent of business attributes
- [ ] No N+1 lazy loads in batch paths

## Violations (severity)

- **V1 - Over-architecture** (HIGH): Mapper + Repository + Service layer for a two-table pipeline. Fix: use Transaction Script or Table Module.
- **V2 - Logic in the webhook layer** (HIGH): Business rules inside trigger/HTTP nodes. Fix: move to a service sub-workflow.
- **V3 - Save-everywhere** (HIGH): Writes fired after every mutation. Fix: one Unit of Work, one commit.
- **V4 - Repository leaking SQL** (MEDIUM): Storage details visible at the domain boundary. Fix: hide storage behind the collection metaphor.
- **V5 - Unstable identity** (MEDIUM): Entities keyed by email/name. Fix: surrogate identity field.

## Verification

Run the build gates and require READY_FOR_DEPLOYMENT. For service code, confirm one commit per request by tracing write calls in a test.
