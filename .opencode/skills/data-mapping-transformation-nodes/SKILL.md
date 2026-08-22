---
name: data-mapping-transformation-nodes
description: "Transforms payloads with explicit declarative mappings, tests. Use at system boundaries."
---

# Data Mapping and Transformation Nodes

Scattered expressions rot; central mappings survive drift.

## Workflow
1. Document source/target schemas.
2. Declare mapping declaratively with defaults.
3. Snapshot-test against real samples.
4. On upstream change, fixtures fail loudly.

## Core Rules
- Rename once at boundary.

## Pairs with
- `eip-message-transformation`, `validation-gate-data-quality`, `n8n-syntax-v2-enforcer`
