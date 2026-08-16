# Plan Example (Directory Structure)

> A compact mid-execution example using the current required structure. Behavior steps are vertical slices: each includes implementation, tests, and focused validation. Use [`task-overview-template.md`](../references/task-overview-template.md) and [`step-template.md`](../references/step-template.md) as the canonical templates.

---

## Directory Layout

```text
plans/2026-04-28-add-email-validation/
├── plan.md
└── steps/
    ├── step-1.md   # Client validation + tests (COMPLETED)
    └── step-2.md   # Server validation + tests (IN_PROGRESS)
```

## `plan.md` — Task Overview

```markdown
# Plan: Add email validation to user registration

> Status: ACTIVE
> Created: 2026-04-28
> Last Updated: 2026-04-28

## Goal
Registration rejects invalid email formats in both the form and API using the project's existing zod validation pattern.

## Assumptions
- React + TypeScript frontend and Node/Express backend.
- Vitest and eslint are configured.
- zod is already used for API schemas.

## Open Questions
None.

## Spec-Lite

### Acceptance Criteria
- [x] Invalid email is blocked in the registration form with the existing inline-error pattern.
- [ ] Invalid email is rejected by `POST /register` with the existing 400 error shape.
- [ ] Focused client and API tests pass.

### Non-goals
- Email deliverability, DNS/MX lookup, or changes to login.

### Edge Cases
- Empty input, malformed input, and a valid plus-address.

## Design Decisions

| Decision | Options Considered | Chosen | Confirmed |
|----------|--------------------|--------|-----------|
| Validation depth | Client only vs client + server | Client + server — defense in depth | yes |
| Error display | Inline vs toast | Inline — matches `LoginForm.tsx` | yes |
| Validator | New dependency vs zod | zod — already used by auth schemas | yes |

## Steps Overview
| Step | File | Status | Goal |
|------|------|--------|------|
| Step 1 | `steps/step-1.md` | COMPLETED | Add client validation and focused form tests. |
| Step 2 | `steps/step-2.md` | IN_PROGRESS | Add server validation and focused API tests. |

## Validation Commands

| Purpose | Command | Source | Required? |
|---|---|---|---|
| Typecheck | `npx tsc --noEmit` | `package.json` | yes |
| Lint | `npx eslint src/` | `package.json` | yes |
| Test | `npx vitest run` | `package.json` | yes |
| Build | N/A | No configured build | no |

## Context & Learnings
### Key Decisions
- Reuse zod and the existing inline field-error component.
### Gotchas & Warnings
- Client validation improves feedback but never replaces server validation.

> Append only. Never delete or rewrite existing entries below — only add new rows/facts as steps complete.
### Working Set
| Path | Role in this task | Evidence |
|------|-------------------|----------|
| `src/components/RegistrationForm.tsx` | Client validation target | Form and nearby tests read |
| `src/components/__tests__/RegistrationForm.test.tsx` | Client behavior tests | Existing Vitest pattern read |
| `src/api/schemas/auth.ts` | Existing zod schema pattern | Auth schema read |
| `src/api/routes/auth.ts` | Registration API target | Route and error handling read |
| `src/api/__tests__/auth.test.ts` | API behavior tests | Existing route tests read |
### Verified Facts
- zod is already installed and used for auth schemas — verified by `package.json` and `src/api/schemas/auth.ts`.
- `LoginForm.tsx` renders inline errors with `field-error` — verified by file read.
- `POST /register` currently accepts an unchecked email string — verified by route read.

## Implementation Log
| Date | Step | Summary |
|------|------|---------|
| 2026-04-28 | Step 1 | Added client-side zod validation, inline error behavior, and three focused tests. |
```

## `steps/step-1.md` — Completed Vertical Slice

```markdown
# Step 1: Add client validation and tests

> Status: COMPLETED
> Created: 2026-04-28

## Goal
RegistrationForm validates email on blur and submit and reports invalid input with the existing inline-error pattern.

## Prerequisites
- Files to modify: `src/components/RegistrationForm.tsx`, `src/components/__tests__/RegistrationForm.test.tsx`
- Inline error and zod choices confirmed in the task plan.

## Deliverables
- Client email validation on blur and submit.
- Focused tests for valid, invalid, and corrected input.
- After this step: focused RegistrationForm tests pass.

## Plan
- [x] `edit` `src/components/RegistrationForm.tsx` — reuse zod and the inline field-error pattern.
- [x] `edit` `src/components/__tests__/RegistrationForm.test.tsx` — cover valid, invalid, and corrected input.
- [x] `run` `npx vitest run --filter=RegistrationForm` — expect 0 failures.

## Quality Checklist
- [x] Evidence-before-edit: form and tests read; impact isolated to registration form; focused command identified.
- [x] Existing pattern / reuse checked: `LoginForm.tsx` and auth zod schemas.
- [x] Contract understood: prevent submit while invalid and clear the error when corrected.
- [x] Risk reviewed: correctness / accessibility.
- [x] Mitigation recorded: behavior tests and existing accessible error markup retained.

## Validation Checklist
- [x] `npx tsc --noEmit` exits 0.
- [x] `npx eslint src/components/RegistrationForm.tsx` exits 0.

## Test Checklist
- [x] `npx vitest run --filter=RegistrationForm` — 6 tests pass.

## Implementation Notes
Reused the existing zod and inline-error patterns; no dependency or component abstraction was added.

## Files Changed
- `src/components/RegistrationForm.tsx`
- `src/components/__tests__/RegistrationForm.test.tsx`
```

## `steps/step-2.md` — In-Progress Vertical Slice

```markdown
# Step 2: Add server validation and tests

> Status: IN_PROGRESS
> Created: 2026-04-28

## Goal
`POST /register` rejects malformed email input through the existing zod/error-response path.

## Prerequisites
- Step 1 completed.
- Files to modify: `src/api/schemas/auth.ts`, `src/api/routes/auth.ts`, `src/api/__tests__/auth.test.ts`
- Existing 400 error shape verified and unchanged.

## Deliverables
- Register schema validates email.
- Route uses the shared schema and existing 400 response shape.
- Focused API tests cover valid, malformed, and missing email.
- After this step: focused auth API tests pass.

## Plan
- [x] `edit` `src/api/schemas/auth.ts` — add email validation to the register schema.
- [ ] `edit` `src/api/routes/auth.ts` — apply the schema through the existing parse/error path.
- [ ] `edit` `src/api/__tests__/auth.test.ts` — cover valid, malformed, and missing email.
- [ ] `run` `npx vitest run --filter=auth` — expect 0 failures.

## Quality Checklist
- [x] Evidence-before-edit: schema, route, callers, and API tests read.
- [x] Existing pattern / reuse checked: existing auth zod parse/error path.
- [x] Contract understood: preserve the current 400 response shape.
- [x] Risk reviewed: API compatibility / correctness.
- [x] Mitigation recorded: caller search and focused API tests.

## Validation Checklist
- [ ] `npx tsc --noEmit` exits 0.
- [ ] `npx eslint src/api/` exits 0.

## Test Checklist
- [ ] `npx vitest run --filter=auth` — all registration cases pass.

## Implementation Notes
Schema update is complete; route integration and tests remain.

## Files Changed
- `src/api/schemas/auth.ts`
```

---

This example is intentionally mid-execution. Plan-level status remains `ACTIVE`, exactly one writer step is `IN_PROGRESS`, and each behavior step includes its own implementation and tests.
