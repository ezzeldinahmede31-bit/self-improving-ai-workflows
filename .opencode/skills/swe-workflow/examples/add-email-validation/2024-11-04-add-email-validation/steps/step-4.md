# Step 4: Document the verified public contract

> Status: PENDING
> Created: 2024-11-04

## Goal
Document the validated `validateEmail()` contract and record the user-visible addition.

## Prerequisites
- Step 3 completed and the full behavior matrix passes.
- Files to modify: `docs/utils.md`, `CHANGELOG.md`.
- Public signature, error codes, boundaries, and non-goals are fixed by passing tests.

## Deliverables
- Public docs list the signature, all codes, supported boundaries, and IDN non-goal.
- Unreleased changelog entry describes the utility.
- After this step: docs links resolve and the documented contract matches tests.

## Plan
- [ ] `edit` `docs/utils.md` — add signature, result examples, code table, boundaries, and non-goals.
- [ ] `edit` `CHANGELOG.md` — add the utility under Unreleased.
- [ ] `run` the configured Markdown/link check — expect success.

## Quality Checklist
- [ ] Evidence-before-edit: passing tests and neighboring docs reread; docs command identified.
- [ ] Existing pattern / reuse checked: `validatePhone` docs section reused.
- [ ] Contract understood: document only behavior protected by completed tests.
- [ ] Risk reviewed: documentation drift.
- [ ] Mitigation recorded: compare docs against types/tests and run link validation.

## Validation Checklist
- [ ] Configured Markdown/link check exits 0.
- [ ] `git diff --check` exits 0.

## Test Checklist
- [ ] Manual contract comparison: every documented code and boundary has a passing behavior test.

## Implementation Notes
Pending Step 3 completion.

## Files Changed
None yet.
