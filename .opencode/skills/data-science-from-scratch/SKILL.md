---
name: data-science-from-scratch
description: Applies Joel Grus' Data Science from Scratch to implement the core algorithms of data science in plain Python without libraries: linear algebra, statistics and probability, gradient descent, data munging and cleaning, correlation, and machine learning algorithms (k-nearest neighbors, naive Bayes, simple linear/logistic regression, decision trees, neural networks), plus database and MapReduce thinking. Use when the user says 'data science from scratch', 'implement kNN', 'implement logistic regression', 'gradient descent', 'implement from scratch', 'Grus', 'data science basics', or when the mechanics of an algorithm must be understood by building it by hand. Pairs with: think-stats, think-bayes, python-for-data-analysis, algorithmic-math-reasoner, tdd-sandbox-proof-engine.
---
# Data Science from Scratch

Transfers Grus' method: implement every algorithm by hand so the mechanics are real, then trust libraries because you know what they do.

## When to use
- Learning or teaching the internals of core data-science algorithms.
- Writing a hand-rolled implementation to verify or replace a library call.
- Building intuition for gradient descent, regression, and classification.

## Core practice
1. Reimplement the building blocks (linear algebra, statistics, probability, gradient descent) so later algorithms are built on understood primitives.
2. Implement each model family (kNN, naive Bayes, linear/logistic regression, decision trees, neural nets) from scratch and test against a known answer.
3. Use the hand-built versions to validate what the libraries are doing.

## Algorithms
- Gradient descent and its variants as the engine of most learning.
- kNN and naive Bayes as simple baselines with clear assumptions.
- Decision trees by information gain; neural networks by backpropagation.
- Databases and MapReduce for the data-processing mindset that scales.

## Verification discipline
- Compare the hand-written output against a library on the same input.
- Test edge cases (empty data, all-same class, zero variance) before trusting the code.
- Prefer correctness of the mechanic over cleverness.

## Pairs with
think-stats, think-bayes, python-for-data-analysis, algorithmic-math-reasoner, tdd-sandbox-proof-engine.
