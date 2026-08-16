---
name: ambiguity-resolver
description: "Forced-explicit ambiguity gate for weak/free models. Before ANY execution step, produce a mandatory JSON contract with ambiguity_score, assumptions_made, missing_info, clarifying_question. If ambiguity_score > 0.4, BLOCK execution and route the clarifying question to HITL (or a frontier model) instead of guessing. Use whenever a task is underspecified, vague, placeholder-laden, or when the generator model is small and cannot be trusted to self-stop. Paired with: context-enrichment, chain-integrity-checker, confidence-calibrator."
---

# AMBIGUITY RESOLVER PROTOCOL

## DIRECTIVE

A small model does not fail because it "doesn't notice" ambiguity — it fails
because it is not wired to stop. This skill FORCES the model to turn an
implicit decision ("do I understand enough?") into an explicit, machine-checkable
classification BEFORE any execution.

## MANDATORY CONTRACT

Before executing any step, emit ONLY this JSON:

```json
{
  "ambiguity_score": 0.0,
  "assumptions_made": ["..."],
  "missing_info": ["..."],
  "clarifying_question": "..." | null
}
```

## ESCALATION RULES (hard)

- `ambiguity_score > 0.4` → **CLARIFY**. Do NOT execute. Send the
  `clarifying_question` to HITL (default-deny on timeout) or to a frontier
  model. Never continue with a guessed interpretation.
- `0.15 <= ambiguity_score <= 0.4` → **ESCALATE**. Route to a frontier model
  if available; otherwise proceed cheaply but flag `missing_info` for the
  generator prompt.
- `ambiguity_score < 0.15` → **PASSTHROUGH**. Proceed, but carry
  `assumptions_made` into the generator prompt so they stay auditable.

## DETERMINISTIC FLOOR (never trust the model alone)

The structural heuristic below caps the minimum ambiguity score and can never
be reduced by the contract:

- vague terms: `etc`, `handle it`, `make it nice`, `do your best`, `عادي`, `كده`
- unresolved placeholders: `XXX`, `<...>`, `TBD`, `[]`
- required signals absent from the artifact: `token`, `url`, `path`,
  `chat_id`, `webhook path`, `endpoint`, `api_key`, `credentials`, `channel`
- instructions shorter than 6 words

`ambiguity_score = max(model_score, structural_floor)`.

## PROTOCOL FLOW

1. Mild prompting to classify, never to "do your best with what you have".
2. Merge model JSON with the structural floor.
3. Penalize (do not reward) the absence of a `clarifying_question`: no question
   AND missing_info non-empty means the model is silent-doubting → raise weight.
4. Route per escalation rules above.

## INTEGRATION

This is the FIRST of the four hardening skills:

```
ambiguity-resolver (stops if unclear)
  → context-enrichment (inject known implicit context)
  → execution WITH chain-integrity-checker (verify each step)
  → confidence-calibrator (decide real escalation, not self-report)
```