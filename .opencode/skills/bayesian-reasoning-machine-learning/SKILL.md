---
name: bayesian-reasoning-machine-learning
description: Applies David Barber's Bayesian Reasoning and Machine Learning to build probabilistic models and reason with them: graphical models, belief propagation, sampling methods, and the Bayesian treatment of regression, classification, and latent variable models. Use when the user says 'Bayesian reasoning', 'Barber', 'belief propagation', 'probabilistic model', 'sampling', 'Bayesian regression', 'latent variable', or when a model must carry and propagate uncertainty. Pairs with: probabilistic-graphical-models, machine-learning-probabilistic-perspective, think-bayes, formal-math-logic-verification-engine.
---
# Bayesian Reasoning and Machine Learning

## When to use
Use when a model must carry and propagate uncertainty, or when the user asks about Bayesian inference, belief propagation, or probabilistic models.

## Core mechanics
- Define a prior and a likelihood for the problem.
- Compute or approximate the posterior.
- Use graphical models to structure the computation.
- Apply belief propagation for tree-structured models.
- Use sampling when exact inference is intractable.
- Report predictive distributions, not point estimates alone.

## Verification
- Compare the posterior against a grid or exact computation on a toy problem.
- Verify that the predictive distribution covers the held-out data.
- Test sensitivity to the prior.
