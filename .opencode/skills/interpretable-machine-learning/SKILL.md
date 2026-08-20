---
name: interpretable-machine-learning
description: Applies Christoph Molnar's Interpretable Machine Learning to explain model predictions with proven methods: interpretable models (linear, tree, rule), model-agnostic tools (SHAP, LIME, permutation importance, partial dependence), and global versus local explanations, with the honest limits of each. Use when the user says 'explain the model', 'SHAP values', 'LIME', 'feature importance', 'partial dependence', 'why did the model predict this', 'model interpretability', 'ML fairness explainability', or when a prediction or model must be justified to stakeholders. Pairs with: model-explanations-shap-lime, machine-learning-design-patterns, data-analysis, designing-machine-learning-systems, evidence-over-memory.
---
# Interpretable Machine Learning

## When to use
Use when a model's decisions must be explained, audited, or justified: local explanations for single predictions and global explanations for the model as a whole, with honest limits.

## Core mechanics
- Prefer inherently interpretable models (linear, decision trees, rule lists) when accuracy allows; they explain themselves.
- For black boxes, use model-agnostic tools: permutation importance and partial dependence for global effects, SHAP and LIME for local explanations.
- Distinguish global (how the model behaves overall) from local (why one prediction) explanation; never conflate them.
- SHAP gives consistent, additive feature attributions; LIME fits a local surrogate model around a prediction.
- State limits: explanations describe the model, not necessarily the true causal mechanism; correlations are not causes.
- Check the explanation against a sanity case before trusting it (an empty or obvious prediction should produce an obvious explanation).

## Verification
- Produce the explanation output (SHAP summary, partial dependence plot) and verify it matches a known property of the training data.
- Confirm feature attributions sum approximately to the prediction (SHAP additivity) as a consistency check.

