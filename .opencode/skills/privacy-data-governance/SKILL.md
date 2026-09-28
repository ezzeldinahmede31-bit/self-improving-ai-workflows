---
name: privacy-data-governance
description: "Privacy and data governance skill (classification, retention TTL, export/delete requests, DLP deny-list, minimization). Use when handling personal or medical data, when logs must never carry PII, or when a deletion request arrives. Trigger phrases: 'PII check', 'retention due', 'delete my data', 'خصوصية البيانات'."
---

# Privacy + Data Governance (Classify, Retain, Redact)

Code: `privacy.py` (stdlib only). `classify()` sets level/TTL/
residency per field; `retention_due()` flags expired values;
`record_request()` tracks export/delete jobs; `check_text()`/
`redact()` enforce the DLP deny-list (phones, emails, keys, cards,
national ids, private keys, bearer tokens + caller patterns);
`minimize()` keeps solely declared-necessary fields.

## Verification

- `tests/test_p1c_tenancy_privacy.py` privacy half green (hits,
  redact, minimize, TTL, requests, bad inputs).
- DLP scan gates every log/telemetry/prompt/analytics sink.

## Pairs with

`multi-tenant-platform` (per-tenant data), `secret-scanning-lifecycle-adapter`,
`credential-secret-handling`, `build-gates-pipeline`.
