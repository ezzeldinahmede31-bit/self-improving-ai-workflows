# Task Overview Template

> Copy this file to `plans/<YYYY-MM-DD>-<slug>/plan.md` for every new Full-workflow task. Do not reconstruct from memory. This is the **task overview** — high-level context, design decisions, and working set. Individual steps live in `steps/step-N.md` files.

---

```markdown
# Plan: [Task Name]

> Status: DRAFT | ACTIVE | COMPLETED | ARCHIVED
> Created: YYYY-MM-DD
> Last Updated: YYYY-MM-DD

<!--
  Plan-level status (lifecycle):
    DRAFT     — awaiting approval after clarification
    ACTIVE    — execution in progress
    COMPLETED — all steps done, verified
    ARCHIVED  — optional long-term archival state
  This is distinct from step-level status (PENDING|IN_PROGRESS|COMPLETED|BLOCKED)
  in `steps/step-N.md`. The pre-edit gate checks step status, not plan status.
-->

## Goal
[One sentence describing what "done" looks like.]

## Assumptions
- [What we're taking for granted — verify or make explicit. Label unverified repo claims here until evidence moves them to Verified Facts.]

## Open Questions
None.

## Spec-Lite
> Fill for ambiguous, high-risk, or behavior-heavy work. Otherwise write `N/A — covered by Goal, Deliverables, and Validation.`

### Acceptance Criteria
- [ ] [Observable behavior or outcome that must be true.]

### Non-goals
- [What is explicitly out of scope.]

### Edge Cases
- [Important boundary/failure case, or `N/A`.]

## Design Decisions
> Decisions about UX, schema shape, component structure, or API contract.
> Each must be confirmed by the user before execution begins.
> Write `None — no design-sensitive changes.` if the task is purely logic/config.

| Decision | Options Considered | Chosen | Confirmed |
|----------|--------------------|--------|-----------|
| [e.g. User list layout] | [Table vs Card grid] | [Table — matches /admin pages] | [yes/no] |

## Steps Overview
| Step | File | Status | Goal |
|------|------|--------|------|
| Step 1 | `steps/step-1.md` | PENDING | [One-line goal] |
| Step 2 | `steps/step-2.md` | PENDING | [One-line goal] |
| Step 3 | `steps/step-3.md` | PENDING | [One-line goal] |

## Validation Commands

| Purpose | Command | Source | Required? |
|---|---|---|---|
| Typecheck |   |   |   |
| Lint |   |   |   |
| Test |   |   |   |
| Build |   |   |   |

## Context & Learnings
### Key Decisions
- [Decision]: [Rationale]
### Gotchas & Warnings
- [Warning]: [What to watch out for]

> Append only. Never delete or rewrite existing entries below — only add new rows/facts as steps complete.
### Working Set
| Path | Role in this task | Evidence |
|------|-------------------|----------|
| [path] | [why this file matters] | [read/rg/test/config check used to verify] |
### Verified Facts
- [Fact] — verified by [tool/read/search/config], [date or step].
- Unknowns stay out of Verified Facts until checked; record them in Assumptions, Open Questions, or the current step's Implementation Notes.

## Implementation Log
| Date | Step | Summary |
|------|------|---------|
```

## Required Fields Checklist

For `## Open Questions`, the valid content is exactly `None.`. If any known question would be listed there, do not create or finalize the plan; ask the user in chat first. `DRAFT` means plan review/approval after clarification is complete, not unresolved requirements.

Before marking any step **COMPLETED**, confirm the corresponding `steps/step-N.md` file has all ten required fields populated:

- [ ] **Status** — one of `PENDING`, `IN_PROGRESS`, `COMPLETED`, `BLOCKED`
- [ ] **Goal**
- [ ] **Prerequisites**
- [ ] **Deliverables**
- [ ] **Plan** (action checklist)
- [ ] **Quality Checklist**
- [ ] **Validation Checklist**
- [ ] **Test Checklist** (use `N/A` if no test framework)
- [ ] **Implementation Notes**
- [ ] **Files Changed**

The task overview file must also have:

- [ ] Header block with `Status`, `Created`, `Last Updated`
- [ ] `Goal`, `Assumptions`, `Open Questions` (exactly `None.`), `Spec-Lite` (filled or `N/A`), `Design Decisions` (filled or `None`)
- [ ] `Steps Overview` table listing all steps
- [ ] `Validation Commands` table populated from repo evidence or marked unavailable
- [ ] `Context & Learnings`, including `Working Set` and `Verified Facts`
- [ ] `Implementation Log` table (appended to as steps complete)

## Violations to Avoid

- `### Step N — Title [STATUS]` headers with inline status brackets instead of a `> Status:` field.
- Steps missing any of the ten required fields.
- Horizontal slicing (Step 1 = all types, Step 2 = all logic, Step 3 = all tests). Each step must be a thin vertical slice through the necessary layers — independently verifiable.
- Marking a step **COMPLETED** with known validation or test failures. Either fix them or mark **BLOCKED**.
- Recording guessed paths, APIs, dependencies, or conventions as facts without read/search/tool evidence.
- Creating a new component, utility, hook, or schema pattern without searching for an existing reusable equivalent. Evidence of the search must appear in Verified Facts.
- Making silent design choices (UI layout, schema shape, API contract) without confirming with the user. Surface design decisions in the Design Decisions table.
- Listing unresolved requirement/design questions under `## Open Questions` instead of asking them in chat before planning.
- Adding a step whose purpose is to resolve open questions. Clarification is a pre-plan gate, not implementation work.
- Treating `DRAFT` as permission to leave requirements unresolved. `DRAFT` is only for plan review/approval after clarification is complete.
- Batching multiple steps in a single execution pass.
