---
name: long-horizon-executor
description: "Survive long, many-step tasks without losing the thread or compounding errors: plan first, checkpoint state to disk, verify each step, and recover explicitly instead of plowing on. Use for any multi-file refactor, feature build, debugging across modules, migration, or any job likely to take 5+ steps. Trigger phrases: 'implement', 'refactor', 'migrate', 'build a', bug fixes across files, or any task list with 3+ items."
---

# Long Horizon Executor

The failure mode of a small model on a long task is not intelligence — it is
**drift**: early steps get contradicted by late ones, or one wrong assumption
contaminates everything after it. This skill makes the run checkpointed and
auditable, like a frontier pipeline.

## Protocol

1. **Plan to a file.** Use `todowrite` (or write `PLAN.md`) with the full
   dependency-ordered step list BEFORE touching code. Each item = one testable
   unit.
2. **Smallest reversible step.** Each edit is one logical change. Read the
   surrounding context of the target file first (`Read` before `Edit`).
3. **Checkpoint after each step.** Update the todo (mark done / blocked) and, in
   ≤2 lines, what changed at `file:line`. This is the recovery point.
4. **Verify after each step, not at the end.** Run the relevant tests / lint /
   a tiny assertion the moment a step is done. A broken step found now costs
   minutes; found at the end costs retries of everything after it.
5. **Explicit recovery on failure.** If a step fails: STOP advancing. State what
   was tried, the actual error, and one candidate next move. Do not silently
   bypass the failure with a different approach unless you say so and re-verify
   the affected earlier steps.
6. **No silent scope creep.** If the work requires touching files outside the
   original plan, stop and tell the user (or add a todo item) instead of
   expanding silently.
7. **Final gate:** before finishing, re-run the whole verification set once and
   confirm every todo is `completed` with evidence (test output, lint pass).

## When NOT to use
Single-step tasks (rename one variable, answer a question) do not need this —
the overhead is not worth it. Use judgment; the threshold is roughly 3+
interdependent steps.