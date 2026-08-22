---
name: ecommerce-order-processing-flows
description: "Automates order lifecycles with idempotent steps + reconciliation. Use for shop orders."
---

# E-commerce Order Processing Flows

Orders involve money — idempotent + reconcilable.

## Workflow
1. Diagram lifecycle: created -> paid -> fulfilled -> shipped -> delivered -> refunded.
2. Each transition idempotent with key.
3. Centralize notifications per transition.
4. Nightly reconcile platform vs payment vs fulfillment.

## Core Rules
- Refunds first-class, tested like purchases.

## Pairs with
- `shopify-automation`, `stripe-dispute`, `idempotency-key-design`
