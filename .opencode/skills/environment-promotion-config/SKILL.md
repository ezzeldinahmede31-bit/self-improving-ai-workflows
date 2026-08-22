---
name: environment-promotion-config
description: "Moves workflows across dev/stage/prod with scoped config, never copy-paste. Use for deployments."
---

# Environment Promotion and Configuration

Hand-edited copies drift.

## Workflow
1. Externalize env-specific values to config variables.
2. Promotion moves artifact unchanged; config resolves per env.
3. Stage mirrors prod topology.
4. Credentials env-scoped, never in dev.

## Core Rules
- Log version/approver/diff per promotion.

## Pairs with
- `infrastructure-as-code`, `continuous-delivery-pipeline`, `n8n-self-hosting`
