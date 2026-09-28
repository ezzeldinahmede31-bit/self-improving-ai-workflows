---
name: idempotency-store
description: "Idempotency store skill (keyed exactly-once records, replay without re-execution, crash-safe). Use for bookings, payments, messages, or any sensitive write that webhooks may deliver twice. Trigger phrases: 'idempotency key', 'exactly once', 'duplicate webhook', 'عدم التكرار'."
---

# Idempotency Store (Same Request Twice, Same Result)

Code: `idempotency.py` (stdlib only, JSON persistence). `make_key()`
derives deterministic keys from namespace + request fields; `execute()`
runs once then replays the recorded result (crashes record nothing,
so retry re-executes safely); `forget()` is explicit-operator only.

## Verification

- `tests/test_p1b_idem_chaos.py` idempotency half green (replay,
  crash-clean, namespace split, forget).
- Every sensitive write path names its key scheme before shipping.

## Pairs with

`saga-compensation-engine` (undo + no-redo), `ecommerce-order-processing-flows`,
`lead-capture-enrichment-routing`, `build-gates-pipeline`.
