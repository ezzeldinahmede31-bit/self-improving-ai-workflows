---
name: gaussian-processes-machine-learning
description: Applies Rasmussen & Williams' Gaussian Processes for Machine Learning to build probabilistic regression and classification with GPs: covariance functions, exact and approximate inference, hyperparameter learning, and the uncertainty that makes GPs trustworthy. Use when the user says 'Gaussian process', 'Rasmussen Williams', 'covariance function', 'GP regression', 'kernel hyperparameters', 'predictive uncertainty', or when a model must give calibrated uncertainty on small data. Pairs with: prml-kernels-gaussian-processes, machine-learning-probabilistic-perspective, probabilistic-graphical-models, bayesian-reasoning-machine-learning.
---
# Gaussian Processes for Machine Learning

## When to use
Use when a model must give calibrated uncertainty on small data, or when the user asks about Gaussian process regression, covariance functions, or GP hyperparameters.

## Core mechanics
- Define the prior over functions with a mean and covariance.
- Choose a covariance function that matches the data.
- Do exact regression when the dataset is small.
- Learn hyperparameters by maximizing the marginal likelihood.
- Approximate when exact inference is infeasible.
- Report predictive uncertainty with the posterior.

## Verification
- Verify the posterior on a toy regression problem.
- Check that predictive intervals cover the held-out data at the claimed rate.
- Test hyperparameter learning recovers known values.
