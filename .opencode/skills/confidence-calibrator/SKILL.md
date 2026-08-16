---
name: confidence-calibrator
description: "Externally-measured confidence calibration for weak/free models. The model has NO true self-knowledge: its claimed confidence is a linguistic guess. The only honest calibration is a feedback loop — log every (stated_confidence, task_category) at decision time, record the real HITL/verifier outcome, then derive per-category accuracy and an ADAPTIVE escalation threshold. Use when the system should stop trusting a low-quality model's 'I am 0.8 sure' and instead trust the measured historical acceptance rate. Feeds EscalationGate and cascade routing."
---

# CONFIDENCE CALIBRATOR PROTOCOL

## DIRECTIVE

Never trust the model's spoken confidence. It has no real introspection — any
"confidence: 0.8" is a linguistic guess, not a measurement. Calibration must be
TRUE measurement: compare what the model claimed against what actually happened
(human approval/rejection, verifier pass/fail), per task category, over time.

## FEEDBACK LOOP (the core of the whole system)

### Write path — fed from HITL decisions

1. At routing time, log: `log_prediction(category, stated_confidence)` → keep
   the prediction_id.
2. When HITL (or the verifier) reaches a terminal verdict, record the real
   outcome: `record_outcome(prediction_id, accepted=True|False)`.

### Read path — adaptive escalation

- `effective_confidence = stated_confidence * historical_accuracy(category)`
  (no history ⇒ effective == stated; no penalty, no free pass).
- `get_adjusted_threshold(category, base)` — when a category's real acceptance
  rate is low (the model is overconfident there), the threshold is RAISED so
  the cascade escalates to frontier/HITL EARLIER in that category.

## LOGIC EXAMPLE

Model claims `confidence: 0.8` in category `webhook-build`. History: 9
predictions, 3 accepted (accuracy 0.33). Then:

- `effective_confidence = 0.8 * 0.33 ≈ 0.26` → below any sane base → escalate.
- `adjusted_threshold` rises from `0.5` toward `0.5 + 0.5*0.67 ≈ 0.84`.

The system STOPS trusting the 0.8 and acts on the measured 0.26.

## SUMMARY METRICS

Per category, expose: resolved predictions, accepted count, accuracy, adjusted
threshold. This is a real feedback loop — the item that the original design
reviews as the most important missing capability. There is no prompt trick here,
only measurement.

## INTEGRATION

`hitl_gate.py` records every decision → `confidence_calibrator.record_outcome`.
The orchestrator uses `get_adjusted_threshold` instead of a fixed 0.5 threshold
in its EscalationGate. Runs last in the pipeline:

```
ambiguity-resolver → context-enrichment → chain-integrity-checker
→ confidence-calibrator (decides real escalation)
```