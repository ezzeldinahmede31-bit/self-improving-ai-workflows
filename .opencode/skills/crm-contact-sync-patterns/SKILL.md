---
name: crm-contact-sync-patterns
description: "Keeps contacts consistent across systems with ownership + change cursors. Use for CRM sync."
---

# CRM Contact Sync Patterns

Two-way sync without ownership -> update wars.

## Workflow
1. Assign single owning system per field.
2. Change-driven sync via updated-since cursors.
3. Resolve conflicts by ownership policy.
4. Log applied/skipped/conflicted per run.

## Core Rules
- Soft-delete first.

## Pairs with
- `hubspot`, `crm-automation`, `duplicate-detection-deduplication`
