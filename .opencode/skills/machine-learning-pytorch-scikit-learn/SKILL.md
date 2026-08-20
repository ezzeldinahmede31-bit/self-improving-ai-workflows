---
name: machine-learning-pytorch-scikit-learn
description: Applies Sebastian Raschka & Yuxi Liu's Machine Learning with PyTorch and Scikit-Learn to build machine learning and deep learning systems in Python: scikit-learn pipelines and model evaluation, then PyTorch fundamentals (tensors, autograd, DataLoader) and neural network training for tabular, vision, and text tasks, with hyperparameter tuning and model interpretation. Use when the user says 'Raschka PyTorch', 'scikit-learn pipeline', 'PyTorch training loop', 'tune hyperparameters', 'evaluate a model', 'machine learning with Python end to end', or when moving from classical ML to deep learning in one workflow. Pairs with: hands-on-ml-sklearn-keras-tensorflow, python-machine-learning-raschka, deep-learning-with-pytorch, experiment-code, data-analysis.
---
# Machine Learning with PyTorch and Scikit-Learn

## When to use
Use when a task spans classical machine learning and deep learning in Python and needs one coherent workflow: data prep, model selection, evaluation, tuning, and interpretation.

## Core mechanics
- Treat scikit-learn as the tool for classical modeling: pipelines compose preprocessors with estimators; cross-validation gives honest scores.
- Layer PyTorch for deep models: tensors replace numpy arrays, autograd computes gradients, DataLoader feeds batches.
- Write a standard training loop: forward pass, loss, backward, optimizer step, epoch evaluation — keep it explicit and readable.
- Choose the right estimator by task: linear models and trees for small structured data, neural networks when features are raw and abundant.
- Evaluate with the correct protocol: stratified splits, cross-validation, and a final held-out test set never used for tuning.
- Interpret the model: feature importance and permutation importance for trees; saliency and activations for networks.

## Verification
- Compare the tuned model against a simple baseline and report the metric delta.
- Confirm the training loop reproduces on a fixed seed so results are rerunnable.

