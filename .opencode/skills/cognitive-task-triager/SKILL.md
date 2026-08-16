---
name: cognitive-task-triager
description: "Analyzes task complexity and assigns execution to the optimal LLM tier (Routine, Code, Long-Context, Critical Reasoning) before any model call. Prevents wasting high-cost tokens on trivial tasks and NEVER sends complex reasoning to a weak 13B-active-parameter model. Use when deciding which model should execute a task, when a prompt mixes easy and hard sub-tasks, when context is huge, or when ambiguous requirements must be surfaced. Trigger phrases: 'which model should handle this', 'route this to a smarter model', 'task complexity', 'cognitive triage', 'cheap vs expensive model'."
---

# COGNITIVE TASK TRIAGER SKILL

## DIRECTIVE

Analyze prompt intent, depth, and domain BEFORE model assignment. Do NOT waste
high-cost tokens on simple tasks, and NEVER send complex reasoning tasks to
13B-active-parameter models. Model choice is decided by measured complexity,
not by habit.

## TRIAGING DECISION MATRIX

| Complexity | Task Category | Target Tier | Primary Reason |
| :--- | :--- | :--- | :--- |
| **1-3** | JSON parsing, Regex, Basic routing, Summarization | **Tier 1 (V4-Flash / Free)** | Low risk, deterministic structure |
| **4-6** | Standard code gen, Refactoring, SQL queries | **Tier 2 (V4-Pro / Qwen 2.5 Coder)** | High SWE-bench (~80.6%), cost-effective |
| **7-8** | Multi-file refactoring, Long docs (>100k tokens) | **Tier 2+ (Kimi K3 / GLM-5.2)** | Long-context retention & structural understanding |
| **9-10** | Architecture trade-offs, Edge cases, Red-teaming | **Tier 3 (Claude Opus 4.8 / Frontier)** | Requires max intelligence (≥60 AA/Intelligence Index) |

## EVALUATION ALGORITHM

Score each task 1..10 against these triggers:

1. `Is_Edge_Case`: Does the problem lack standard StackOverflow/Docs
   solutions? -> Escalates to Tier 3. No foothold in training data means the
   weak model has nothing to recall.
2. `Token_Depth`: Is context > 100k tokens? -> Assign to Kimi K3 /
   high-context model. Long-context *retention* — not raw window size — is
   what matters.
3. `Ambiguity_Level`: Are requirements contradictory or undefined? -> Force
   Tier 3 clarification. Doubt must surface, never be guessed by a weak model.

Composite rule: `score = base_intent(0-4) + min(3, edge_case*3) + min(3, depth_drift)`
then floor the assignment by the highest-scoring sub-signal. A task is NEVER
downgraded below the tier of its hardest sub-task.

## HARD RULES

- JSON/Regex/shape work on clean, well-scoped inputs -> Tier 1 only.
- Any security, adversarial, or edge-case reasoning -> Tier 3, no exceptions.
- Split mixed tasks: cheap parsing components go to Tier 1, the reasoning core
  goes to its own tier. Do not send a 9/10 reasoner wrapped in a 2/10 formatter.

## INTEGRATION

Feeds the routing decision into `litellm-tier-router` (which provider answers)
and `cascade_routing.CascadeRouter` (confidence-based tiering). The triager is
the COST side; cascade confidence is the CORRECTNESS side.