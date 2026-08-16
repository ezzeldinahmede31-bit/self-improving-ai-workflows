# Resume Workflow

## Contract — Read This First

1. Memory is unreliable. Files + current-workspace verification are truth.
2. If `plans/context.md` exists, read it first as a session snapshot.
3. Find candidate work by scanning `plans/<YYYY-MM-DD>-<slug>/plan.md` files and each task's step statuses.
4. Confirm `Open Questions` is `None.` — if not, ask in chat before resuming.
5. Find resume point: IN_PROGRESS → continue after verifying state; PENDING → next step; BLOCKED → note reason; all COMPLETED → global-reflection.
6. Re-verify target files and prerequisites in the current workspace before editing.
7. Orient the user with a brief summary before continuing.

## Instructions

### Step 1: Read Context File

```bash
cat plans/context.md 2>/dev/null || echo "No context snapshot found"
```

If `plans/context.md` exists, read it completely. Capture: current task/step, completed work, decisions, active files, Working Set, open questions, next actions. Treat it as a session snapshot; permanent state lives in `plan.md` and step files.

### Step 2: Discover Plan Directories

Use a focused scan to find task plans:

```bash
find plans -mindepth 2 -maxdepth 2 -name plan.md 2>/dev/null | sort
rg -n "^> Status:|^\| Step .* \|" plans/*/plan.md plans/*/steps/*.md 2>/dev/null
```

Read likely active task overviews first: plans with plan-level `ACTIVE`, incomplete step rows, or names matching the user's request. If multiple active plans exist, ask the user which to resume.

### Step 3: Read the Task Overview

Read `plans/<YYYY-MM-DD>-<slug>/plan.md`. Read all sections: Goal, Assumptions, Open Questions, Design Decisions, Context & Learnings, Steps Overview table, Implementation Log.

If `Open Questions` is not `None.`, stop and ask in chat before resuming.

### Step 4: Read the Active Step File

Based on the resume point (IN_PROGRESS / PENDING), read the relevant step file:
- `plans/<YYYY-MM-DD>-<slug>/steps/step-N.md` for the current/in-progress step
- Check each step file's status to find the right one

Step file status is authoritative. If a step file conflicts with the plan overview table, trust the step file and sync `plan.md` before continuing.

### Step 5: Find Resume Point

| Status | Action |
|--------|--------|
| IN_PROGRESS | Read Implementation Notes from step file, verify current state, continue |
| PENDING | This is the next step to implement |
| BLOCKED | Note reason, try next unblocked step if safe |
| All COMPLETED | Proceed to global-reflection |

Cross-check with context file. If it disagrees significantly with `plan.md` or step files, trust persisted plan/step state for status and ask the user before changing direction.

### Step 6: Verify Prerequisites and Evidence

1. Read the current step's Prerequisites from its step file.
2. Confirm required files/facts in Working Set or Verified Facts from plan overview.
3. Re-verify stale or branch-sensitive facts in current workspace.
4. Read target files before editing.

### Step 7: Orient User

```markdown
**Resuming:** [task name] (`plans/<YYYY-MM-DD>-<slug>/`)
**Read:** context.md [✓/absent], plan.md ✓, steps/step-N.md ✓
**Progress:** Completed [X, Y, Z]. Current: Step N — [title]. Remaining: [N steps].
**Key facts:** [verified decision or fact]
Continue with Step N, or adjust plan?
```

### Step 8: Resume Execution

Continue with execute-step. One step IN_PROGRESS, stay within plan, verify before editing.

## Mandatory Checklist

| Check | Why |
|-------|-----|
| Context read or confirmed absent | Know where work stopped |
| Plan directories scanned | Find active/incomplete work without relying on memory |
| Plan overview read completely | Know full scope |
| Active step file read | Know current context without noise from other steps |
| Step status cross-checked against Steps Overview | Catch stale summaries |
| Open Questions is `None.` | No unresolved requirements |
| Design Decisions reviewed | Know confirmed choices |
| Resume point identified | Know what's next |
| Working Set and Verified Facts reviewed | No hallucinated paths/APIs |
| Prerequisites verified in current workspace | No stale assumptions |
| User oriented | No drift |

## Edge Cases

| Situation | Action |
|---|---|
| No context snapshot | Scan plan directories and ask user if multiple candidates exist |
| Context and plan disagree | Trust plan/step files for status, context for recent session notes; ask if ambiguous |
| Multiple active plans | Ask user which to resume |
| Plan overview and step file disagree | Trust step file status and sync `plan.md` |
| Plan looks stale | Ask: continue, update, or start fresh? |

## Next Step

→ **execute-step** (next PENDING or IN_PROGRESS step from its step file), or **require-clarification** if no plan exists.
