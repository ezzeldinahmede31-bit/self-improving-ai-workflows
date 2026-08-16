# Verify Step

## Contract — Read This First

1. Run all three passes — Validate, Test, Review Diff — before marking any step COMPLETED.
2. Re-read every modified file with `read`. Do not trust memory.
3. Run discovered commands from the plan; do not replace them with guessed generic commands unless no repo-specific command exists.
4. Tests must cover happy path, edge cases, and error paths. All must pass.
5. Review the actual `git diff` — no artifacts, no scope creep, no unverified imports.
6. Every changed file must be in the step's Files Changed; every fact in Verified Facts must have tool evidence.
7. Evidence gaps block completion: missing target read, missing impact search for shared behavior, guessed repo facts, or missing validation/skipped reason must be fixed or documented as `BLOCKED`.
8. If any pass fails: fix, re-run. Do not defer. Do not mark COMPLETED with known failures.

## When to Use

After finishing implementation in `execute-step`, before `persist-plan`.

## Pass 1 — Validate

1. **Re-read every modified file** with `read`. Not from memory.
2. **Run discovered commands from the plan:** use the Validation Commands table populated via [`command-discovery.md`](command-discovery.md). Do not replace repo-specific commands with guessed generic commands unless no repo-specific command exists.
3. **Run pre-commit hooks** when configured. If hooks can't run, document why.
4. **Verify evidence:** every changed file in Files Changed, every fact in Working Set/Verified Facts backed by read/search/tool output.
5. **Verify anti-shortcut evidence:** target files re-read; impact search recorded when behavior/contracts are shared; validation commands run or skipped with reason and risk.

**Checklist:** re-read ✓ | parses ✓ | lint ✓ | format ✓ | hooks ✓ | matches plan ✓ | only in-scope files ✓ | evidence accurate ✓

## Pass 2 — Test

1. **Define expected behavior** — inputs, outputs, failure modes.
2. **Write tests** — happy path, edge cases, error cases.
3. **Run tests** — all must pass.
4. **No test framework?** Document manual verification.
5. **Add test files to Working Set.**

**Checklist:** happy path ✓ | edge cases ✓ | error paths ✓ | all pass ✓ | test files in Working Set ✓

## Pass 3 — Review Diff

1. **View the actual diff:** `git diff` / `git diff --staged`
2. **Scan for issues:**

   | Category | Look for |
   |---|---|
   | Artifacts | `console.log`, commented-out code, stray TODO/FIXME, unused imports |
   | Scope creep | Formatting changes to unrelated files, "while I'm here" refactors |
   | Evidence gaps | Unverified imports, packages, APIs, paths, skipped impact search |
   | Quality | Magic numbers, poor names, deep nesting (>3), long functions (>30 lines) |
   | Duplication | Copy-pasted blocks, similar logic in multiple places |
   | Missing handling | No error handling on fallible ops, missing null/empty checks |
   | Contracts | Changed public API/schema/route without caller updates |
   | Security/data/performance | Leaked secrets, missing auth, injection risk, N+1, unsafe migration |
   | Project fit | New pattern when existing pattern exists, inconsistent style |

3. **Scope audit:** every changed file explainable by the step's Plan. Unexplained → dependency (document) or scope creep (revert).
4. **Quality standard:** apply [`references/code-quality.md`](code-quality.md) and fix violations now.

**Checklist:** diff reviewed ✓ | no artifacts ✓ | only planned files ✓ | no duplication ✓ | error handling ✓ | contract compatible ✓ | security/data/performance reviewed ✓ | project fit ✓

## Definition of Done

Before marking COMPLETED, all of the following must be true:

**Scope:** diff contains only changes required by the task. No unrelated refactors, formatting churn, or dependency changes unless explicitly required.

**Correctness:** implementation satisfies success criteria; existing behavior preserved unless explicitly changed; edge/failure cases handled consistently with nearby code.

**Project fit:** change follows local naming, layering, error handling, logging, testing conventions; existing helpers/types reused; new abstractions justified by current use.

**Validation record:**

| Check | Command | Result | Notes |
|---|---|---|---|
| Typecheck |  |  |  |
| Lint |  |  |  |
| Test |  |  |  |
| Build |  |  |  |

If a command is skipped, record why. For noisy output use compact evidence: `Command`, `Exit`, `Output` (path or inline), `Summary`, `Freshness`.

**Anti-hallucination gate:**
- Target read: modified files re-read after changes ✓
- Impact search: callers/usages searched when shared behavior changed (or `N/A — isolated`) ✓
- No guessed facts: unverified claims labeled `Assumption`/`Unknown`, not `Verified` ✓
- Validation: checks run with evidence, or skipped with reason and residual risk ✓

**Final response shape:**
```markdown
Summary: [What changed]
Verified: [Key files/commands checked]
Validation: [Command/result, or skipped with reason]
Risks/Unknowns: [Residual risk, or `None known`]
```

## If Any Pass Fails

1. Fix immediately — do not defer.
2. Re-run the failing pass.
3. Pre-existing unrelated failure? Document evidence, run narrowest passing check.
4. Significant extra work? Update plan (see execute-step → Scope Changes).

## Next Step

→ **persist-plan** (mark COMPLETED, update plan and context)
