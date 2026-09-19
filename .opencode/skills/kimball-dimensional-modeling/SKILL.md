---
name: kimball-dimensional-modeling
description: "Models data warehouses dimensionally: facts, dimensions, and slowly changing history. Use when the user says 'star schema', 'snowflake schema', 'fact table', 'dimension table', 'SCD', 'slowly changing dimensions', 'Kimball', 'data mart', or when analytics needs fast, understandable queries."
---

# Kimball Dimensional Modeling

Distilled from Kimball & Ross *The Data Warehouse Toolkit*: warehouses serve
HUMANS asking business questions — model facts (what happened) ringed by
dimensions (who/what/where/when), and every BI question becomes an obvious
join.

## Purpose

Build warehouses business users can query without an engineer — fast,
consistent (conformed dimensions), and historically honest.

## The method (bus architecture first, tables second)

1. **Grain declaration.** One row = one WHAT at which granularity (one row
   per sale line? per sale? per day?). Grain is the single most important
   decision: too coarse destroys analysis, too fine explodes volume. State
   it in one sentence or the model is not designed yet.
2. **Facts: measurements + keys.** Fact tables hold numeric measurements
   (additive: sums work; semi-additive: balances need care; non-additive:
   ratios computed, never stored) plus foreign keys to dimensions. Factless
   fact tables capture EVENTS (attendance, coverage) — presence IS the fact.
3. **Dimensions: context with history.** Wide, denormalized, human-readable
   (star beats snowflake for comprehension and join simplicity; snowflake
   only with measured cause). Surrogate keys ALWAYS (source keys change;
   integers join fast).
4. **Slowly changing dimensions.** Type 1 (overwrite — history destroyed, use
   only for corrections), Type 2 (new row with effective dates — full
   history, the default), Type 3 (previous-value column — narrow use).
   SCD policy per attribute, decided with the business, not by developers.
5. **Conformed dimensions + bus matrix.** Same customer/product/date dimension
   shared across marts (rows: business processes, columns: dimensions, cells:
   fact tables). Conformance is what makes "one version of the truth" real
   instead of a slogan. Date dimension prebuilt (holidays, fiscal calendar).
6. **ETL discipline.** Extract (don't break sources), clean (quarantine rows
   with data-quality errors — never silently drop), conform (apply
   standards), deliver (indexed, partitioned, documented). Data-quality
   dashboards ship WITH the warehouse.

## Verification

Model review: grain sentence, fact classifications (additive/semi/non),
SCD policy per attribute, bus matrix filled, conformance proven by
cross-mart query agreement. A warehouse users query through engineers is a
failed warehouse.

## Pairs with

- `columnar-analytics-engines` (physical substrate),
  `dbt-analytics-engineering` (modern implementation),
  `data-pipelines-pocket-reference` (ETL practice),
  `fundamentals-of-data-engineering` (platform context).
