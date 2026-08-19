---
name: python-machine-learning-raschka
description: Applies Sebastian Raschka's Python Machine Learning to implement ML end to end in Python: scikit-learn workflows for classification and regression, data preprocessing and feature scaling, decision trees and ensemble methods, model evaluation and hyperparameter tuning, and an introduction to deep learning with PyTorch. Practical, code-first, with the reasoning for each choice. Use when the user says 'Python machine learning', 'scikit-learn', 'Raschka', 'preprocess features', 'ensemble methods', 'hyperparameter tuning', 'evaluate models', 'implement ML in Python', or when coding a model pipeline from scratch. Pairs with: hands-on-ml-sklearn-keras-tensorflow, applied-predictive-modeling, data-analysis, code-execution-guided-swemaster.
---
# Python Machine Learning (Raschka)

Transfers Raschka's code-first method: implement, evaluate, and tune models in Python with scikit-learn, and understand each step well enough to explain it.

## When to use
- Implementing a classification or regression pipeline in Python.
- Learning the reasoning behind preprocessing, ensembling, and tuning choices.
- Extending a scikit-learn workflow into a deeper model with PyTorch.

## Core workflow
1. Load, split, and preprocess data (feature scaling matters for distance-based and gradient methods).
2. Fit a baseline, then evaluate honestly with cross-validation and ROC/confusion analysis.
3. Tune hyperparameters with search over a grid while the metric stays resampled.
4. Combine models into ensembles when single models plateau.

## Techniques
- Decision trees, random forests, and AdaBoost with their variance/bias trade-offs.
- Regularization (L1/L2) and its effect on feature selection and stability.
- PyTorch for neural networks: dataset/dataloader, model class, optimizer, and training loop.

## Verification discipline
- Scale features before distance-based and neural methods.
- Report cross-validated metrics, never training metrics.
- Reproduce the best config from the log before deploying it.

## Pairs with
hands-on-ml-sklearn-keras-tensorflow, applied-predictive-modeling, data-analysis, code-execution-guided-swemaster.
