---
name: applied-predictive-modeling
description: Applies Max Kuhn and Kjell Johnson's Applied Predictive Modeling to build dependable predictive models from data: the predictive modeling process (data splitting, preprocessing, imputation, near-zero-variance filters), model training and tuning with resampling, the linear and nonlinear model families (regression, trees, SVM, KNN), and honest model evaluation with confusion matrices, ROC curves, and gain/lift charts. Emphasis on what works in practice over theoretical purity. Use when the user says 'applied predictive modeling', 'Kuhn', 'train a classifier', 'imbalanced classes', 'resampling', 'tune hyperparameters', 'ROC', 'model comparison', 'predictive model', or when building a predictive model that must generalize to unseen data. Pairs with: introduction-to-statistical-learning, elements-of-statistical-learning, data-analysis, designing-machine-learning-systems.
---
# Applied Predictive Modeling

Transfers Kuhn & Johnson's practitioner discipline: build predictive models with a repeatable process, honest resampling, and evaluation that matches the business decision.

## When to use
- Building any predictive classifier or regressor that must work on unseen data.
- Tuning hyperparameters without fooling yourself with training error.
- Handling imbalanced classes or small datasets realistically.

## Core process
1. Split data once into training and test, then use resampling (k-fold CV, repeated CV) inside training for tuning.
2. Preprocess inside the resampling loop — scaling, imputation, and feature filters must never peek at validation folds.
3. Tune each model family over a grid, choose by the resampled metric, then assess the final model once on the held-out test.

## Practice rules
- Imbalanced classes: use the right metric (sensitivity, specificity, ROC AUC, prevalence-scaled), and consider resampling strategies inside CV.
- Near-zero-variance and highly correlated predictors are filtered early.
- Compare a handful of model families (regularized linear, trees, SVM, KNN) with the same protocol instead of betting on one.
- Report gains/lift for business impact, not just accuracy.

## Verification discipline
- The test set is touched exactly once at the end.
- Tuning metrics come from resampling, never from the test set.
- A model that wins on accuracy but loses on the business metric is the wrong model.

## Pairs with
introduction-to-statistical-learning, elements-of-statistical-learning, data-analysis, designing-machine-learning-systems.
