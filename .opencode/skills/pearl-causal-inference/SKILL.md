---
name: pearl-causal-inference
description: "Reasons from correlation to causation: graphs, interventions, and counterfactuals. Use when the user says 'causal inference', 'confounding', 'do-calculus', 'DAG', 'instrumental variable', 'propensity score', 'counterfactual', 'Pearl', 'causal effect', or when a decision needs what WILL happen, not what correlates."
---

# Pearl Causal Inference

Distilled from Pearl (*Causality*, *Book of Why*) and Peters/Janzing/
Schölkopf (*Elements of Causal Inference*): correlation answers "what is",
intervention answers "what if I act", counterfactuals answer "what if I had".
Each rung needs strictly stronger assumptions — climb deliberately.

## Purpose

Estimate the effect of ACTIONS from data (observational or experimental),
stating the exact assumptions that license the causal claim.

## The ladder (never skip rungs silently)

1. **Draw the DAG.** Nodes = variables, arrows = direct causal influence
   (domain knowledge first, discovery algorithms second). The graph encodes
   every independence the analysis will use — a missing arrow is a strong
   claim, a present one is cheap.
2. **Close the backdoors.** Identify confounders (common causes of treatment
   and outcome); adjust for a set satisfying the backdoor criterion. NEVER
   adjust for colliders (common effects) or mediators on the path of
   interest — conditioning on them OPENS bias instead of closing it.
3. **Estimate with the right tool.** Randomized trials (gold standard, when
   ethical/feasible); matching/weighting on observables (propensity scores
   with overlap checks); instrumental variables (relevance + exclusion
   defended, not assumed); difference-in-differences (parallel trends
   argued); regression discontinuity (no manipulation at the cutoff).
4. **Do-calculus for the hard cases.** When adjustment is impossible, derive
   identifiability mechanically (front-door, napkin graphs). If the effect is
   non-identifiable from the graph + data, say so — no estimator rescues it.
5. **Counterfactuals for individuals.** Abduction (infer background from what
   happened) -> action (apply the intervention) -> prediction (compute the
   alternate world). Unit-level claims need functional (structural) models,
   not just graphs.

## Assumption hygiene (the whole game)

- Every causal number ships with its identifying assumptions listed FIRST.
- Sensitivity analysis: how strong would unmeasured confounding need to be
  to overturn the conclusion? Report the breakpoint, not just the point.
- Transportability: the effect licensed HERE travels THERE only under
  stated invariance — populations, times, and regimes differ.

## Verification

Deliverable: DAG, estimand in do-notation, identification argument, estimator
+ diagnostics (overlap, balance, placebo tests), sensitivity breakpoint. Any
missing piece demotes the claim one rung.

## Pairs with

- `think-stats`/`data-analysis` (statistical machinery),
  `experiment-code` (trials and A/B), `thinking-second-order` (downstream
  effects), `data-mining-concepts-techniques` (observational data).
