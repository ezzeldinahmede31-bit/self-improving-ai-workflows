---
name: feature-engineering-machine-learning
description: Applies Alice Zheng and Amanda Casari's Feature Engineering for Machine Learning to turn raw data into features that make models work: numeric features (scaling, binarization, transformations, interactions), categorical features (one-hot, dummy, feature hashing), text features (bag of words, TF-IDF, word embeddings), and the feature-engineering pipeline integrated with modeling. Use when the user says 'feature engineering', 'feature extraction', 'one-hot encoding', 'feature hashing', 'TF-IDF', 'handle categorical data', 'feature interactions', 'Zheng Casari', or when raw data must become a usable feature matrix. Pairs with: applied-predictive-modeling, python-for-data-analysis, hands-on-ml-sklearn-keras-tensorflow, data-pipelines-pocket-reference.
---
# Feature Engineering for Machine Learning

Transfers Zheng & Casari's method: features are not just extracted — they are engineered deliberately, then validated as part of the model, not in isolation.

## When to use
- Turning raw CSV/log/text data into a model-ready feature matrix.
- Deciding how to encode categorical or text fields.
- Debugging a model that underperforms because of weak features.

## Core practice
1. Numeric features: scale appropriately, handle outliers, and consider log/count transforms and binning when the relationship is nonlinear.
2. Categorical features: one-hot for low cardinality, feature hashing for high cardinality or streaming, ordinal encoding only when order is real.
3. Text features: bag of words, TF-IDF, and word embeddings; choose by task size and whether meaning or presence matters.
4. Interactions and domain features: combine fields when domain knowledge says the combination is what predicts.

## Engineering discipline
- Build features in a pipeline that runs inside cross-validation so no information leaks.
- Record exactly how each feature was derived so it can be reproduced in production.
- Validate feature value by ablation: add/remove features and watch the resampled metric.

## Verification discipline
- Check the feature matrix for leakage from future data or the target.
- Verify categorical encodings survive unseen categories at prediction time.
- Confirm the engineered feature set improves the resampled metric before keeping it.

## Pairs with
applied-predictive-modeling, python-for-data-analysis, hands-on-ml-sklearn-keras-tensorflow, data-pipelines-pocket-reference.
