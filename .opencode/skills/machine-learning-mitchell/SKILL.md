---
name: machine-learning-mitchell
description: Applies Tom Mitchell's Machine Learning (the classic textbook) to the foundations every ML system rests on: the well-posed learning problem definition, decision tree learning and ID3 with information gain, artificial neural networks and backpropagation, evaluating hypotheses and the bias-variance trade-off, Bayesian learning and naive Bayes, computational learning theory, and instance-based and reinforcement learning. Use when the user says 'Mitchell machine learning', 'decision tree ID3', 'information gain', 'backpropagation', 'naive Bayes', 'computational learning theory', 'learning problem', 'concept learning', or when grounding a modern ML project in the classical definitions and guarantees. Pairs with: hands-on-ml-sklearn-keras-tensorflow, pattern-recognition-machine-learning, algorithmic-math-reasoner, data-science-from-scratch.
---
# Machine Learning (Mitchell)

Transfers Mitchell's classical foundations: a learning problem is well-posed, hypotheses are evaluated honestly, and the guarantees of computational learning theory apply to today's systems.

## When to use
- Defining the learning task precisely before choosing an algorithm.
- Explaining decision trees, backpropagation, or naive Bayes from first principles.
- Reasoning about generalization guarantees and the cost of learning.

## Core framework
1. A learning problem is well-posed when the target function, the training experience, and the performance measure are all explicit.
2. Search over hypotheses guided by training data; prefer simpler consistent hypotheses (Occam) unless evidence demands complexity.
3. Evaluate hypotheses on held-out data; the bias-variance decomposition explains when more data or a better hypothesis class helps.

## Techniques
- ID3 decision trees grow by maximizing information gain; prune to avoid overfitting.
- Backpropagation trains neural networks by gradient descent on the squared error.
- Naive Bayes classifies with a conditional independence assumption that often works anyway.
- Computational learning theory (PAC) gives sample-complexity bounds: how much data guarantees good generalization.

## Verification discipline
- State the target, experience, and measure explicitly before building.
- Validate generalization on unseen data, never on the training set.
- When more data fails to help, suspect bias (wrong hypothesis class), not variance.

## Pairs with
hands-on-ml-sklearn-keras-tensorflow, pattern-recognition-machine-learning, algorithmic-math-reasoner, data-science-from-scratch.
