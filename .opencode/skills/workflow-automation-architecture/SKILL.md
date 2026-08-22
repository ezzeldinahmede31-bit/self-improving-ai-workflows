---
name: workflow-automation-architecture
description: "Designs layered automation graphs with clear trigger, transform, act, observe stages before any node is placed. Use when planning any n8n/Zapier system."
---

# Workflow Automation Architecture

Layered graphs beat spaghetti chains. Decide the shape first so stages compose cleanly.

## Workflow
1. Name the business outcome, trigger event, and final side effects.
2. Sketch boundaries: ingest → validate → transform → act → notify → record.
3. Define payload contract handed across each boundary (field names, types).
4. Draw failure route for every external call before success route.

## Core Rules
- One responsibility per stage; split when two concerns share a stage.
- Explicit contracts over implicit field coupling.
- Failure path designed alongside happy path.

## Failure Modes
- Bottom-up chains with no boundaries -> spaghetti nobody can modify.
- Silent payload drift breaks downstream renames.

## Pairs with
- `n8n-subworkflow-modularizer`, `enterprise-integration-patterns`, `automation-known-issues-compass`
