---
name: traceability-links
description: "Requirement traceability skill (requirement registry, test linkage, coverage gaps, delivery gate). Use when a delivery must prove every requirement has a test, when an unlinked requirement must block shipment, or when auditing what-proves-what. Trigger phrases: 'requirement coverage', 'unlinked requirements', 'ready to ship', 'تتبع المتطلبات'."
---

# Traceability Links (No Requirement Ships Unproven)

Code: `traceability.py` (stdlib only, separate JSON store).
`add_requirement(id, statement, acceptance)` registers the contract;
`link_test(id, test_ref, evidence)` attaches proof; `coverage()`
splits linked vs unlinked; `assert_ready(ids)` blocks delivery on gaps
or unknown ids.

## When to use

- Delivery time: assert_ready first, ship after.
- Audits: `requirement(id)` shows statement + acceptance + tests.
- Planning: unlinked list is the test-writing backlog.

## Verification

- `tests/test_p0c_trace.py` green (link/coverage, gap block,
  unknown-key reject, persistence).
- Ship decisions cite the coverage output, not memory.

## Pairs with

`business-invariants` (rule source), `provenance-lineage` (why-chain),
`n8n-delivery-verification-gate` (REQ-evidence table),
`build-gates-pipeline`.
