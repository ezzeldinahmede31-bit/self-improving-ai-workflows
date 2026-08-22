---
name: credential-secret-handling
description: "Stores secrets in vaults, references by ID, never in code/logs. Use for any auth."
---

# Credential and Secret Handling

Leaked creds are cheapest attack.

## Workflow
1. Move every secret to credential manager, reference by ID.
2. Replace inline occurrences.
3. Set rotation cadence, rehearse.
4. Scan repo/logs for patterns.

## Core Rules
- Least scope per credential.
- Redact mechanically.

## Pairs with
- `n8n-credential-security-guard`, `security-and-hardening`, `applied-cryptography-engineering`
