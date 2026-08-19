---
name: probabilistic-machine-learning-intro
description: Applies Kevin Murphy's Probabilistic Machine Learning: An Introduction as the modern foundation for ML engineering: supervised and unsupervised learning framed probabilistically, neural networks and deep learning basics, loss functions and optimization, regularization and evaluation, and the practical mechanics of data loading, training loops, metrics, and reproducibility. Brings the probabilistic viewpoint up to the modern deep-learning era. Use when the user says 'probabilistic machine learning', 'Murphy PML', 'train a model from first principles', 'loss function', 'optimization', 'evaluation metrics', 'reproducibility', or when building a model and wants the probabilistic and practical reasoning behind each step. Pairs with: machine-learning-probabilistic-perspective, deep-learning-with-python-chollet, designing-machine-learning-systems, experiment-code, data-analysis.
---
# Probabilistic Machine Learning: An Introduction

Transfers Murphy's modern probabilistic ML foundation: the same probability machinery that explains classical methods now explains deep learning, and engineering discipline makes it reproducible.

## When to use
- Building a model and wanting the reasoning behind loss, optimization, and evaluation choices.
- Understanding deep learning as a continuation of probabilistic modeling, not a break from it.
- Setting up a reproducible training pipeline with sound metrics.

## Core workflow
1. Choose the model and its likelihood; the loss function is the negative log-likelihood (or its surrogate) of that model.
2. Optimize with gradient-based methods, monitoring validation as the real objective.
3. Evaluate with metrics that match the decision (accuracy, log-loss, calibration, intervals), not the training loss.

## Practical mechanics
- Data: load, split, and batch correctly; leak-free preprocessing.
- Optimization: SGD/Adam with learning-rate schedules, regularization (weight decay, dropout) as explicit priors.
- Evaluation: honest splits, calibration of probabilities, and error analysis by category.
- Reproducibility: pin seeds, record the config, log everything.

## Verification discipline
- Confirm the loss decrease is real (no data leakage, no metric gaming).
- Check calibration of predicted probabilities, not only ranking metrics.
- Reproduce the same result twice from a pinned config before trusting it.

## Pairs with
machine-learning-probabilistic-perspective, deep-learning-with-python-chollet, designing-machine-learning-systems, experiment-code, data-analysis.
