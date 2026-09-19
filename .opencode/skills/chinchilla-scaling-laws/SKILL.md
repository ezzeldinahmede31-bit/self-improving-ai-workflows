---
name: chinchilla-scaling-laws
description: "Plans large-model training with scaling laws: compute-optimal size, data mix, and emergent behavior. Use when the user says 'scaling laws', 'Chinchilla', 'compute-optimal', 'how big a model', 'training FLOPs', 'data scaling', 'emergent abilities', 'Kaplan', 'Hoffmann', or when training compute must be spent where it buys loss."
---

# Chinchilla Scaling Laws

Distilled from Kaplan et al. (2020) and Hoffmann et al. *Chinchilla* (2022):
test loss follows smooth power laws in parameters, data, and compute — so
training budgets are an allocation problem with a computable answer, not a
vibes problem.

## Purpose

Spend a fixed FLOP budget where it minimizes loss: the right model size, the
right token volume, and honest expectations about what scale buys.

## The laws (and what to do with them)

1. **Power-law loss.** L(N,D) ≈ A/N^α + B/D^β + E: loss falls predictably
   with parameters N and data D. Fit the exponents on SMALL runs, extrapolate
   to large — never guess the large run directly.
2. **Compute-optimal allocation (Chinchilla).** For fixed FLOPs C ≈ 6ND:
   scale N and D TOGETHER (~equal proportions). The classic failure is
   oversized models starved of tokens — Chinchilla showed a 70B model on 1.4T
   tokens beating a 280B model on 300B. When in doubt, train smaller on more.
3. **Data quality is a multiplier.** Laws assume fixed data distribution;
   better data shifts the whole curve (dedupe, filter, mix domains
   deliberately). Token crisis planning: repeated data yields diminishing
   returns after ~4 epochs — budget unique tokens first.
4. **Emergence is thresholded, not magic.** Some capabilities appear
   discontinuously with scale — plan evals across scales, never certify a
   capability from one model size. U-shaped/inverse scaling exists: bigger
   can get WORSE on specific tasks; measure, don't assume monotonicity.
5. **Inference enters the budget.** Training-optimal ≠ deployment-optimal:
   total cost = train + (per-token × lifetime volume). Small-long-trained
   models (Llama-style) often win lifetime economics; distill/quantize after.

## Planning protocol

- State C (FLOPs), derive (N,D) from the fitted law, add 20% headroom for
  the unexpected, instrument loss-vs-prediction from step one.
- Mid-training divergence from the predicted curve is information: data
  issue, bug, or wrong exponents — investigate, don't ignore.

## Verification

Training plan ships with: fitted exponents + source runs, (N,D,C) triple
with the allocation math shown, data-mix rationale, evals at ≥2 scales, and
the inference-cost model. "Bigger model" without the triple is rejected.

## Pairs with

- `llm-deployment-optimization` (inference economics),
  `efficient-dl-quantization-pruning` (post-train efficiency),
  `distributed-training-foundation-models-v2` (spending the FLOPs),
  `evaluation` (capability measurement across scales).
