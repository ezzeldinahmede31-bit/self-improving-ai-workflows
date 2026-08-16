---
name: frontier-deep-reasoner
description: "Compensate for shallow/degraded multi-step reasoning by forcing an explicit decomposition ladder (Problem -> Constraints -> Steps -> Verify -> Output). Use before answering any non-trivial question, debugging session, design decision, or algorithm implementation, especially when the task has >2 interacting constraints. Trigger phrases: 'solve this', 'why does', 'design', 'optimize', any bug hunt, or any task where a wrong first guess would be expensive."
---

# Frontier Deep Reasoner

A flash-tier model degrades toward *plausible-but-shallow* answers on complex
tasks. This skill forces the reasoning discipline of a frontier model: break
the problem into verifiable pieces and prove each one before outputting.

## Protocol (mandatory for non-trivial tasks)

1. **Restate the problem** in one line. If you cannot, ask the user to clarify
   BEFORE guessing — a wrong target wastes the whole chain.
2. **List explicit constraints** (inputs, edge cases, what "done" means, what is
   OUT of scope). Write them out; do not carry them silently in your head.
3. **Decompose**: split into 2-5 independent pieces. For each piece state a
   testable claim: *"if I do X, then Y must hold."*
4. **Execute piece by piece** — never merge two pieces into one jump.
5. **Verify each claim**: run the code / check the file / compute the example by
   hand IN YOUR REPLY (show the arithmetic or the actual output). A claim that
   you cannot prove stays open.
6. **Only then summarize.** If you find an inconsistency, go back to step 3 —
   do not paper over it.

## The anti-shallow checklist (ask before replying)
- Did I address the *actual* question or what I assumed the question was?
- Is there an edge case (empty input, nil, 0, huge number, race, permission) I skipped?
- Am I stating a "fact" — and did I verify it with a tool or the repo, or did I recall it?
- Would my answer survive a hostile reviewer who knows the subject?

## Worked contract (use for long chains)
Write a tiny plan line like `[1/5] parse -> [2/5] validate -> [3/5] transform -> [4/5] verify -> [5/5] report` and physically advance it in your replies so the reasoning is auditable.