---
name: end-to-end-workflow-testing
description: "Proves workflows via real executions against fixtures asserting side effects. Use for QA."
---

# End-to-End Workflow Testing

Green checkmarks are not proof — side effects are.

## Workflow
1. Capture fixture payloads per trigger.
2. Execute real flows with stubbed externals.
3. Assert final side effects (records/messages).
4. Verify deliberate break is caught (test can fail).

## Core Rules
- Cover happy, boundary, failure modes.

## Pairs with
- `tdd-sandbox-proof-engine`, `n8n-delivery-verification-gate`, `n8n-e2e-test-runner`
