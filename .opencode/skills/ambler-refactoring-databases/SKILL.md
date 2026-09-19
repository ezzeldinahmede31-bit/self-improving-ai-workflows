---
name: ambler-refactoring-databases
description: "Evolves production databases safely: refactoring patterns, migrations, and dual running. Use when the user says 'refactor database', 'schema migration', 'rename column production', 'split table', 'evolutionary database design', 'Ambler', or when the schema must change without downtime or data loss."
---

# Ambler Refactoring Databases

Distilled from Ambler & Sadalage *Refactoring Databases*: application code
refactors freely while schemas fossilize — fix the imbalance with
evolutionary database techniques that keep production running throughout.

## Purpose

Change any schema (rename, split, merge, migrate) on a live database with
zero downtime and a rollback path — as a routine, not an event.

## The techniques (in increasing power)

1. **Version everything.** Every schema change is a versioned migration
   script (up + down), applied in order, recorded in a changelog table.
   No manual production edits, ever — the script IS the change.
2. **Transition phases, not flag days.** Expand-then-contract: add the new
   structure alongside the old, dual-write/read during transition, migrate
   data, switch readers, THEN drop the old. Both shapes coexist — backward
   compatibility is engineered, not hoped for.
3. **The refactoring catalog (use by name).** Introduce Surrogate Key, Split
   Table, Merge Tables, Move Column, Rename Column/Table (via view/synonym
   indirection first), Introduce Read-Only Table, Encapsulate Table with
   View, Replace LOB with Table. Each has mechanics + rollback story — follow
   the recipe, don't improvise.
4. **Test the database.** CI runs migrations up AND down on production-like
   data volumes; data-quality tests (constraints, row counts, checksums
   before/after); performance tests on the migrated shape (new indexes
   verified under load, not assumed).
5. **Coordinate code + schema.** Application and database evolve in lockstep
   via the transition period: deploy code that tolerates BOTH shapes, migrate
   schema, then deploy code that assumes the new shape. Three deploys, zero
   outages — the price of safety, paid gladly.

## Data-quality non-negotiables

- Backups verified by restore BEFORE the migration window. Dry run on a
  production clone with timing measured. Rollback rehearsed, not theorized.
  Communication: who is affected, when, and the abort line.

## Verification

Migration review: scripts versioned with down-paths, transition plan with
coexistence window, dual-shape code deployed first (evidence), test results
on clone (data + performance), rollback drill logged. "Run it Friday night
and pray" is rejected as a plan.

## Pairs with

- `refactoring-improving-design` (code-side refactorings),
  `database-reliability-engineering` (production discipline),
  `monolith-database-decomposition` (service splits),
  `continuous-delivery-pipeline` (migration in the pipeline).
