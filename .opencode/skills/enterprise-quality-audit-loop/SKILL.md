---
name: enterprise-quality-audit-loop
description: "Deterministic Quality & ISO/IEC 25010 compliance gate paired with an automated feedback and self-correction loop. Use whenever generating or editing n8n workflow JSON or Code-node scripts, to enforce Schema V2 syntax, graph integrity, and reliability before deploy."
---

# ENTERPRISE QUALITY AUDIT & SELF-HEALING LOOP

## DIRECTIVE
Ensure high reliability, maintainability, structural integrity, and strict
adherence to n8n Schema V2 standards. Automatically collect audit flaws and
re-feed them to the generator in a deterministic retry loop (max 3 attempts).

## AUDIT & QUALITY METRICS

1. **SYNTAX V2 ENFORCEMENT:**
   - BAN deprecated syntax: `$node[]`, `$json` (without an explicit input
     reference).
   - MANDATE V2 expressions: `$input.first().json`, `$input.item.json`,
     `$input.all().map(...)`, conditional `$input.first().json.field` checks.
   - Code nodes must use `$input.item.json` / `$input.first().json`, never bare
     `$json` or `$node["X"]`.
   - Ban `moment.js`; force Luxon / JS built-ins for date handling.

2. **GRAPH INTEGRITY & MAINTAINABILITY:**
   - Ensure ZERO isolated/unreachable nodes in the execution graph (every node
     must have at least one incoming path from the trigger and be reachable).
   - Enforce cyclomatic complexity limits (< 10) inside custom
     JavaScript/Python Code Nodes. Split logic beyond that into multiple Code
     nodes or a sub-workflow.
   - Enforce verb-prefixed, discoverable node names (e.g. `Send Slack Alert`).
   - Flag any workflow > ~10 nodes: recommend sub-workflow extraction.

3. **RELIABILITY & FAULT TOLERANCE:**
   - Mandatory inclusion of `Error Trigger` nodes or `onError:
     "continueRegularOutput"` configurations for critical nodes.
   - Mandatory `pinnedData` generation on primary nodes for instant unit testing.
   - Verify rate-limit / cost guards exist for workflows that call external
     paid or rate-limited services.

## SELF-HEALING LOOP EXECUTION

```
[WORKFLOW GENERATION] ──► [QUALITY AUDIT CHECK]
│
┌────────────────┴────────────────┐
▼                                 ▼
[PASS: Score >= 80]              [FAIL: Score < 80]
│                                 │
▼                                 ▼
[PROCEED TO MCP DEPLOY]         [GENERATE AUDIT PAYLOAD]
│
▼
[RETRY LOOP: Attempt <= 3]
│
▼
[LLM SELF-CORRECTION]
```

Scoring: start at 100. Deduct per violation (e.g. -15 deprecated syntax, -10
isolated node, -10 missing error handling, -5 missing pinnedData, -5 complexity
breach). Below 80 = FAIL.

## FEEDBACK PROMPT SCHEMA
When auditing fails, format the feedback prompt strictly as follows:

```
❌ QUALITY AUDIT FAILED (Attempt {attempt_number}/3)
VIOLATIONS DETECTED:

- {violation_1}
- {violation_2}

REQUIRED FIX: Adjust the JSON/Code to eliminate the violations above while
preserving original business logic. Re-output ONLY the updated JSON.
```

Rules:
- Exactly one retry input per attempt. Do NOT dump whole workflow context again.
- If attempt 3 fails, STOP and hand back to the user with the full violation
  list — never deploy a failing artifact silently.

## OUTPUT CONTRACT
After the loop:
- Audit score (0-100) and attempt count.
- Violations fixed vs remaining.
- Final decision: DEPLOY / FAIL (deferred to human).