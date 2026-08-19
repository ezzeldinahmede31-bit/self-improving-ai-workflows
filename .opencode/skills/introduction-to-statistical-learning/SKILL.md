---
name: introduction-to-statistical-learning
description: Applies James, Witten, Hastie and Tibshirani's An Introduction to Statistical Learning to apply modern statistical learning methods with practical intuition: the supervised learning framework, linear regression and diagnostics, classification (logistic regression, LDA, QDA), resampling (cross-validation, bootstrap), tree-based methods with bagging/boosting/random forests, and unsupervised methods with PCA and clustering. Keeps the math approachable while keeping the reasoning honest. Use when the user says 'ISL', 'linear regression', 'logistic regression', 'cross-validation', 'bootstrap', 'classification', 'random forest', 'unsupervised learning', 'statistical learning', or when choosing a modeling method and needs a grounded, practical explanation. Pairs with: elements-of-statistical-learning, applied-predictive-modeling, data-analysis, python-machine-learning-raschka.
---
# An Introduction to Statistical Learning

Transfers the ISL teaching path: build intuition first, verify with resampling, and choose the simplest model that fits the data.

## When to use
- Explaining or choosing between regression, classification, tree, and unsupervised methods.
- Any model decision that needs cross-validation and bootstrap reasoning.
- Onboarding someone into statistical learning without drowning in math.

## Core workflow
1. Frame the task as supervised (predict an output) or unsupervised (find structure), then choose a model family by the shape of the data and the interpretability needed.
2. Assess every model with resampling (k-fold cross-validation, bootstrap) — this is the ISL rule that never changes.
3. Compare models on the same folds and prefer the simpler one unless the complex one wins clearly.

## Method families
- Linear regression: the baseline; check residuals and influential points before trusting it.
- Classification: logistic regression as the default, LDA/QDA when normality holds.
- Trees and ensembles: single trees are interpretable, random forests and boosting are accurate.
- Unsupervised: PCA for dense structure, hierarchical and k-means clustering for grouping.

## Verification discipline
- Use the same resampling protocol for every method you compare.
- Never report training accuracy as the model's quality.
- Prefer interpretable models unless accuracy demands otherwise.

## Pairs with
elements-of-statistical-learning, applied-predictive-modeling, data-analysis, python-machine-learning-raschka.
