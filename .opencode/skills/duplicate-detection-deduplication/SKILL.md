---
name: duplicate-detection-deduplication
description: "Detects collapses duplicates via deterministic keys, windows. Use for CRM/events."
---

# Duplicate Detection and Deduplication

One truth per real-world entity.

## Workflow
1. Define entity identity precisely.
2. Normalize fields before compare.
3. Exact-key first, fuzzy only where justified.
4. Bounded window, preserve provenance on merge.

## Core Rules
- Report tally spikes.

## Pairs with
- `crm-contact-sync-patterns`, `idempotency-key-design`, `validation-gate-data-quality`
