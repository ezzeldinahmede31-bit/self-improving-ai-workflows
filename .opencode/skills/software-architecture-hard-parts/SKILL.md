---
name: software-architecture-hard-parts
description: "Applies Ford, Richards & Sadalage's Software Architecture: The Hard Parts to the architecture decisions that have no perfect answer: modularity (which modularity unit — modules, services, microservices), decomposing monoliths vs service-based architectures, granularity and coupling/cohesion trade-offs, data ownership and distributed data (eventing, sagas, CQRS, shared data), and moving from a monolith to a distributed architecture while managing trade-offs with quantified reasoning (trade-off analysis, architecture fitness). Use when the user says 'what architecture should I use', 'modular monolith vs microservices', 'how fine-grained should services be', 'trade-off analysis', 'architecture decision', 'coupling and cohesion', 'decompose by domain', 'distributed data', 'saga vs CQRS', 'event-driven vs request-driven', 'architecture trade-offs', 'the hard parts', or when an architecture choice has no obvious winner and the trade-offs must be made explicit. Pairs with: agent-arch-system-design, tradeoff-and-postmortem-documenter, evolutionary-architecture, monolith-to-microservices, distributed-systems-concepts-design."
---

# Software Architecture: The Hard Parts

The premise: most architecture decisions have **no perfect answer** — every choice
trades one set of problems for another. The skill of architecture is naming the
trade-offs, quantifying them where possible, and choosing the option whose
downsides you can live with.

## When to use

- Any architecture decision with real trade-offs (modularity, granularity, data).
- Choosing among monolith, modular monolith, and microservices.
- Making data-ownership and distributed-data calls.

## The decision framework
1. **Name the decision** (what exactly is being chosen).
2. **Enumerate options** — two or more real alternatives, not strawmen.
3. **Trade-off analysis**: for each option list benefits, trade-offs, and
   implications (this is the heart — see the "trade-off matrix" method below).
4. **Make the call and record it** with the reasoning and the triggers that would
   reverse it.

### The trade-off matrix
For each option, score against the dimensions that matter to you: development
speed, operational complexity, scalability, resilience, team structure fit,
data consistency, deployability, cost. A decision that wins on every axis is
usually a mis-analysis; real choices have winners and losers per axis.

## The core debates

### 1. Modularity unit
- **Modular monolith**: one deployable, strong internal boundaries, simple
  operations, still one bottleneck for scaling a single hot component.
- **Microservices**: independent deployability and scaling, but distributed-
  systems tax (network, failure, consistency, observability).
- Rule of thumb: start modular-monolith-shaped; extract services only for a
  specific, named reason (see `monolith-to-microservices`).

### 2. Granularity (how fine to split)
- Too coarse = you are back to a monolith; too fine = coordination and
  operational overhead explode. Split by **business capability** (domain) rather
  than by technical layer or by table.
- Favor **high cohesion + low coupling**: components that change together should
  live together; components that must not coordinate tightly should be separated.

### 3. Data ownership and distributed data
- Decide who owns each piece of data; other services get data through the owner's
  API or through events, never by reaching into another service's database.
- Distributed transactions are the enemy — prefer **sagas** (stepwise with
  compensation) for long-running business transactions, and **CQRS** (separate
  read models) where reads and writes have different shapes/loads.
- **Event-driven vs request-driven**: events decouple and scale asynchronously
  but hide control flow; requests are visible and debuggable. Use events where
  independence matters and requests where the caller must know the outcome (see
  `designing-event-driven-systems`).

### 4. Architecture fitness
- Define **architecture fitness functions** — automated checks that the system
  still matches the chosen architecture (e.g., "no service reaches into another
  service's database", "all services deploy independently"). Without them, the
  architecture decays silently (see `evolutionary-architecture`).

## Practical rules
- Write the trade-off decision down (see `tradeoff-and-postmortem-documenter`);
  a decision without recorded rationale is unknowable later.
- Prefer the boring, well-understood option unless a specific requirement forces
  the clever one.
- Test architectural hypotheses with a spike/experiment before committing.
- Every "best practice" in architecture is a trade-off in disguise — demand the
  name of the trade-off from anyone who prescribes one.

Pairs with: agent-arch-system-design (design methodology), tradeoff-and-postmortem-
documenter (record decisions), evolutionary-architecture (fitness functions),
monolith-to-microservices (execution), distributed-systems-concepts-design
(distributed semantics).