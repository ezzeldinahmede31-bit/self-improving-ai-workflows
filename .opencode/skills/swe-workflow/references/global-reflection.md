# Global Reflection

## Contract — Read This First

1. Run when all current execution steps are `COMPLETED` and the plan is still `ACTIVE` — this is the last gate before delivery.
2. Re-read the plan overview, every step file, and every modified/created file.
3. Verify goal achieved, evidence accurate, architecture clean, and no artifacts remain.
4. Verify `plan.md` Steps Overview and step files agree.
5. If any fix requires a file change, create and start a scoped fix step before editing; then verify it and rerun reflection. Critical issue → STOP and flag.
6. Would you hand this to another developer to maintain? If not, record the concrete issue and route it through a fix step.

## Instructions

1. **Re-read the plan overview** (`plans/<YYYY-MM-DD>-<slug>/plan.md`) — verify the plan is `ACTIVE`, all current Steps Overview entries are `COMPLETED`, and the Implementation Log, Working Set, Verified Facts, and Context & Learnings are complete.

2. **Re-read every step file** (`plans/<YYYY-MM-DD>-<slug>/steps/step-N.md`) — verify each has `Status: COMPLETED`, all 10 fields populated, Implementation Notes filled, Files Changed accurate.

3. **Verify plan/step consistency** — confirm every step file status matches the Steps Overview table and all steps are `COMPLETED`.

4. **Re-read ALL modified/created files** with `read` — in the order changes were made.

5. **Evaluate:**

   | Area | Check |
   |------|-------|
   | **Goal** | Achieved? All requirements met? Solution complete? |
   | **Evidence** | Working Set accurate? Verified Facts still true? Files Changed complete? |
   | **Architecture** | Clean design? Could be simpler? Appropriate abstractions? Sensible file organization? |
   | **Code quality** | Technical debt? Error handling sufficient? Edge cases covered? Clear naming? |
   | **Tests** | All passing? Adequate coverage? Edge cases covered? |
   | **Artifacts** | Commented-out code? TODO/FIXME? Debug statements? Hardcoded values? |
   | **Security** | Input validation? Auth checks? Injection risks? |
   | **Performance** | N+1 queries? Unnecessary loops? Memory leaks? |

6. **Route what you find:**

   | Outcome | Action |
   |---------|--------|
   | No file change needed | Record the observation and continue the gate |
   | Any fix requiring a file change | Add a scoped step, mark it `IN_PROGRESS`, implement → verify → persist, then rerun global reflection |
   | Critical security or data-loss risk | STOP, mark/report the blocker, and do not proceed without user direction |

## Mandatory Checklist

- [ ] Re-read entire plan overview (`plan.md`)
- [ ] Re-read every step file (`steps/step-N.md`)
- [ ] Verified plan is `ACTIVE` and Steps Overview matches completed step files
- [ ] Re-read ALL modified/created files
- [ ] Goal achieved with evidence
- [ ] Context & Learnings complete (decisions, gotchas, patterns)
- [ ] Working Set, Verified Facts, Files Changed accurate
- [ ] Architecture clean, no unnecessary complexity
- [ ] No artifacts (debug statements, commented code, stale TODOs)
- [ ] All tests passing
- [ ] Error handling sufficient
- [ ] Comfortable handing to another developer

## After Reflection

If all checks pass:
1. Update the plan overview to `Status: COMPLETED` and update `Last Updated`.
2. Record the successful reflection in the Implementation Log.
3. The task is **DONE**. Do not stage or commit unless the user explicitly requests it.

If an issue needs a file change: keep the plan `ACTIVE`, create an authorized fix step, execute it through verification/persistence, and rerun this reflection.

## This is the End

No more references to load. The workflow is finished.
