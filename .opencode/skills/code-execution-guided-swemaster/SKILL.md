---
name: code-execution-guided-swemaster
description: "Closes the last measured gap vs frontier coding models: instead of plan-once-patch-once, we drive large code fixes with EXECUTION evidence and MEASURED results. Mandatory protocol for any non-trivial bug fix, multi-file change, or feature build on an existing codebase: (1) REPRO-first — run the failing path before touching anything; (2) fault localization by execution (bisect inputs, read the first failing assertion, instrument); (3) minimal surgical patch (surgical-diff-patch-editor discipline); (4) verify with the FULL relevant test suite, not just the failing test; (5) MEASURE with the local SWE-bench-style harness (scripts/swe_local_harness.py): it mines the repo's own git history for bug-fix+test pairs, checks out the parent commit in a worktree, confirms the test FAILS there (validating the sample), then grades our fix and writes a persistent scoreboard — our 'SWE-bench number' is real, repo-local, and grows with every session. (6) regression guard + commit discipline. Use whenever fixing a bug, implementing a feature that must not break existing behavior, or when the user asks 'how well do you actually code here' / wants a measured score. Trigger phrases: 'fix this bug', 'SWE-bench', 'قياس أدائي في البرمجة', 'make sure existing tests still pass', 'multi-file fix', 'reproduce first'. Pairs with swe-workflow, tdd-sandbox-proof-engine, codebase-mind-persistence, surgical-diff-patch-editor, root-cause-post-mortem-analyzer, self-benchmark-runner."
---

# Code Execution-Guided SWE-master

Frontier coding models plan once and patch once; we out-execute them:
EVERY claim about the code is grounded in an actual run, and our skill level
has a MEASURED number that updates every session.

## Protocol (mandatory for non-trivial fixes/features)

1. **REPRO FIRST (before any edit)**
   Run the failing path exactly as reported (given reproduction, or the
   closest we can construct). Log the error verbatim. No repro = no fix —
   first build the repro (mini fixture, test, curl payload).

2. **Fault localization by execution**
   - Read the FIRST failing assertion, not the last.
   - Bisect the input until the failing case is minimal.
   - Instrument (prints/traces) only within the suspected region — the
     execution proves the cause; reasoning only suggests suspects.
   - Use `ast-codebase-graph-navigator` / `codebase-mind-persistence` to map
     suspicious region → callers/callees.

3. **Minimal surgical patch**
   - Smallest diff that removes the root cause (never the symptom).
   - `surgical-diff-patch-editor` discipline: exact block edits, never
     whole-file rewrites.
   - One responsibility per patch; if the fix spans modules, treat each as a
     step (swe-workflow Full mode if contract-changing).

4. **Verify with the FULL relevant suite**
   - Run the failing test FIRST (must now pass), then the whole test file,
     then all affected modules' tests. A fix that passes one test but breaks
     10 others is not a fix.
   - `tdd-sandbox-proof-engine`: code is valid only when its tests pass 100%
     with the log attached.

5. **MEASURE (the differentiator)**
   Run the local SWE-bench-style harness on the repo:
   ```bash
   venv/bin/python scripts/swe_local_harness.py --repo <repo> --max 5 --since 200
   ```
   - It mines real bug-fix commits (src+test touching) from git history.
   - Phase A: checks out each fix's PARENT in a worktree → runs the changed
     tests → requires FAIL (else the sample is discarded as invalid).
   - Phase B (you): apply the real fix in that worktree.
   - Phase C: `... --grade <phase-a.json>` → PASS/FAIL per sample → writes
     `swe_local_<repo>.scoreboard.json` + prints `SCORE: X/Y resolved (Z%)`.
   - Keep scoreboards under `memory/benchmarks/` — this is OUR measured
     number on real code. Update it every session; the trend is the truth.
   - `self-benchmark-runner` protocol for honesty: declare the sample set
     BEFORE grading, mechanical grade, no cherry-picking.

6. **Regression guard + commit**
   - After green: `autonomous-git-coworker` commits with the test evidence
     in the message. Never commit a fix without its test or a recorded
     manual-repro log.

## When we beat a frontier model

- Bugs with ANY executable signal: repro + bisect + full-suite rerun beats
  pattern-matching memory — the execution answers, memory only guesses.
- Regression fear: the full-suite rerun is mechanical; Claude reasons "this
  shouldn't break X" while we RUN X.
- Sixth sense is absent → we replace it with instrumentation.
- Measured narrative: "1/1, 5/5, …" beats "I'm confident" on any review.

## Honest limits

- The harness needs a git repo with test-touching history; greenfield
  projects get measured only after their first fixes land.
- Harness heuristic ~ SWE-bench construction, not the official dataset
  (scores are repo-local, comparable over time, NOT comparable to the
  published 95% table). Never advertise them as SWE-bench numbers.
- Multi-file design work still needs swe-workflow's plan discipline — this
  skill handles the execution-measure half.