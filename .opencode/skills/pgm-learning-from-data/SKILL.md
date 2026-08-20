---
name: pgm-learning-from-data
description: Applies the learning chapters of Koller & Friedman's Probabilistic Graphical Models to estimate a graphical model from data: maximum likelihood and Bayesian parameter estimation, structure learning, hidden variables and the EM algorithm, and learning in the presence of missing data. Use when the user says 'learn a graphical model', 'parameter estimation', 'structure learning', 'EM for graphical models', 'hidden variables', 'missing data', or when a probabilistic model must be fitted to data. Pairs with: probabilistic-graphical-models, prml-mixture-models-em, bayesian-reasoning-machine-learning, all-of-statistics.
---
# Learning Probabilistic Graphical Models from Data

## When to use
Use when a probabilistic model must be fitted to data, or when the user asks about parameter estimation, structure learning, or EM for graphical models.

## Core mechanics
- Estimate parameters with maximum likelihood or Bayes.
- Learn structure when it is not given.
- Handle hidden variables with the EM algorithm.
- Deal with missing data explicitly.
- Validate the learned model on held-out data.
- Guard against overfitting in structure search.

## Verification
- Verify parameter estimates on data from a known model.
- Check EM converges to the right parameters on a toy problem.
- Compare learned structure against the generating model.
