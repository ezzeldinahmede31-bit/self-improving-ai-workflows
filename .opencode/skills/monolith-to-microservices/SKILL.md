---
name: monolith-to-microservices
description: "Applies Sam Newman's Monolith to Microservices to decompose a monolith into microservices safely and incrementally: the strangler fig pattern, identifying seams (domain and technical), incremental extraction (database first or application first), data ownership and database decomposition, shared-code and shared-database hazards, orchestration vs choreography, and the rule that you decompose for a business reason, not as a fashion. Use when the user says 'break the monolith', 'migrate to microservices', 'strangler pattern', 'decompose my system', 'identify bounded contexts', 'database per service', 'shared library', 'two-phase commit across services', 'incremental migration', 'monolith first', or when planning or executing a safe modularization. Pairs with: evolutionary-architecture, agent-arch-system-design, cloud-native-patterns, domain-modeling-functional, distributed-systems-concepts-design."
---

# Monolith to Microservices

Newman's central rule: **decompose only for a reason that outweighs the cost.** A
monolith is not a defect; microservices buy independent deployability and scaling
but cost you distributed-systems pain. The whole book is the discipline of
extracting services *incrementally* and *safely*.

## When to use

- Deciding whether/when to split a monolith.
- Planning an extraction order that does not halt the business.
- Reviewing an ongoing migration for safety.

## The decision gate
- Good reasons to split: independent deployability, scaling a hot component alone,
  team ownership boundaries, a genuinely different runtime (memory, throughput).
- Weak reasons: "microservices are modern", cross-team fashion, trying to fix a
  performance problem that one service would not fix.
- If you cannot name the concrete benefit and the concrete cost, do not start.

## The extraction playbook

### 1. Find the seams
- Split by **domain boundaries** (bounded contexts, business capabilities) — not
  by technical layers. Each service should own a coherent slice of behavior.
- Identify the *minimal* seam that lets you move one capability out without
  dragging its dependencies.

### 2. Use the strangler pattern
- Never a big-bang rewrite. Wrap the existing system behind an integration point
  (router/gateway), route a slice of traffic to the new service, verify, then
  retire the old path. Rinse, repeat — the old monolith shrinks as services grow.
- Keep the monolith working during the whole migration: each step must be
  releasable on its own.

### 3. Decide extraction order by risk and value
- Extract capabilities where the benefit is largest and the coupling is weakest
  first; leave the tightly-woven core for later. Each extraction should be
  independently deployable and tested.

## Data: the hard part
- **Database decomposition is the riskiest step.** The classic trap is two
  services sharing one database (sharing a schema, or worse, writing to each
  other's tables).
- Aim for **database per service** where possible; when shared data is
  unavoidable, make the ownership explicit (one owner per table) and access it
  through the owner's API.
- A transaction that must span services is a signal to rethink the seam — you
  cannot easily do two-phase commit across services. Prefer sagas/compensation
  or redesign the boundary so the operation stays local (see `distributed-
  systems-concepts-design`).

## Shared-code and coupling hazards
- **Shared libraries**: version carefully; a shared library couples every consumer
  and forces coordinated deploys. Prefer small, stable, rarely-changing libraries.
- **Shared database / shared schema**: the fastest way to turn microservices back
  into a distributed monolith.
- **Orchestration vs choreography**: orchestration (a central coordinator calls
  services) is easier to reason about; choreography (services react to events) is
  more decoupled but harder to trace. Choose deliberately per flow (see
  `designing-event-driven-systems`).

## Incremental safety rules
- Each extraction keeps the system green: same behavior, new internal shape.
- Feature-flag or route by traffic so any step can be rolled back.
- Establish per-service observability (logs, metrics, traces) before you depend
  on it to debug the new topology.
- Keep a written migration map (what moved, what stays, what is next) so the
  effort stays coordinated.

Pairs with: evolutionary-architecture (fitness functions guard the split), cloud-
native-patterns (deployment semantics), domain-modeling-functional (finding
boundaries), agent-arch-system-design (target architecture).