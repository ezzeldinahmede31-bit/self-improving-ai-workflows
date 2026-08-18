---
name: architecture-tradeoff-analysis
description: Applies the trade-off analysis method of Software Architecture: The Hard Parts (Ford, Richards, Sadalage) to decisions with no perfect answer: name the candidate approaches, enumerate the dimensions that matter (coupling, cohesion, consistency, cost, operability), score each candidate honestly, and choose with a documented rationale instead of a gut feeling. Use when the user says 'trade-off analysis', 'which architecture should I choose', 'compare the options', 'architecture decision record', 'weight the options', 'coupling versus cohesion', 'quantify the trade-off', 'decision matrix', 'the hard parts', or when an architecture choice needs a defensible, documented verdict. Pairs with: software-architecture-hard-parts, agent-arch-system-design, tradeoff-and-postmortem-documenter, evolutionary-architecture.
---

# Architecture Trade-off Analysis

Transfers the trade-off analysis method of Software Architecture: The Hard Parts (Ford, Richards, Sadalage) to architecture decisions that have no perfect answer.

## When to use
- An architecture choice has no obvious winner and reasonable people disagree.
- The user asks to compare options, weight criteria, or document an architecture decision.
- A decision must be defensible in review, not just familiar or fashionable.

## Name the candidate approaches
- Write every real candidate, including the boring one (keep the monolith, keep the current design).
- Do not design the answer before the options are listed; the list is the evidence set.
- Drop only candidates that clearly cannot meet a hard constraint; keep the rest for scoring.

## Enumerate the dimensions that matter
- Coupling: how much change in one part forces change in another.
- Cohesion: whether each part holds together around one responsibility.
- Consistency: the consistency model the option can actually deliver (strong, eventual, or none needed).
- Cost: build, run, and operate cost, including the team's ability to maintain the choice.
- Operability: deployment, monitoring, debugging, and recovery burden.
- Add only dimensions the decision actually touches; a generic checklist adds noise.

## Score each candidate honestly
- Score each candidate per dimension on the same scale, with the same definition of the top score.
- Distinguish must-have constraints from nice-to-have preferences; a candidate failing a must-have is out regardless of total.
- Score from evidence (measure or prototype) where the dimension is load-bearing; do not guess a number.
- Record who made the choice and what evidence the score rests on, so the score is challengeable.

## Choose with a documented rationale
- Present the matrix, the must-haves, and the winner with the reasons in plain language.
- Name what the winner gives up; every real choice sacrifices something, and the sacrifice must be explicit.
- Write the verdict as a short architecture decision record that future reviewers can reopen when the evidence changes.
- If two candidates tie, choose the one that is easier to reverse; revisit the decision when the tie-breaker changes.

## Verification discipline
- Confirm every candidate was scored on the same dimensions with the same scale.
- Check that no must-have constraint is violated by the chosen option.
- Record the decision, the reasons, the sacrificed dimension, and the evidence in the decision record.

## Pairs with
software-architecture-hard-parts, agent-arch-system-design, tradeoff-and-postmortem-documenter, evolutionary-architecture.