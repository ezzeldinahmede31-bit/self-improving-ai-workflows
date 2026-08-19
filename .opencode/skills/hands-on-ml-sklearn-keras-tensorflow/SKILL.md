---
name: hands-on-ml-sklearn-keras-tensorflow
description: Applies Aurelien Geron's Hands-On Machine Learning with Scikit-Learn, Keras and TensorFlow to build ML systems end to end: the full project lifecycle (frame, get data, explore, prepare, train, evaluate, tune, present, launch, monitor), scikit-learn pipelines and model selection with cross-validation, and practical deep learning with Keras (Sequential and Functional API, convolutional and recurrent nets, transfer learning, serving). Use when the user says 'train a model end to end', 'scikit-learn pipeline', 'Keras', 'TensorFlow', 'cross-validation', 'ML project lifecycle', 'Geron', 'model tuning', 'hyperparameter search', or when going from a raw dataset to a working, monitored model. Pairs with: python-machine-learning-raschka, applied-predictive-modeling, designing-machine-learning-systems, experiment-code, data-analysis.
---
# Hands-On Machine Learning with Scikit-Learn, Keras & TensorFlow

Transfers Geron's end-to-end ML project method so a model goes from raw data to a deployed, monitored system rather than a notebook that 'worked once'.

## When to use
- Any task that turns a dataset into a working model with a repeatable pipeline.
- Choosing between scikit-learn, Keras, and a simpler approach for the task.
- Fixing a model that trains but underperforms (data prep, tuning, or architecture).

## Project lifecycle discipline
1. Frame the problem, pick the performance measure, and set a baseline before touching data.
2. Get the data, explore with plots and summary stats, and prepare features in a repeatable pipeline (imputation, scaling, encoding).
3. Train a quick baseline, then use cross-validation and hyperparameter search (GridSearchCV / RandomSearch) to improve.
4. Present results honestly, launch, and monitor for drift and degraded performance.

## Core techniques
- scikit-learn Pipelines that compose preprocessing and model so nothing leaks across folds.
- Ensemble and model selection via cross-validation rather than a single train/test split.
- Keras Sequential for most tasks, Functional API for multi-input/Output or shared layers; callbacks (EarlyStopping, ModelCheckpoint) and regularization to fight overfitting.
- Transfer learning with pretrained nets and data augmentation for small datasets.

## Verification discipline
- Prefer multiple stratified cross-validation folds over one holdout split.
- Compare any model against a naive baseline before celebrating accuracy.
- Pin random seeds and record the exact pipeline that produced the best score.

## Pairs with
python-machine-learning-raschka, applied-predictive-modeling, designing-machine-learning-systems, experiment-code, data-analysis.
