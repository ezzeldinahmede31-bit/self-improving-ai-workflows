# Step 3: Implement domain and total-length behavior

> Status: IN_PROGRESS
> Created: 2024-11-04

## Goal
Reject invalid domains and enforce the 254-character total-length boundary with focused tests.

## Prerequisites
- Step 2 completed with local-part behavior protected by tests.
- Files to modify: `src/utils/email.ts`, `src/utils/email.test.ts`.
- IDN/Unicode domains remain explicitly out of scope.

## Deliverables
- `INVALID_DOMAIN` behavior for missing/invalid labels and TLDs.
- `TOO_LONG` behavior with 254/255 total-length boundary tests.
- After this step: the complete validator matrix passes focused test, lint, and typecheck commands.

## Plan
- [x] `edit` `src/utils/email.ts` — add total-length check and focused `DOMAIN_RE`.
- [ ] `edit` `src/utils/email.test.ts` — cover missing TLD, short TLD, label hyphens, and valid subdomains.
- [ ] `edit` `src/utils/email.test.ts` — add explicit 254-valid and 255-invalid boundaries.
- [ ] `run` `npx vitest run src/utils/email.test.ts`, lint, and typecheck — expect success.

## Quality Checklist
- [x] Evidence-before-edit: implementation/tests reread and domain scope confirmed.
- [x] Existing pattern / reuse checked: early-return order and parameterized tests retained.
- [x] Contract understood: total length is checked before domain parsing; ASCII-only scope is explicit.
- [x] Risk reviewed: regex correctness / off-by-one boundaries.
- [x] Mitigation recorded: focused domain matrix and explicit boundary construction.

## Validation Checklist
- [ ] `npx tsc --noEmit` exits 0.
- [ ] `npx eslint src/utils/` exits 0.

## Test Checklist
- [ ] `npx vitest run src/utils/email.test.ts` — all prior, domain, and total-length cases pass.

## Implementation Notes
Implementation branches are present. Domain matrix and total-length boundary tests remain before completion.

## Files Changed
- `src/utils/email.ts`
