---
name: hundred-page-machine-learning-book
description: Applies Andriy Burkov's The Hundred-Page Machine Learning Book as a concise, complete map of ML: supervised learning (regression, classification, decision trees, ensembles, neural networks), unsupervised learning (clustering, dimensionality reduction), and the practical concerns of data preparation, evaluation, model selection, and performance. Use when the user says 'hundred page machine learning', 'Burkov', 'quick ML overview', 'ML fundamentals', 'supervised vs unsupervised', 'ml cheat sheet', or when a compact yet rigorous foundation of ML is needed before applying a specific method. Pairs with: introduction-to-statistical-learning, machine-learning-mitchell, data-science-from-scratch, hands-on-ml-sklearn-keras-tensorflow.
---
# The Hundred-Page Machine Learning Book

Transfers Burkov's compact map of ML: the essential methods and the reasoning that ties them together, in the least space that still stays correct.

## When to use
- Getting a rigorous overview of ML before diving into a specific method.
- Refreshing the mental model of supervised, unsupervised, and evaluation practice.
- Onboarding: the shortest path from zero to a working mental map.

## Core map
1. Supervised learning: regression (linear, regularized), classification (logistic, SVM, trees, ensembles), and neural networks, each with its inductive bias.
2. Unsupervised learning: clustering (k-means, hierarchical, DBSCAN) and dimensionality reduction (PCA, autoencoders, t-SNE).
3. Evaluation and model selection: honest splits, cross-validation, and the bias-variance reasoning that picks the method.

## Practice rules
- Start with the simplest model that could work; add complexity only when the metric demands it.
- Evaluate with the same protocol for every candidate.
- Understand the assumptions behind each method (linearity, distance metric, independence) before applying it.

## Verification discipline
- Every claim about a model is backed by a resampled metric.
- Prefer methods whose failure modes you can reason about.
- Know whether your problem is supervised or unsupervised before modeling.

## Pairs with
introduction-to-statistical-learning, machine-learning-mitchell, data-science-from-scratch, hands-on-ml-sklearn-keras-tensorflow.
