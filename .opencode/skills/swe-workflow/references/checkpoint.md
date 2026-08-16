# Checkpoint

> Use every 2–3 completed steps and before any session pause.

## Contract

1. Re-read all recently modified files — not from memory.
2. Check for complexity drift: duplication, naming, nesting, coupling.
3. Verify remaining PENDING steps still make sense.
4. Write `plans/context.md` before any pause that might span sessions.

## Reflect on Recent Changes

1. **Re-read files modified** in recent steps with `read`.

2. **Check touched scope for meaningful drift:** duplicated business rules, control flow that obscures behavior, unclear names, new coupling, or temporary artifacts introduced by the task. Treat these as review prompts, not numeric mandates.

3. **Route fixes through scope** — fix only when the current step already authorizes it. Otherwise record the issue and add/approve a scoped step before editing. Re-run affected validation; do not perform opportunistic refactors.

4. **Verify remaining plan:**
   - Re-read PENDING steps — do they still fit current implementation?
   - **Drift signals:** remaining steps reference changed code, descriptions seem outdated, previous steps took much longer than expected.
   - If drifted: summarize to user, propose updates, get confirmation.

## Dump Context Before Pause

Write `plans/context.md` with:

```markdown
# Session Context

> Last Updated: [YYYY-MM-DD HH:MM]

## Current Task
[One sentence]

## Completed Steps
| Step | Summary | Files Changed |
|------|---------|---------------|

## Current Step
**Step N: [Title]** — Status: [IN_PROGRESS|PENDING]
- What was done
- Decisions made

## Key Learnings
- [Gotcha or pattern]

## Next Actions
1. [Ordered next steps]
```

Do NOT include full file contents, detailed diffs, or temporary analysis — reference paths only.

## After Checkpoint

Continue automatically when the approved plan has an unblocked next step. Orient the user briefly; ask only when a blocker, decision, scope change, or requested pause requires input:
> "Completed Steps 1-N. Checks passed: [summary]. Continuing with Step N+1."

## Next Step

→ **execute-step** (next PENDING) or ask user.
