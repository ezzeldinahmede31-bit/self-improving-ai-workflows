---
name: root-cause-post-mortem-analyzer
description: "Performs rigorous root-cause analysis (RCA) on stack traces and runtime errors to prevent superficial band-aid fixes. Use whenever anything fails: a test, a workflow, a crash, or unexpected output. Trigger phrases: 'it fails', 'error:', 'bug', 'why is this broken', stack trace, unexpected behavior."
---

# ROOT CAUSE POST-MORTEM ANALYZER

## DIRECTIVE
When encountering a bug or error, NEVER apply superficial quick fixes (e.g.,
blanket try-catch, arbitrary delay timers, or silencing the exception). You must
identify the root mechanical cause.

## RCA EXECUTION FRAMEWORK
1. **Isolate Stack Trace:** Extract exact error type, file, line number, and
   variable states (run with `--tb=long` / `-x` to get the real trace, not the
   truncated one).
2. **5-Whys Analysis:** Trace back the state mutations that led to the fault.
   Follow the data: where did the bad value enter, how did it propagate?
3. **Identify Root Trigger:** Differentiate between symptom (e.g.,
   `KeyError: 'x'`) and cause (e.g., an upstream API returned a payload without
   `x`, and the code never validated it).
4. **Permanent Structural Fix:** Fix the underlying state leak (validate at the
   boundary, not at the crash point), and add a regression test that reproduces
   the ORIGINAL failing input so the fault can never recur silently.

## Acceptance criteria
- The fix must be explainable in one sentence of cause, not one sentence of
  symptom.
- A regression test accompanies every fix; "it works now" without a test that
  would catch a recurrence is a band-aid.

## Local adaptation
Reproduce with a minimal script: `venv/bin/python -c` / `pytest -x --tb=long`.
Never claim a fix without re-running the original failing case.