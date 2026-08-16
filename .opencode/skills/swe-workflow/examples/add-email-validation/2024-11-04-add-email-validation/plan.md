# Plan: Add Email Validation

> Status: ACTIVE
> Created: 2024-11-04
> Last Updated: 2024-11-05

<!--
  Plan-level status (lifecycle):
    DRAFT     — awaiting approval after clarification
    ACTIVE    — execution and final reflection in progress
    COMPLETED — global reflection passed
    ARCHIVED  — optional long-term archival state
-->

## Goal
Provide a standalone `validateEmail(input)` utility that returns stable structured error codes for a practical ASCII email subset.

## Assumptions
- TypeScript project with `src/utils/`, Vitest, eslint, and a utils barrel.
- Format validation only; no DNS/MX deliverability check.
- Error shape: `{ valid: boolean; error?: EmailErrorCode }`.
- The dependency policy disallows adding `validator` for this utility.

## Open Questions
None.

## Spec-Lite

### Acceptance Criteria
- [x] Empty, missing-`@`, and multiple-`@` input returns stable error codes with tests.
- [x] Invalid local parts and the 64-character boundary are tested.
- [ ] Invalid domains and total-length boundaries are tested.
- [ ] Public docs list the signature, codes, and unsupported IDN behavior.

### Non-goals
- Unicode/IDN domains, quoted local parts, comments, or deliverability checks.

### Edge Cases
- Whitespace-only input, consecutive local dots, 64/65-character local parts, missing TLD, and 254/255-character total length.

## Design Decisions

| Decision | Options Considered | Chosen | Confirmed |
|----------|--------------------|--------|-----------|
| Error representation | Strings vs stable codes | Stable union codes — callers can localize | yes |
| Validator | New package vs existing code | Length checks + focused regexes — dependency policy | yes |
| Whitespace | Trim vs reject | Reject — matches `validatePhone` | yes |
| Domain scope | ASCII vs IDN | ASCII practical subset; IDN deferred | yes |

## Steps Overview
| Step | File | Status | Goal |
|------|------|--------|------|
| Step 1 | `steps/step-1.md` | COMPLETED | Implement presence/`@` behavior, types, exports, and tests. |
| Step 2 | `steps/step-2.md` | COMPLETED | Implement local-part behavior and boundary tests. |
| Step 3 | `steps/step-3.md` | IN_PROGRESS | Implement domain/total-length behavior and tests. |
| Step 4 | `steps/step-4.md` | PENDING | Document the verified public contract and release note. |

## Validation Commands

| Purpose | Command | Source | Required? |
|---|---|---|---|
| Typecheck | `npx tsc --noEmit` | `package.json` | yes |
| Lint | `npx eslint src/` | `package.json` | yes |
| Test | `npx vitest run` | `package.json` | yes |
| Build | N/A | No configured build | no |

## Context & Learnings
### Key Decisions
- Implement and test one behavior group per step; do not defer all tests to a later phase.
- Reuse the utils barrel and `describe.each` test style.
### Gotchas & Warnings
- SMTP total length is 254 characters; local-part length is checked independently at 64.
- Client/user-facing integration is outside this standalone utility task.

> Append only. Never delete or rewrite existing entries below — only add new rows/facts as steps complete.
### Working Set
| Path | Role in this task | Evidence |
|------|-------------------|----------|
| `src/utils/email.ts` | Types and validator implementation | Existing validator pattern compared |
| `src/utils/email.test.ts` | Behavior and boundary tests | Vitest pattern from `phone.test.ts` |
| `src/utils/index.ts` | Public barrel export | Existing utils exports read |
| `src/utils/phone.ts` | Return-shape/error-order pattern | File read before planning |
| `src/utils/phone.test.ts` | Parameterized-test pattern | File read before planning |
| `docs/deps-policy.md` | Dependency constraint | File rejects `validator` package |
### Verified Facts
- Vitest and eslint commands come from `package.json`.
- Validators use named exports through `src/utils/index.ts`.
- Validator matrix tests use `describe.each` in `src/utils/phone.test.ts`.
- `docs/deps-policy.md` rejects adding the `validator` package.

## Implementation Log
| Date | Step | Summary |
|------|------|---------|
| 2024-11-04 | Step 1 | Added types, exports, presence/`@` behavior, and focused tests. |
| 2024-11-05 | Step 2 | Added local-part validation and boundary tests. |
| 2024-11-05 | Step 3 | Started domain and total-length implementation/tests. |
