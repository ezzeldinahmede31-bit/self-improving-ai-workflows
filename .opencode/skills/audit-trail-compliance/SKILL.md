---
name: audit-trail-compliance
description: "Records actor, action, target, hashes, outcome in append-only logs for compliance. Use for regulated flows."
---

# Audit Trail and Compliance Logging

Answers must already exist when auditors ask.

## Workflow
1. Enumerate auditable actions (writes, approvals, config changes).
2. Standardize record + correlation ID.
3. Write append-only, restricted access, separate from debug logs.
4. Tabletop audit: reconstruct one transaction from logs alone.

## Core Rules
- Corrections are new entries, never edits.

## Pairs with
- `security-monitoring`, `sre-reliability-engineering`, `autonomous-systems-future`
