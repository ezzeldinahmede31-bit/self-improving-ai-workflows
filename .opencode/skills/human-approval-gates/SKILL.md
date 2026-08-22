---
name: human-approval-gates
description: "Inserts audited human checkpoints before high-stakes actions with expiring single-use tokens. Use before destructive/financial steps."
---

# Human Approval Gates

Some actions must pause for a human.

## Workflow
1. Gate destructive/financial/visible actions.
2. Render full details to approver channel.
3. Issue single-use expiring token, verify by hash.
4. Timeout -> auto-deny -> notify requester.

## Core Rules
- Show exactly what will execute.
- Log requester, approver, time.

## Pairs with
- `autonomous-systems-future`, `audit-trail-compliance`, `build-gates-pipeline`
