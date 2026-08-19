---
name: bayesian-data-analysis
description: Applies Gelman, Carlin, Stern, Dunson, Vehtari and Rubin's Bayesian Data Analysis to perform rigorous Bayesian inference on real data: probability and Bayesian modeling, one- and multi-parameter models, hierarchical models, Bayesian regression, model checking and comparison, and computation via MCMC and variational methods. The standard reference for doing Bayesian statistics properly. Use when the user says 'Bayesian data analysis', 'Gelman', 'hierarchical model', 'posterior predictive check', 'MCMC', 'Bayesian regression', 'Bayesian workflow', or when real data must be modeled with uncertainty quantified. Pairs with: think-bayes, pattern-recognition-machine-learning, information-theory-inference-learning, data-analysis.
---
# Bayesian Data Analysis

Transfers the Gelman workflow: build a model that matches how the data were generated, compute the posterior, check the model against the data, and improve it.

## When to use
- Modeling real data when the answer must include uncertainty and structure.
- Building hierarchical models that share strength across groups.
- Running a rigorous Bayesian workflow (fit, check, improve) on a real problem.

## Core workflow
1. Write a generative model (prior + likelihood) that describes how the data were produced.
2. Compute the posterior with MCMC (Stan-style) or variational methods, checking convergence.
3. Check the model with posterior predictive checks: can simulated data look like the observed data?
4. Compare models and report the posterior and its practical implications.

## Techniques
- Hierarchical/multilevel models for grouped data, with shrinkage toward a common prior.
- Bayesian regression with uncertainty in coefficients and predictions.
- Model checking and comparison (loo, WAIC) as honest evaluation of fit and predictive quality.

## Verification discipline
- Check MCMC convergence (multiple chains, R-hat) before trusting draws.
- Report posterior intervals and their sensitivity to the prior.
- A posterior predictive check that fails means the model is wrong, not the data.

## Pairs with
think-bayes, pattern-recognition-machine-learning, information-theory-inference-learning, data-analysis.
