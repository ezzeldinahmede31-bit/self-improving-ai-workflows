---
name: reversibility-engine
description: "Enforces the Pragmatic Programmer principle of Reversibility: design so decisions can be undone. In n8n workflows, this means every node that creates state or causes side effects must have a documented rollback strategy. Provides undo/redo patterns, compensation transactions, and state management for workflow reversibility. Triggers on workflow build/validation; warns on stateful nodes without clear rollback. Pairs with: gate-first-pass-builder, n8n-error-boundary-architect, n8n-subworkflow-modularizer."
---
# Reversibility Engine

The Pragmatic Programmer's Reversibility principle: "If you can't undo a decision, you can't make it with confidence." In n8n workflow automation, this translates to: every stateful operation must have a defined rollback path. If a workflow sends an email, updates a database, or triggers a webhook - there must be a clear way to reverse or compensate for that action.

## Clean Code & Pragmatic Programmer Alignment

This skill enforces:
- **Reversibility** (Pragmatic Programmer): "If you can't undo it, don't do it"
- **Command-Query Separation** (Clean Code): separate operations that change state from those that just read
- **Comprehensive Error Handling** (Code Complete): every error path must have a recovery strategy
- **Testability** (Code Complete): reversibility patterns must be testable

## Irreversibility Detection Catalog (15+ Patterns)

### A. External Side Effects (1-10)

| # | Irreversible Operation | Risk | Rollback Pattern |
|---|------------------------|------|------------------|
| E1 | **Email Send** | Cannot recall sent email | Log sent emails; provide "recall" workflow via follow-up apology email |
| E2 | **Database Write** | Permanent data change | Add compensating DELETE/UPDATE; use transaction-like patterns |
| E3 | **Webhook Call** | External system state change | Log webhook payloads; provide idempotency keys for safe retry |
| E4 | **File Creation** | Persistent artifact created | Add cleanup node; use temporary file patterns |
| E5 | **API State Change** | External API resource modified | Implement DELETE/PATCH endpoints; use versioning |
| E6 | **Notification Push** | User sees notification permanently | Log notifications; provide "mark as read" or follow-up correction |
| E7 | **Payment/Charge** | Financial transaction executed | Use payment provider refund APIs; log transaction IDs |
| E8 | **Scheduled Job Creation** | Cron job/task created in external system | Store job IDs; provide cancellation workflow |
| E9 | **Permission Grant** | Access rights modified | Store previous permissions; add revocation workflow |
| E10 | **Configuration Change** | System config modified | Version configs; provide rollback to previous version |

### B. Internal State Mutations (11-15)

| # | Irreversible Operation | Risk | Rollback Pattern |
|---|------------------------|------|------------------|
| I1 | **Variable Overwrite** | Previous value lost forever | Use versioned variables; snapshot before change |
| I2 | **Cache Invalidation** | Stale data served until refresh | Use cache tags; implement selective invalidation |
| I3 | **Token/Credential Rotation** | Old credentials invalidated | Store previous tokens; overlap period before revocation |
| I4 | **Workflow State Change** | Execution context mutated | Use immutable data patterns; copy-on-write |
| I5 | **Sub-workflow Mutation** | Called workflow modified | Use versioned sub-workflows; pin specific versions |

## Reversibility Implementation Patterns

### Pattern 1: Compensating Transaction (Saga)
```
Main Workflow → Step 1 (write) → Step 2 (write) → Step 3 (fail)
     ↓
Compensation → Undo Step 2 → Undo Step 1
```
**Implementation**: Each write step stores compensation data; on failure, execute compensating steps in reverse order.

### Pattern 2: Idempotency with Replay
```
Every external call gets idempotency key
Replay with same key = safe (no double effect)
```
**Implementation**: Generate deterministic keys; store in workflow execution context.

### Pattern 3: Versioned State with Rollback
```
Before mutation: snapshot current state
On failure: restore snapshot
```
**Implementation**: Use Set nodes to snapshot; dedicated rollback sub-workflow.

### Pattern 4: Two-Phase Commit (Lightweight)
```
Phase 1: Prepare (validate, reserve resources)
Phase 2: Commit (execute) OR Abort (release)
```
**Implementation**: Split into Prepare workflow + Commit workflow; Execute Workflow node bridges.

## Usage

### Detection Mode (default)
Run skill detection on a workflow JSON:
```bash
venv/bin/python scripts/detect_reversibility.py .opencode/skills/reversibility-engine   --workflow /path/to/workflow.json   --output /path/to/reversibility_report.json
```

### Report Format
```json
{
  "workflow_id": "example",
  "total_irreversible": 4,
  "operations": [
    {
      "id": "E2",
      "name": "Database Write",
      "severity": "high",
      "node": "Postgres/Update",
      "description": "Updates user_status column without compensation DELETE",
      "rollback": "Add compensating UPDATE to revert status on failure",
      "auto_fix_possible": true
    },
    {
      "id": "E1",
      "name": "Email Send",
      "severity": "medium",
      "node": "SendGrid",
      "description": "Sends notification email; no recall mechanism",
      "rollback": "Log email ID; add follow-up correction workflow",
      "auto_fix_possible": false
    }
  ],
  "summary": {
    "high_severity": 2,
    "medium_severity": 2,
    "recommendation": "All high-severity irreversible ops need compensation before delivery"
  }
}
```

## Integration with Gate Pipeline

1. **Pre-flight check**: Run `reversibility-engine` before `SchemaPreflightGate`
2. **High-severity flagging**: Any high-severity irreversible op auto-adds to avoid-list
3. **Fix verification**: After adding compensations, re-run to confirm exit 0
4. **Mandatory skills**: When `reversibility-engine` reports >1 high-severity irreversible op without compensation, gate pipeline blocks delivery

## Pairing Recommendations

- **With `n8n-error-boundary-architect`**: Error boundaries provide the execution context for compensations
- **With `gate-first-pass-builder`**: Ensures first-pass success considers rollback paths
- **With `n8n-subworkflow-modularizer`**: Compensations implemented as dedicated sub-workflows
- **With `n8n-syntax-v2-enforcer`**: Concurrent syntax and reversibility quality checks
