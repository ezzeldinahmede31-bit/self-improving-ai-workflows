---
name: single-pass-frontier-emulator
description: "Emulates a frontier model's single-pass open-ended depth on a flash model: instead of greedily splitting a big open-ended task into tiny delegated pieces (which loses the whole-picture coherence a 1M-context model has internally), DELIVER THE ENTIRE ARTIFACT IN ONE COMPLETE RESPONSE with internal draft-versus-attack rounds inside the same generation, then only split if a hard proof/execution gate demands it — and then re-integrate and re-check the whole. Use for any open-ended engineering request: 'build X from scratch', 'design this system', 'write the full module', 'implement this feature end-to-end', 'no splitting, do it yourself', or any task where the user implies 'I want the complete thing in one coherent pass'. Trigger phrases: 'single pass', 'one shot', 'from scratch in one go', 'don't delegate', 'do it all yourself', 'complete build'."
---

# Single-Pass Frontier Emulator

## The gap it closes
A frontier model (Fable-class) answers an open-ended task with ONE internally-coherent
reasoning pass: it holds the whole design, every component, and the integration in one
working memory. A flash model, told to "do a big task", usually fragments the work into
sub-agents and file splits BEFORE thinking — producing disjoint pieces that don't hold
together. This skill forces the flash model to behave like the frontier one: **one
coherent pass with internal attack rounds**, where delegation is the exception, not the
default.

## Protocol (follow in order)

### Gate 0 — Decide: single pass vs split (honest, not lazy)
- **Single pass** if: the deliverable is one artifact/system/feature and you can hold
  its full design in this response (most non-trivial builds DO fit — this is the point).
- **Split ONLY if** a hard gate requires it: a proof must be executed (sandbox), a
  test suite must run, or the artifact exceeds one response's practical limit. Splitting
  is allowed for EXECUTION, never for DESIGN coherence.

### Gate 1 — Whole-picture contract (MANDATORY, before any component)
Write the complete contract first, in ONE block:
1. Goal + success criteria (measurable)
2. Full component/entity inventory (all parts that will exist)
3. Data/control flow between every part (the typing contract)
4. Failure modes + security/reliability edges
5. Verification plan (how we'll know it works)
This contract IS the working memory the frontier model has natively. Everything below
must reference it — no part may contradict the contract.

### Gate 2 — Draft the ENTIRE artifact
Produce the complete deliverable: every file, every function, every schema, in one
response. Do not stop to "ask which part first". Do not stub components as
"TODO". The draft must be FINISHABLE-AS-IS.

### Gate 3 — Internal attack rounds (inside the same pass)
Before delivering, attack your own draft:
1. **Integration check**: does each part's input match the previous part's output shape?
   Trace one end-to-end scenario THROUGH the whole artifact mentally.
2. **Edge case scan**: empty input, zero, duplicates, concurrent access, missing config,
   auth failure, timeouts — list what each component does in each case.
3. **The frontier question**: "What would make a senior reviewer reject this in review?"
   Fix everything you can find NOW (in the same response), not "later".
4. **Self-falsify**: state the one scenario where this design fails, and either fix it or
   say explicitly why it's outside scope (honest boundary, not hand-waving).

### Gate 4 — Deliver one coherent artifact + one verification command
The response ends with:
- The complete artifact (all parts, nothing deferred)
- A single command that proves it (`pytest`, `node --check`, `python -m compileall`,
  `docker build`, a smoke script...)
- The expected output of that command stated in advance

### Gate 5 — Execute the verification (never skip)
Run the command. If it fails, fix IN THE SAME DELIVERY FLOW (remember the contract) and
re-run. Only after green: report `[single-pass] complete — N parts, verification green`.

## Anti-patterns (do not do)
- Do NOT turn a one-artifact task into 7 sub-tasks by default ("subagent-task-delegator"
  style) — that is exactly the flash behavior this skill kills. Delegation happens ONLY
  after Gate 1 says execution needs it.
- Do NOT say "let me first design, then I'll write the code" across separate turns —
  the design AND the code are one pass here.
- Do NOT leave "…" or "rest is obvious" in a deliverable. Frontier models deliver the
  whole thing's skeleton fully realized.

## When the split is genuinely required
If Gate 0/1 forces execution-splitting (tests, sandbox, huge scale):
1. Split only EXECUTION phases, keeping the Gate-1 contract as a checkpoint file on disk.
2. After every execution chunk, re-check the piece against the contract, then re-integrate.
3. End with one full-trace re-verification of the WHOLE artifact (contract → parts → green).

## Pairing
- Carry `proactive-spec-expander` (Gate 1 contract quality) + `frontier-deep-reasoner`
  (Gate 3 reasoning) inside this one — but the DELIVERABLE is the single coherent pass,
  not a pipeline.
- Use `test-time-compute-scaling` only when single-pass reliability is truly exceeded
  (deep uncertainty), not as a habit.