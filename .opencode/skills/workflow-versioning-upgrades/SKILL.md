---
name: workflow-versioning-upgrades
description: "Versions artifacts, staged rollout, safe downgrade. Use for lifecycle."
---

# Workflow Versioning and Upgrades

Versions in VCS, not only editor.

## Workflow
1. Export definitions to VCS as source of truth.
2. Additive-first changes; breaking behind flag/new version.
3. In-flight executions finish on starting version.
4. Keep tested one-step rollback.

## Core Rules
- Changelog: what/why/who approved.

## Pairs with
- `n8n-git-sync`, `continuous-delivery-pipeline`, `infrastructure-as-code`
