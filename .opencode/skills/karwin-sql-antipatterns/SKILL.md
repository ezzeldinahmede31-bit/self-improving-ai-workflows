---
name: karwin-sql-antipatterns
description: "Avoids the classic SQL traps: EAV,Adjacency lists, and other logical landmines. Use when the user says 'SQL antipattern', 'entity-attribute-value', 'adjacency list', 'polymorphic association', 'comma-separated values', 'Karwin', or when a schema smells but nobody can name why."
---

# Karwin SQL Antipatterns

Distilled from Bill Karwin's *SQL Antipatterns*: the same two dozen schema
mistakes recur everywhere — each with a name, a diagnosis, and a legitimate
alternative. Name the smell, apply the fix.

## The rogues' gallery (recognize → replace)

1. **Jaywalking (comma-separated lists).** Storing `1,2,3` in one column
   kills querying, indexing, integrity. Fix: intersection table (one row per
   association) — always.
2. **Naive Trees (adjacency list for deep hierarchies).** `parent_id` only:
   subtree queries need recursion the DB may lack. Fix by access pattern:
   path enumeration (read-fast), nested sets (subtree-fast), closure table
   (flexible + integrity) — pick per workload, never default.
3. **ID Required (surrogate-everything).** Meaningless IDs on pure junction
   tables invite duplicates the natural key would forbid. Fix: natural keys
   where they exist, UNIQUE constraints everywhere reality demands one.
4. **Keyless Entry (no constraints).** "Handled in the app" means handled
   nowhere under concurrency. Fix: PK/FK/NOT NULL/CHECK/UNIQUE in the schema
   — the database is the last honest validator.
5. **EAV (entity-attribute-value).** Open-schema flexibility that destroys
   typing, constraints, and queryability. Fix: real columns (schema
   evolution is normal work), JSON columns for genuinely sparse data, or a
   document store if the shape truly varies.
6. **Polymorphic Associations (`parent_type` + `parent_id`).** Unjoinable,
   unenforceable. Fix: separate FK columns per parent, or a supertype table
   with subtype joins.
7. **Magic Beans (ENUM misuse / booleans for states).** Hard-coded lists that
   need deploys to change. Fix: lookup tables for real domains; booleans
   only for true binaries.
8. **Metadata Tribbles (one table per year/user/tenant).** Schema explosion
   instead of rows. Fix: one table with a discriminator column (+
   partitioning for scale, RLS for tenancy).
9. **Implicit Columns (SELECT * in production).** Schema changes break
   consumers silently. Fix: explicit column lists everywhere outside ad-hoc.
10. **Random Selection / Poor Man's Audit (triggers-as-logic).** Hidden
    behavior and ordering nightmares. Fix: ORDER BY with real randomness
    needs (TABLESAMPLE/offset techniques), audit via explicit history
    tables or CDC — visible and testable.

## Review protocol

Walk every new schema against the gallery: name any match out loud, justify
with workload evidence if kept anyway, record the exception. Silent matches
are tech debt with compound interest.

## Verification

Schema review ends with: antipattern checklist walked (each marked
absent/justified), constraints inventory matching business rules, and one
query proving each hot path uses an index. Unnamed smells stay; named ones
get fixed.

## Pairs with

- `database-system-concepts` (relational theory beneath),
  `winand-sql-indexing` (making the fixed schema fast),
  `dbt-analytics-engineering` (models must avoid these too),
  `ambler-refactoring-databases` (fixing them in production).
