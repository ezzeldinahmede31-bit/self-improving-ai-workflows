# Step 2: Implement local-part behavior

> Status: COMPLETED
> Created: 2024-11-04

## Goal
Reject invalid local parts and enforce the 64-character local-part boundary with tests.

## Prerequisites
- Step 1 completed with public types, baseline function, and test file.
- Files to modify: `src/utils/email.ts`, `src/utils/email.test.ts`.
- Practical ASCII subset confirmed.

## Deliverables
- `INVALID_LOCAL` behavior for dots, unsupported characters, and excessive length.
- Boundary tests for 64 valid and 65 invalid local-part characters.
- After this step: focused email tests and lint pass for local-part behavior.

## Plan
- [x] `edit` `src/utils/email.ts` — add local-part length check and focused `LOCAL_RE`.
- [x] `edit` `src/utils/email.test.ts` — cover leading/trailing/consecutive dots, characters, and 64/65 boundaries.
- [x] `run` `npx vitest run src/utils/email.test.ts` and `npx eslint src/utils/` — expect success.

## Quality Checklist
- [x] Evidence-before-edit: Step 1 implementation/tests reread; RFC boundary verified from task evidence.
- [x] Existing pattern / reuse checked: early-return error ordering retained.
- [x] Contract understood: local-part failures return `INVALID_LOCAL` without throwing.
- [x] Risk reviewed: regex correctness / boundary ordering.
- [x] Mitigation recorded: table-driven examples and explicit 64/65 tests.

## Validation Checklist
- [x] `npx tsc --noEmit` exits 0.
- [x] `npx eslint src/utils/` exits 0.

## Test Checklist
- [x] `npx vitest run src/utils/email.test.ts` — local-part cases and prior cases pass.

## Implementation Notes
Used a focused local-part expression instead of a single email mega-regex so error codes remain deterministic and tests map directly to behavior.

## Files Changed
- `src/utils/email.ts`
- `src/utils/email.test.ts`
