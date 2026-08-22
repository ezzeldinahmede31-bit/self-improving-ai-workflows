---
name: conditional-routing-switches
description: "Designs exhaustive, disjoint branching with default route. Use for IF/Switch logic."
---

# Conditional Routing and Switches

Branches decide where data flows — silent drops live here.

## Workflow
1. Enumerate decision dimensions + values.
2. Cover full value space plus default.
3. Ensure conditions disjoint by construction.
4. Default logs or dead-letters, never silent.

## Core Rules
- Deep nested ifs -> flat switch.

## Pairs with
- `eip-message-routing`, `validation-gate-data-quality`, `dead-letter-error-routes`
