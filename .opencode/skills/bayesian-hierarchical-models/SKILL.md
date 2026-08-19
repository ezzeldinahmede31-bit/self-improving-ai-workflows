---
name: bayesian-hierarchical-models
description: Applies the hierarchical-model chapters of Gelman et al.'s Bayesian Data Analysis: multilevel models that share strength across groups, partial pooling, group-level and individual-level parameters, and the shrinkage that improves estimates for small groups. Use when the user says 'hierarchical model', 'multilevel model', 'partial pooling', 'random effects', 'grouped data', 'shrinkage', 'small groups', or when data is grouped and each group has few observations that should borrow strength from the others. Pairs with: bayesian-data-analysis, think-bayes, data-analysis, pattern-recognition-machine-learning.
---
# Hierarchical Models (BDA)

Transfers the Gelman treatment of hierarchical models: model the groups as drawn from a common distribution, let each group's estimate shrink toward the overall structure, and quantify the uncertainty correctly.

## When to use
- Data is grouped (sites, users, regions) and groups have few observations.
- You need group-level estimates that borrow strength rather than ignoring structure or pooling everything.
- Quantifying between-group variation and its uncertainty.

## Core framework
1. Model each group's parameters as drawn from a common (hyper)prior distribution — the hierarchy that shares information.
2. Estimates are partially pooled: shrunk from the raw group estimate toward the overall mean, with the shrink depending on group sample size and between-group variance.
3. Posterior inference handles both the group-level parameters and the hyperparameters, propagating all uncertainty.

## Practice rules
- Hierarchical models fix the overconfidence of separate fits and the bias of full pooling.
- Check that the between-group variance is estimated, not assumed.
- For many groups with little data each, this is often the only honest model.

## Verification discipline
- Compare hierarchical estimates to no-pooling and full-pooling baselines.
- Check the posterior of the hyperparameters for identifiability.
- Run posterior predictive checks to confirm the model reproduces observed structure.

## Pairs with
bayesian-data-analysis, think-bayes, data-analysis, pattern-recognition-machine-learning.
