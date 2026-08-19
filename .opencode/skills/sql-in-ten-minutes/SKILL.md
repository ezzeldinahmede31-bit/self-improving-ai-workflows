---
name: sql-in-ten-minutes
description: Applies Ben Forta's SQL in 10 Minutes to writing correct, portable SQL fast: selecting, filtering and sorting, joins, grouping and aggregate functions, subqueries, views, transactions, and creating and altering tables, with the syntax differences across the major databases. Use when the user says 'sql in ten minutes', 'write a SQL query', 'join', 'group by', 'having', 'subquery', 'create table', 'insert update delete', 'Ben Forta', 'portable SQL', or when a SQL statement must be written or fixed quickly and correctly.
---

# Sams Teach Yourself SQL in 10 Minutes (Ben Forta)

Forta's book is the fastest path from zero to writing correct SQL. This skill applies its task-oriented style to everyday query work.

## The SELECT basics

- SELECT, FROM, WHERE, ORDER BY, LIMIT are the core; write them in the standard order.
- Filter with precise predicates and beware of NULL comparisons; use IS NULL, never equals NULL.
- Distinguish filtering rows (WHERE) from filtering groups (HAVING).

## Joins and aggregation

- Joins combine tables by the join condition; specify the join type (inner, left, right, full) deliberately.
- Aggregates (sum, average, min, max, tallies) summarize groups; GROUP BY defines the grouping.
- Every column in the SELECT that is not aggregated must appear in GROUP BY.

## Subqueries and views

- A subquery in WHERE, FROM, or SELECT computes a value used by the outer query.
- Views are named queries that simplify and control access; they do not store data by default.
- Correlated subqueries reference the outer row; they run once per row and can be expensive.

## Data modification and DDL

- INSERT, UPDATE, and DELETE change data; UPDATE and DELETE need precise WHERE clauses.
- CREATE, ALTER, and DROP manage schema; constraints (primary key, foreign key, unique, check) encode rules.
- Transactions group changes so they commit or roll back together.

## Pairs with
database-system-concepts, database-management-systems, postgresql-up-and-running, high-performance-mysql, n8n-code-nodes-official
