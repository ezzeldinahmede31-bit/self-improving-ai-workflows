---
name: validation-gate-data-quality
description: "Blocks bad data at entrances with schema/range checks + quarantine. Use at trust boundaries."
---

# Validation Gates for Data Quality

Stop garbage at the door.

## Workflow
1. Define canonical schema at entrance.
2. Check presence/type/format/range/referential sanity.
3. Quarantine violations with reasons.
4. Threshold alert on violation rate jumps.

## Core Rules
- Version validation rules like code.

## Pairs with
- `building-data-heavy-applications`, `data-pipelines-pocket-reference`, `dead-letter-error-routes`
