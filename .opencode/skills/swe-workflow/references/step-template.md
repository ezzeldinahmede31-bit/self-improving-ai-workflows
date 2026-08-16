# Step Template

> Copy this file verbatim to `plans/<YYYY-MM-DD>-<slug>/steps/step-N.md` for every step. Do not reconstruct from memory. Each step file is a focused, self-contained slice of the task — typically 20–40 lines, designed to fit cleanly in a small LLM's context window.

---

```markdown
# Step N: [Title]

> Status: PENDING | IN_PROGRESS | COMPLETED | BLOCKED
> Created: YYYY-MM-DD

## Goal
[One sentence describing what this step produces.]

## Prerequisites
- [Step N-1 completed — specific artifact exists, e.g. "`UserService` class created"]
- [Files to modify: `src/auth/validate.ts`, `src/auth/__tests__/validate.test.ts`]
- [Design: confirm approach with user before implementing (if design-sensitive)]

## Deliverables
- [What this step produces, e.g. "`validateEmail()` accepts an `options` parameter"]
- [After this step: `npm test -- --filter=validate` passes]

## Plan
- [ ] `edit` src/auth/validate.ts — add `options: ValidateOptions` parameter to `validateEmail()`
- [ ] `create` src/auth/__tests__/validate.test.ts — add focused happy-path and invalid-email coverage
- [ ] `run` `npm test -- --filter=validate` — expect 0 failures

## Quality Checklist
> Evidence summary only. Detailed guidance lives in `references/code-quality.md`, `references/risk-classification.md`, and `references/verify-step.md`.

- [ ] Evidence-before-edit: target read [path], impact search [cmd or N/A], validation [cmd or skipped reason]
- [ ] Existing pattern / reuse checked: [path/search evidence]
- [ ] Contract understood: [inputs/outputs/errors/side effects]
- [ ] Risk reviewed: [none or risk categories]
- [ ] Mitigation recorded: [test/check/design constraint]

## Validation Checklist
- [ ] `npm run build` exits 0
- [ ] `npm run lint` exits 0

## Test Checklist
- [ ] `npm test -- --filter=validate` — all pass (or `N/A` if no test framework)

## Implementation Notes
[Fill after implementation — what actually happened, surprises, deviations.]

## Files Changed
[List exact paths after implementation.]
```

## Required Fields Checklist

Before marking any step **COMPLETED**, confirm all fields below are populated:

- [ ] **Status** — one of `PENDING`, `IN_PROGRESS`, `COMPLETED`, `BLOCKED`
- [ ] **Goal** — one-sentence description
- [ ] **Prerequisites** — explicit dependencies listed
- [ ] **Deliverables** — what this step produces + observable outcome
- [ ] **Plan** — action checklist with capability + file path/query + specific change
- [ ] **Quality Checklist** — evidence summary, not duplicated quality doctrine
- [ ] **Validation Checklist** — build/lint commands
- [ ] **Test Checklist** — test commands or `N/A`
- [ ] **Implementation Notes** — filled after execution
- [ ] **Files Changed** — exact paths

## Why This Format

This step template is intentionally compact so each file fits cleanly in a small LLM's working context:

- Each file is 20–40 lines, scoped to a single vertical slice of the task
- Context noise from other steps is eliminated (they live in separate files)
- Reading just the current step + the task overview is sufficient for execution
- Easier to diff and track per-step progress in git

## Violations to Avoid

- `### Step N — Title [STATUS]` headers instead of a top-level `> Status:` field
- Steps missing any of the ten required fields
- Horizontal slicing (Step 1 = all types, Step 2 = all logic). Each step must be a thin vertical slice.
- Marking **COMPLETED** with known validation or test failures — fix them or mark **BLOCKED**.
- Listing guesses as facts without evidence.
