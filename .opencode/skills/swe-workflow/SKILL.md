---
name: swe-workflow
description: >-
  REQUIRED for every code-related task. Read SKILL.md before acting, then start
  the reply with workflow triage. Use `Workflow mode: Lightweight — <reason>;
  success: <outcome>; plan: no.` for clear localized changes and read-only
  review or discovery. Use the Full triage block and persisted plan for risky,
  coupled, cross-session, or contract-changing implementation. Escalate from
  Lightweight before target-file edits when discovery reveals Full-mode risk.
  Focused delegated agents follow Delegated Mode instead.
license: MIT
compatibility: Requires file read/search/edit capabilities; shell and Git are recommended for validation.
metadata:
  version: "1.12.2"
  author: "Evan Xu"
---

# SWE Workflow

> Every code task starts with workflow triage. Bounded work stays lightweight; risky or coordination-heavy implementation uses a persisted plan.

## Contract

1. **Triage first.** Start the first reply to a code-related task with one of these declarations:
   ```text
   Workflow mode: Lightweight — <reason>; success: <outcome>; plan: no.
   ```
   ```text
   Workflow mode: Full
   Reason: <one sentence>
   Success criteria:
   - <what done means>
   Plan needed: yes
   ```
2. **Lightweight is the default** for clear localized changes, bounded investigation, and read-only reviews or discovery—even when many files must be inspected. It uses the Behavioral Guards but no persisted plan.
3. **Full is required before implementation** when work is risky or hard to reverse; changes API/schema/migration/security/configuration contracts; couples multiple subsystems; is a broad refactor/migration/cleanup; needs durable multi-session or multi-agent coordination; remains materially ambiguous after bounded discovery; or the user requests a plan. File count alone is a signal, not a trigger.
4. **Escalate before target-file edits.** Lightweight discovery may gather evidence first. If Full criteria emerge, stop before mutating task files, declare Full mode, clarify decision-critical questions, create the plan, and then resume. If edits already began, preserve the verified state and escalate before expanding scope.
5. **Pre-edit gate (Full mode).** Before mutating task target files: a plan directory must exist under `plans/<YYYY-MM-DD>-<slug>/`, exactly one step file must have `> Status: IN_PROGRESS`, and the edit must map to that step. Read-only exploration and workflow-bookkeeping updates are allowed before this gate.
6. **Plan file format.** Copy [`references/task-overview-template.md`](references/task-overview-template.md) to `plan.md` and [`references/step-template.md`](references/step-template.md) to each step file. Every step has ten fields: `Status`, `Goal`, `Prerequisites`, `Deliverables`, `Plan`, `Quality Checklist`, `Validation Checklist`, `Test Checklist`, `Implementation Notes`, `Files Changed`.
7. **Clarification gate (Full mode).** Ask only decision-critical questions that repository evidence cannot answer. A valid plan has `Open Questions: None.`; the plan approval is the sole routine pre-execution approval.
8. **One writer step at a time.** Exactly one step may authorize active-worktree writes. Independent read-only investigation or validation may run concurrently. Never mark `COMPLETED` with known failures—fix through an authorized step or mark `BLOCKED`.

## Delegated Mode

When **all** of the following are true, skip triage/plan/pre-edit gate:

1. Task assigned by another agent or orchestrator (not an open-ended user request)
2. Explicit scope, success criteria, or acceptance contract received
3. Operating in a focused role (implementer, reviewer, analyst, etc.)

In Delegated Mode: follow all Behavioral Guards and [`references/code-quality.md`](references/code-quality.md); report changed files, commands, validation evidence, and surprises; escalate unapproved design/architecture decisions; stay in scope.

## Statuses

**Plan-level** (`plan.md`): `DRAFT` → `ACTIVE` → `COMPLETED` → `ARCHIVED`
**Step-level** (`steps/step-N.md`): `PENDING` → `IN_PROGRESS` → `COMPLETED` | `BLOCKED`

Only one writer step may be `IN_PROGRESS` at a time. The pre-edit gate checks step-level status. The plan remains `ACTIVE` after execution steps finish and becomes `COMPLETED` only after global reflection passes.

## Reference Loading

Load only what the current phase needs:

- **Planning:** [`references/create-plan.md`](references/create-plan.md), [`references/task-overview-template.md`](references/task-overview-template.md), [`references/step-template.md`](references/step-template.md)
- **Execution:** [`references/execute-step.md`](references/execute-step.md), [`references/code-quality.md`](references/code-quality.md)
- **Verification:** [`references/verify-step.md`](references/verify-step.md)
- **Command discovery:** [`references/command-discovery.md`](references/command-discovery.md)
- **Risk review:** [`references/risk-classification.md`](references/risk-classification.md)
- **Project setup:** [`references/project-agents-template.md`](references/project-agents-template.md)

## Behavioral Guards

Active for the entire session. Do not drift.

1. **Evidence first** — read target files before editing; search callers/usages before changing shared behavior; label claims as `Verified`/`Assumption`/`Unknown`.
2. **Anti-shortcut gate** — before editing: target read ✓, impact search (or `N/A — isolated`) ✓, validation command (or skipped reason) ✓.
3. **Think in code** — for aggregate analysis, prefer short scripts/commands that compute results over many raw file dumps. For noisy output, store in `/tmp`, print bounded slice.
4. **Minimalism ladder** — before adding code, prefer: delete/skip if not needed → stdlib/native feature → existing dependency/helper → smallest safe implementation; never cut security, data safety, accessibility, or explicit requirements.
5. **Surgical changes** — touch only needed files/lines; match existing formatting, naming, and conventions; do not copy degraded patterns.
6. **Reuse before create** — search for existing equivalents before writing new components/utilities/patterns; evidence of search in Verified Facts.
7. **Design discipline** — do not make silent design choices. Surface decisions for user confirmation. Verify approach matches conventions or Design Decisions table.
8. **Goal-driven** — define success before coding; verify via tests/lint/build/typecheck; add focused tests for new code and bug fixes; fix introduced issues or report blockers.

## Full Workflow Phases

1. **Clarify** — resolve only decision-critical ambiguity that repository evidence cannot answer. See [`references/require-clarification.md`](references/require-clarification.md).
2. **Plan** — break into vertical-slice steps. See [`references/create-plan.md`](references/create-plan.md).
3. **Execute** — one step at a time: [`references/execute-step.md`](references/execute-step.md) → [`references/verify-step.md`](references/verify-step.md) → [`references/persist-plan.md`](references/persist-plan.md). Every 2–3 steps: [`references/checkpoint.md`](references/checkpoint.md). Before pausing: dump context.
4. **Reflect** — after all execution steps are done, keep the plan `ACTIVE`; [`references/global-reflection.md`](references/global-reflection.md) owns final plan completion.

### Resume Protocol

New session → read `plans/context.md` → relevant `plan.md` → current step file. See [`references/resume-workflow.md`](references/resume-workflow.md).
