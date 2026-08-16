---
name: self-benchmark-runner
description: "Runs the agent against a public benchmark that frontier models have also been scored on (AIME, MATH-500, GSM8K, GPQA, HLE), so the user gets an honest head-to-head of the full skill-stack vs published frontier scores. Only free/public benchmarks with objective answers; grades mechanically, reports evidence, never inflates. Use when the user asks 'compare yourself to Claude', 'run a benchmark', 'test me against Fable', 'how would I do on AIME'. Trigger phrases: 'benchmark', 'run the test', 'compare to Fable', 'AIME', 'MATH-500', 'prove yourself'."
---

# SELF BENCHMARK RUNNER

## DIRECTIVE
An honest benchmark is a prisoner swap: no cherry-picking questions, no
hand-graded leniency, no "it's basically right". Pick a public benchmark with
published frontier scores, solve it WITH the full skill stack, grade
mechanically, and report the score side-by-side with the published number.

## BENCHMARK ELIGIBILITY
Use ONLY where ALL hold:
1. Free to access (public problem text + public answer key — no paywall, no
   gated API).
2. Published scores exist for a frontier model (e.g. Claude Fable 5 / Opus).
3. Objective grading (exact answer / integer / unit tests), not vibes.
4. Sized so the run is completable in one session; if the full set is huge
   (MATH-500, SWE-bench), define a fixed, pre-declared subset upfront — BEFORE
   seeing the answers.

Sorted by fit for this stack: AIME (best: 30 problems, integer keys, AoPS
wiki), GSM8K (easiest tier), MATH-500 (subset), GPQA Diamond (needs web for
facts), HLE (very hard). SWE-bench requires a full harness — report as
"not run" rather than fake it.

## PROTOCOL
1. **Declare BEFORE solving:** benchmark + exact problem list + scoring rule
   (e.g., "AIME I 2025, problems 1–15, ratio correct/15"). Save it first so it
   can't be gamed toward the answer key.
2. **Answer key locked:** download the answer key to a file but DO NOT open it
   until all answers are written. (Honesty gate.)
3. **Solve under the skill stack** — this is the point of the run: apply
   `algorithmic-math-reasoner` gates + `test-time-compute-scaling` to each
   hard problem. No shortcuts.
4. **Grade mechanically:** one exact-string compare per problem; a digit off =
   wrong. Produce a table: problem | my answer | key | score.
5. **Report honestly:** score + per-problem table + which skills were used +
   evidence (any brute-force output). Compare to the published frontier score
   on the SAME set. If a problem was skipped, mark it wrong, don't exclude it.
6. **Don't flatter:** low score = low score. The user asked for the truth.

## ANTI-CHEAT
- Never open the key before answering.
- Never fetch a solution from the source page — fetch problems and answers as
  separate steps, and do the solving reasoning yourself.
- If a problem was likely seen in training (classic), say so and weight the
  comparison accordingly — contamination confounds the score either direction.

## Local adaptation
Problem text: artofproblemsolving.com/wiki (public). Answer keys are also on
the wiki pages (bottom "Answers to 2025 AIME I Problems" list). MATH-500/GSM8K
are on Hugging Face (`openai/gsm8k`, `HuggingFaceH4/MATH-500`) — fetch with
`requests` in venv. Grading is a small `venv/bin/python` script. Record results
in `memory/benchmarks.md` and re-encode memory.