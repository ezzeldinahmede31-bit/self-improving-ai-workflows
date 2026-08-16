# Example: Add Email Validation

This directory contains a populated Full-workflow example for a TypeScript email-validation utility. It demonstrates the current directory plan structure and **vertical behavior slices**: each implementation step includes its corresponding tests and focused validation.

## Directory Layout

```text
examples/add-email-validation/
├── README.md
├── context.md
└── 2024-11-04-add-email-validation/
    ├── plan.md
    └── steps/
        ├── step-1.md   # Presence/@ behavior + tests (COMPLETED)
        ├── step-2.md   # Local-part behavior + tests (COMPLETED)
        ├── step-3.md   # Domain/length behavior + tests (IN_PROGRESS)
        └── step-4.md   # Public docs and release note (PENDING)
```

## Files

| File | What it shows |
|---|---|
| [`plan.md`](2024-11-04-add-email-validation/plan.md) | Active task overview with Spec-Lite, decisions, evidence, and statuses |
| [`step-1.md`](2024-11-04-add-email-validation/steps/step-1.md) | Completed vertical slice with implementation and tests |
| [`step-2.md`](2024-11-04-add-email-validation/steps/step-2.md) | Completed local-part behavior slice |
| [`step-3.md`](2024-11-04-add-email-validation/steps/step-3.md) | In-progress domain/length behavior slice |
| [`step-4.md`](2024-11-04-add-email-validation/steps/step-4.md) | Pending public documentation outcome |
| [`context.md`](context.md) | Compact session handoff while Step 3 is active |

Use these files as populated examples, not templates. Copy [`task-overview-template.md`](../../references/task-overview-template.md) and [`step-template.md`](../../references/step-template.md) when creating a real plan.

## Scenario

> **User request:** "Add a standalone function that validates email addresses and returns stable error codes."

Repository discovery found an existing validator/test style and dependency policy. The user confirmed a practical ASCII subset, structured error codes, and no new package. The resulting Full plan implements and tests each behavior group together rather than postponing all tests to a separate phase.
