---
name: esl-ensembles-boosting
description: Applies the tree and ensemble chapters of Hastie, Tibshirani and Friedman's The Elements of Statistical Learning (ESL): bagging to reduce variance, random forests with feature subsampling, and boosting (AdaBoost, gradient boosting) to reduce bias — with the bias-variance reasoning that explains when each helps. Use when the user says 'bagging', 'boosting', 'AdaBoost', 'gradient boosting', 'random forest', 'ensemble methods', 'ESL ensembles', 'when to use boosting', or when combining models to beat a single strong model. Pairs with: elements-of-statistical-learning, introduction-to-statistical-learning, applied-predictive-modeling, machine-learning-design-patterns.
---
# Ensembles and Boosting (ESL)

Transfers the ESL theory of ensembles: bagging and random forests tame variance, boosting tames bias, and knowing which is the problem tells you which ensemble to use.

## When to use
- Choosing between bagging, random forests, and boosting for a task.
- Diagnosing whether overfitting or underfitting explains the current error.
- Combining models when a single model has plateaued.

## Core ideas
1. Bagging averages models trained on bootstrap samples to reduce variance, especially for high-variance base learners like deep trees.
2. Random forests add random feature subsampling at each split, decorrelating trees and improving the variance reduction.
3. Boosting sequentially fits weak learners to the current residuals, reducing bias; AdaBoost reweights data, gradient boosting fits residuals.
4. The bias-variance trade-off decides: variance-dominated error calls for bagging/forests; bias-dominated error calls for boosting or a richer base learner.

## Practice rules
- Trees and forests need little preprocessing (scale-invariant) but are sensitive to class imbalance and noise.
- Boosted models can overfit when run too long — use early stopping on validation.
- For forests, tune tree depth and the number of features per split; for boosting, tune learning rate and iterations together.

## Verification discipline
- Compare single trees, forest, and boosted model on the same folds.
- Use early stopping on validation for boosting, never on training.
- Confirm the ensemble choice matches the bias/variance diagnosis.

## Pairs with
elements-of-statistical-learning, introduction-to-statistical-learning, applied-predictive-modeling, machine-learning-design-patterns.
