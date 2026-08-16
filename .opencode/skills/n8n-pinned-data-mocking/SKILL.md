---
name: n8n-pinned-data-mocking
description: "Generate realistic pinned data inside every n8n node so the workflow can be tested instantly in the n8n UI without firing the real trigger. Use ONLY when creating or editing n8n workflows meant for immediate manual testing, demos, or development."
---

# n8n Pinned Data Mocking

Pinned data lets the user press "Execute Node" and see realistic output instantly,
without a live webhook, paid API call, or waiting on an LLM. Every node where output
data can be predicted should ship with `pinnedData`.

## What goes into the workflow JSON

Each node object supports a `pinnedData` array. Shape:

```json
{
  "id": "abc",
  "name": "Clean Data",
  "typeVersion": 2.1,
  "pinnedData": [
    {
      "index": 0,
      "json": { "field": "value" },
      "binary": {}
    }
  ],
  "position": [560, 300],
  "type": "n8n-nodes-base.code"
}
```

- `index` must be the run index.
- `json` must match exactly what the node's logic would emit (shape parity).
- `binary` present only for file/image nodes; else `{}`.

## Rules

1. **Every non-trigger node** with deterministic output gets `pinnedData`.
2. Workbook-scale mocks: provide 2–3 representative items (small / medium / large payloads).
3. Trigger nodes get pinned data showing a representative incoming payload (a fake
   Telegram message or webhook body) so the whole chain can be run from the trigger.
4. Secrets in pinned data are placeholders like `"YOUR_EMAIL"` — mock values only,
   never real credentials.
5. Schema parity: the pinned JSON keys must match the node's real code/normalization
   so downstream nodes resolve expressions correctly.

## When generating a mock
- Base it on the node's actual transformation logic, not a copy-paste of the input.
- Include the edge-case item (empty value, missing field) to prove robustness.
- Mark the mock with a field like `"_mock": true` ONLY if it does not disturb downstream filters; otherwise keep clean.

## Acceptance
- [ ] Every node (except ones requiring live calls) has `pinnedData`.
- [ ] Executing the first node in n8n UI yields sensible output within one click.
- [ ] No real credential or API secret exists inside any pinned payload.