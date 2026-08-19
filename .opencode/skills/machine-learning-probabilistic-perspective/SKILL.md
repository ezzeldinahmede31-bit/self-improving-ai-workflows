---
name: machine-learning-probabilistic-perspective
description: Applies Kevin Murphy's Machine Learning: A Probabilistic Perspective to view all of machine learning through probability: Bayesian inference and conjugate priors, graphical models (Bayesian networks, Markov random fields), generative vs discriminative models, Monte Carlo sampling and MCMC, approximate inference (variational), and the probabilistic treatment of classification, regression, and unsupervised learning. Use when the user says 'probabilistic machine learning', 'Bayesian inference', 'conjugate prior', 'MCMC', 'graphical model', 'generative model', 'Murphy', 'uncertainty quantification', or when a model must carry calibrated uncertainty rather than a point prediction. Pairs with: pattern-recognition-machine-learning, probabilistic-machine-learning-intro, probabilistic-graphical-models, think-bayes, formal-math-logic-verification-engine.
---
# Machine Learning: A Probabilistic Perspective

Transfers Murphy's unifying view: most of ML is statistics with better computation, and every point prediction is a summary of a posterior distribution.

## When to use
- When the output must include uncertainty, not just a best guess.
- Choosing between generative and discriminative models for a task.
- Grounding a learning problem in a probabilistic model before picking an algorithm.

## Core framework
1. Write the joint probability model (prior + likelihood) that encodes domain knowledge.
2. Infer the posterior via exact computation when tractable, otherwise sampling (MCMC) or variational approximation.
3. Summarize the posterior for the decision at hand (predictive mean, intervals, decisions under loss).

## Techniques
- Conjugate priors make Bayesian updating closed-form for many standard models.
- Graphical models factor the joint into local pieces and make inference efficient.
- Generative models (learn p(x,y)) vs discriminative models (learn p(y|x)): generative handles missing data and small samples well, discriminative often classifies better with plenty of data.

## Verification discipline
- Check convergence of MCMC chains and sensitivity to initialization.
- Validate variational approximations against a sampling baseline on toy problems.
- Report credible intervals, not just point estimates, when uncertainty matters.

## Pairs with
pattern-recognition-machine-learning, probabilistic-machine-learning-intro, probabilistic-graphical-models, think-bayes, formal-math-logic-verification-engine.
