---
name: dbt-analytics-engineering
description: "Transforms warehouses with software discipline: versioned models, tests, and docs. Use when the user says 'dbt', 'analytics engineering', 'data models', 'snapshots', 'data tests', 'sources and seeds', 'Jinja macros', or when warehouse SQL must be maintainable, tested, and documented."
---

# dbt Analytics Engineering

Distilled from dbt Labs practice (*Analytics Engineering Guide* lineage):
the warehouse transform layer written like software — SELECT-only models,
versioned in git, tested in CI, documented automatically.

## Purpose

Turn fragile ETL scripts into a trustworthy, reviewable model graph where
every table knows its lineage and every assumption is tested.

## The practice (project order that scales)

1. **Sources over hard-coding.** Every raw input declared as a `source`
   (database.schema.table + freshness checks); staging models (`stg_`) do
   exactly one job: rename + type-cast, no business logic. Logic starts in
   `int_`/`marts` — raw never leaks past staging.
2. **Models as SELECTs.** One model = one SELECT building one table/view;
   CTEs named as steps (readable top-to-bottom); Jinja/`ref()` for
   dependencies (never hard-coded table names — lineage breaks otherwise).
   Materialization chosen deliberately (view/ephemeral/table/incremental by
   size and freshness need).
3. **Tests as contracts.** Generic tests on every model (unique, not_null,
   accepted_values, relationships); singular tests for business rules
   ("revenue never negative", "every order has a customer"). Failing tests
   block merges — untested models are drafts, not assets.
4. **Snapshots for history.** SCD-Type-2 via `snapshot` (timestamp/invalidate
   strategies) instead of hand-rolled history tables; snapshot policy per
   entity with the business, matching `kimball-dimensional-modeling` SCD
   choices.
5. **Docs and exposure.** Descriptions on models AND columns (future-you is
   a stranger); `exposures` declare downstream dashboards so changes warn
   their consumers; generated docs site published per release.
6. **CI that means it.** Slim CI (build only changed models + descendants),
   full nightly rebuild, zero-warning policy, SQL linting + style guide
   enforced. Main branch always deployable to production runs.

## Verification

Project review: DAG acyclic and layered (sources→staging→marts), test
coverage per model shown, freshness SLAs green, docs published, exposures
declared. Untested models merged to main are reverted, not debated.

## Pairs with

- `kimball-dimensional-modeling` (what the marts model),
  `data-pipelines-pocket-reference` (orchestration around dbt),
  `winand-sql-indexing` (fast model SQL),
  `karwin-sql-antipatterns` (what the models must avoid).
