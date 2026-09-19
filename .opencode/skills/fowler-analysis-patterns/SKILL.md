---
name: fowler-analysis-patterns
description: "Reuses domain models that work: accountability, measurements, inventory, and planning patterns. Use when the user says 'analysis patterns', 'accountability pattern', 'measurement pattern', 'inventory model', 'planning structure', 'Fowler patterns', or when a business domain needs modeling, not inventing."
---

# Fowler Analysis Patterns

Distilled from Martin Fowler's *Analysis Patterns*: business domains repeat
the same structures (parties, measurements, holdings, plans) — reuse the
proven models instead of rediscovering their edge cases the hard way.

## Purpose

Model a business domain in days using patterns that already survived
production — with their subtleties (time, multi-party, multi-unit) built in.

## The pattern families (steal these shapes)

1. **Accountability.** Parties (person/organization — one hierarchy, never
   separate person/org tables that later merge painfully), hierarchies with
   accountability relationships (manager/client/owner as RELATIONS, not
   attributes), operating scopes (where a relation is valid). Rule: model the
   relationship, not the role — roles change, relations persist.
2. **Observations & Measurements.** Quantity = amount + unit (never bare
   numbers with implied units); measurement = value + unit + time + context;
   compound units convert explicitly; ranges and ratios as first-class
   values. Phenomenon types separate "blood pressure reading" from "132/84".
   Unit bugs kill missions — make units structural.
3. **Inventory & Holdings.** Account-based thinking for anything countable:
   entries (in/out) rather than mutable balances (auditability free);
   lots/FIFO layers where identity matters; reservations vs availability.
   Balances are always DERIVED, never stored (stored balances drift).
4. **Planning.** Proposed/confirmed/occurred layering (plans vs reality in
   separate structures); protocols (reusable plan templates) vs plans
   (instantiated); resource allocation with commitment states. Comparing plan
   to actual is then a query, not a project.
5. **Temporal patterns.** Effective dating on every fact that can change
   (valid-time + transaction-time bitemporality where audit matters);
   never overwrite history — supersede with date ranges. "Current" is a view,
   not storage.

## Application discipline

- Start from the pattern, then DEVIATE explicitly (pattern X minus Y because
  Z) — deviations documented, not drifted into.
- Validate with domain expert walkthroughs using THEIR terminology (the
  ubiquitous language check): if they rename your entities, adopt their
  names.

## Verification

Model review: pattern source cited per structure, deviations listed with
reasons, temporal policy stated per entity, units explicit per quantity,
expert walkthrough signed. A model with bare numbers and mutable balances
fails review.

## Pairs with

- `domain-driven-design-strategic` (bounded contexts around the models),
  `ddd-tactical-aggregates` (implementation boundaries),
  `domain-modeling-functional` (types for the patterns),
  `database-system-concepts` (relational mapping).
