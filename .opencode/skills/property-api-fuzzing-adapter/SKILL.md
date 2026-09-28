---
name: property-api-fuzzing-adapter
description: "Property-based API fuzzing adapter (schema-driven generation, shrinking reproducers, stateful workflow tests, SARIF/JUnit output). Use when an API/webhook surface needs systematic testing beyond hand-written cases, when minimal reproducers are required, or when stateful create-read-update-delete chains must be verified. Trigger phrases: 'fuzz this API', 'property-based test', 'schemathesis', 'hypothesis', 'فحص شامل للـ API'."
---

# Property API Fuzzing Adapter (Schema → Tests → Minimal Repro)

Adapter over **Schemathesis** (OpenAPI/GraphQL → thousands of cases,
Hypothesis engine, stateful testing, SARIF/JUnit/HAR output; prod users
incl. Netflix/SAP/RedHat) and **Hypothesis** (strategies + shrinking +
example database + seeds). Upgrades our `attack_fuzzer.py`
(mutation-based) with a second engine: constrained generation shaped by
the schema.

## When to use

- Any webhook/API trigger surface before production: schema-driven
  phases (examples → coverage → fuzzing → stateful).
- Reproducer quality matters: shrinking turns a 10k-char crasher into
  the minimal failing input automatically.
- Stateful chains (create→read→update→delete, incl. "update after
  delete"): define OpenAPI links or programmatic `add_link()`.

## Steps

1. Point at the schema (OpenAPI 2/3.x file/URL or GraphQL); zero-config
   CLI run first (`st run`), library/pytest integration for the suite.
2. Phase in: per-PR fast combo (examples+coverage+fuzzing, minutes);
   scheduled deep scans deterministic (`--seed`, time-boxed).
3. Stateful: seed realistic data first, declare links for lifecycle
   ops, review inferred state-machine scenarios before trusting them.
4. Auth via hooks; custom checks for domain invariants ("never 500",
   "POST valid → 201/400 only"); replay `.hypothesis` failures first
   every run.
5. Hypothesis unit-level: strategies mirror input schemas
   (emails/ints-in-range/lists/text), assert PROPERTIES not examples,
   keep seeds for repro.
6. Findings → minimal repro + seed archived; 5xx/contract breaks block
   the gate; results in JUnit/SARIF for CI.

## Verification

- No 5xx on valid or invalid inputs; contract violations zero.
- Every failure ships with seed + shrunk reproducer + replay passing.
- Stateful lifecycle chains green on seeded data.

## Pairs with

`n8n-e2e-test-runner` (live execution), `end-to-end-workflow-testing`,
`build-gates-pipeline` (QUALITY/INTEGRITY), `hitl-patterns` for
destructive-test approvals.
