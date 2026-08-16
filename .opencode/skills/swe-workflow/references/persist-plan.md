# Persist Plan

## Contract — Read This First

1. The plan directory is the source of truth — update it as soon as reality changes.
2. Step files own execution status; `plan.md` owns lifecycle status and the human-readable Steps Overview.
3. Keep the plan `ACTIVE` after execution steps finish; only a successful global reflection sets plan-level `COMPLETED`.
4. Never mark a step `COMPLETED` with known introduced issues — fix or mark `BLOCKED`.
5. Every `COMPLETED` step file must have all ten fields populated with evidence-backed entries.
6. Never leave `IN_PROGRESS` across sessions — complete, block, or dump context.
7. Use targeted edits for status changes; do not rewrite whole plan files.
8. After persisting, orient the user with a progress summary.

## When to Use

After marking IN_PROGRESS, after implementation, after verification, after COMPLETED/BLOCKED, before asking user to continue.

## State Ownership

| File | Owns | Do not duplicate |
|---|---|---|
| `plan.md` | Plan-level status, Goal, Spec-Lite, Design Decisions, Steps Overview, Working Set, Verified Facts, Validation Commands, Implementation Log | Per-step implementation details |
| `steps/step-N.md` | Authoritative step status, plan bullets, checklists, Implementation Notes, Files Changed | Full task history |
| `plans/context.md` | Optional session handoff snapshot | Permanent facts already in plan/step files |

If `plan.md` Steps Overview conflicts with a step file, trust the step file and sync `plan.md`.

## After Starting a Step

1. In the step file: Change `> Status: PENDING` → `> Status: IN_PROGRESS`.
2. In the plan overview: update the matching Steps Overview row and `Last Updated`.
3. If transitioning from draft to execution, set plan-level status to `ACTIVE`.

## After Completing Implementation

Update the current step file with:
- **Implementation Notes:** what changed, why, decisions, deviations
- **Files Changed:** exact paths created/modified/deleted
- **Working Set / Verified Facts:** updated with evidence (not guesses) in the plan overview

## After Verification Passes

1. Confirm all ten fields populated in the step file.
2. Check off Quality, Validation, and Test Checklist items in the step file.
3. Confirm introduced issues fixed, or mark BLOCKED.
4. Update plan overview's Context & Learnings with durable decisions/gotchas.
5. In the step file: Change `> Status: IN_PROGRESS` → `> Status: COMPLETED`.
6. In the plan overview: update the matching Steps Overview row and `Last Updated`.
7. If all current step files are `COMPLETED`, keep plan-level status `ACTIVE` and proceed to `global-reflection`.
8. Add an Implementation Log row in the plan overview.

## After Blocking a Step

1. In the step file: Change status to **BLOCKED**.
2. Document blocker, evidence, and unblock path.
3. In the plan overview: update the matching Steps Overview row and `Last Updated`.
4. Proceed to next safe PENDING step or report to user.

## When Scope Changes

1. Stop implementation.
2. Read the entire plan overview and all step files in dependency order.
3. Update steps in dependency order (add/remove/reorder as needed).
4. Document in Implementation Notes or Deviations.
5. Update the Steps Overview table to match step files.
6. Ensure exactly one step is IN_PROGRESS before resuming.

## Before Asking User "Should I Continue?"

1. Write current state to `plans/context.md` (see [checkpoint](checkpoint.md)).
2. Then ask the user.

## Mandatory Updates When Marking COMPLETED

- [ ] Step file: Status → COMPLETED
- [ ] Step file: Implementation Notes filled (what/why/decisions)
- [ ] Step file: Files Changed lists exact paths
- [ ] Plan overview: matching Steps Overview row updated
- [ ] Plan overview: Working Set and Verified Facts accurate and evidence-backed
- [ ] Plan overview: Context & Learnings updated
- [ ] Step file: Quality, Validation, and Test Checklists checked or documented
- [ ] Plan overview: Introduced failures fixed or blocker documented
- [ ] Plan overview: `Last Updated` changed
- [ ] Plan overview: Implementation Log entry added
- [ ] Plan remains `ACTIVE` until global reflection passes

## Orient the User

**After step:** "Step X complete. Checks passed: [list]. Remaining: [steps]."
**Blocked:** "Step X blocked: [reason]. Evidence: [checked]."
**Pausing:** "Progress saved. Continue with [next action]?"

## Next Step

- More PENDING → **execute-step**
- All steps `COMPLETED` with plan `ACTIVE` → **global-reflection**
- BLOCKED → next safe step or report
- Pausing → context dumped, ask user
