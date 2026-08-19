---
name: pattern-recognition-machine-learning
description: Applies Christopher Bishop's Pattern Recognition and Machine Learning to reason rigorously about ML models: probability and decision theory, linear models for regression and classification, the kernel trick, Gaussian processes, latent-variable models (PCA, factor analysis, mixtures, EM), and Bayesian methods including variational inference and sampling. Covers why a model works under uncertainty, not just how to call a library. Use when the user says 'Bishop PRML', 'kernel method', 'Gaussian process', 'EM algorithm', 'latent variable', 'variational inference', 'decision theory', 'Bayesian model selection', 'bias variance', 'generative vs discriminative', or when an ML method needs its probabilistic and mathematical foundation understood before it is applied. Pairs with: elements-of-statistical-learning, machine-learning-probabilistic-perspective, probabilistic-graphical-models, information-theory-inference-learning, algorithmic-math-reasoner.
---
# Pattern Recognition and Machine Learning (PRML)

Transfers Bishop's unified probabilistic viewpoint: every learning problem is a problem of density estimation and decision under uncertainty.

## When to use
- Choosing between a generative and a discriminative approach for a classification task.
- Understanding or justifying kernel methods, Gaussian processes, or latent-variable models.
- Any ML decision where the answer should come from the math, not from a library default.

## Core framework
1. Model the uncertainty with probability: a joint model over inputs and targets, then a decision rule that minimizes expected loss.
2. Represent knowledge about structure with latent variables and graphical models; fit them with EM when latent variables are discrete and variational methods when they are continuous.
3. Use kernels and Gaussian processes when the task is small-data, smooth, and needs uncertainty estimates.

## Technique map
- Linear regression/classification: least squares, ridge, logistic regression and the probabilistic justification.
- Kernel methods: the kernel trick, SVM, and Gaussian process regression with its predictive uncertainty.
- Latent variables: PCA and factor analysis as Gaussian models, mixtures and EM for clustering, and variational inference for approximations.
- Model comparison: evidence and Bayesian model selection instead of blind cross-validation when priors are available.

## Verification discipline
- Re-derive the update equations for EM on a small dataset and check monotone likelihood.
- Validate Gaussian-process predictions against a hand-computed posterior on a tiny set.
- Sanity-check variational bounds on toy models before trusting them at scale.

## Pairs with
elements-of-statistical-learning, machine-learning-probabilistic-perspective, probabilistic-graphical-models, information-theory-inference-learning, algorithmic-math-reasoner.
