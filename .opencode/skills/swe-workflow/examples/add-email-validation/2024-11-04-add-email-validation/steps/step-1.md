# Step 1: Implement presence and at-sign behavior

> Status: COMPLETED
> Created: 2024-11-04

## Goal
Create the public result types and implement/test `EMPTY`, `NO_AT`, and `MULTIPLE_AT` behavior.

## Prerequisites
- Existing `validatePhone` return shape and utils barrel read.
- Files to modify: `src/utils/email.ts`, `src/utils/email.test.ts`, `src/utils/index.ts`.
- Stable error-code representation confirmed.

## Deliverables
- Public `EmailErrorCode`, `EmailValidationResult`, and `validateEmail()` export.
- Presence and `@`-count behavior with focused tests.
- After this step: focused email tests and typecheck pass for the first behavior slice.

## Plan
- [x] `create` `src/utils/email.ts` — add public types and early-return behavior for three codes.
- [x] `edit` `src/utils/index.ts` — export the new types and function.
- [x] `create` `src/utils/email.test.ts` — cover empty, whitespace, missing `@`, multiple `@`, and a baseline valid input.
- [x] `run` `npx vitest run src/utils/email.test.ts` and `npx tsc --noEmit` — expect success.

## Quality Checklist
- [x] Evidence-before-edit: validator, barrel, and test patterns read; validation commands identified.
- [x] Existing pattern / reuse checked: `validatePhone` result shape and `describe.each` style reused.
- [x] Contract understood: stable named exports; function returns and never throws.
- [x] Risk reviewed: correctness / public contract.
- [x] Mitigation recorded: focused branch tests and typecheck.

## Validation Checklist
- [x] `npx tsc --noEmit` exits 0.
- [x] `npx eslint src/utils/email.ts src/utils/email.test.ts` exits 0.

## Test Checklist
- [x] `npx vitest run src/utils/email.test.ts` — baseline plus all three error codes pass.

## Implementation Notes
Kept the first slice intentionally small but complete: public types, export, implementation branches, and tests landed together.

## Files Changed
- `src/utils/email.ts` (created)
- `src/utils/email.test.ts` (created)
- `src/utils/index.ts`
