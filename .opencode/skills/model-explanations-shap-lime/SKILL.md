---
name: model-explanations-shap-lime
description: Deep dive into the two workhorse model-agnostic explanation methods from Interpretable Machine Learning: SHAP (Shapley values, additive attributions, summary/dependence plots) and LIME (local surrogate models), with when to use each and how to validate an explanation. Use when the user says 'SHAP values', 'SHAP summary plot', 'LIME', 'explain this prediction', 'feature attribution', 'local explanation', 'why did the model predict', or when a model or prediction needs a concrete, verified explanation. Pairs with: interpretable-machine-learning, data-analysis, machine-learning-design-patterns, evidence-over-memory.
---
# SHAP and LIME Explanations

## When to use
Use when a model or a single prediction must be explained with a concrete, quantitative attribution: SHAP for additive global and local values, LIME for local surrogate explanations.

## Core mechanics
- SHAP computes Shapley values: each feature's fair contribution to the prediction, summing to the prediction (additivity).
- SHAP tools: summary plot for global feature impact, dependence plots for feature interactions, and force plots for single predictions.
- LIME fits a simple interpretable model locally around one prediction; the local surrogate reveals which inputs drove it.
- SHAP is consistent and additive; LIME is flexible but sensitive to the neighborhood definition.
- Explain both ways and cross-check: a feature that SHAP ranks top should also appear in the LIME surrogate.
- State the limit: explanations describe the model, not true causality.

## Verification
- Verify SHAP additivity: the attributions sum to the prediction minus the base value.
- Sanity-check an explanation on an obvious example (e.g., a prediction driven by one dominant feature).

