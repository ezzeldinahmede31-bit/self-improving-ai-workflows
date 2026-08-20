---
name: machine-learning-in-action
description: Applies Peter Harrington's Machine Learning in Action to implement core machine learning algorithms from scratch in Python: k-nearest neighbors, decision trees, naive Bayes, logistic regression, SVM, AdaBoost, and unsupervised methods, each built by hand with real examples. Use when the user says 'machine learning in action', 'Harrington', 'implement kNN from scratch', 'implement decision trees', 'naive Bayes implementation', 'build SVM from scratch', 'implement machine learning algorithms in Python', or when the mechanics of classic ML algorithms must be implemented and understood. Pairs with: data-science-from-scratch, algorithm-design-manual-war-stories, python-machine-learning-raschka, tdd-sandbox-proof-engine.
---
# Machine Learning in Action

## When to use
Use when implementing classic machine learning algorithms from scratch in Python so their mechanics are fully understood: kNN, decision trees, naive Bayes, logistic regression, SVM, AdaBoost, and unsupervised clustering.

## Core mechanics
- Each algorithm is implemented as a small, testable Python module; build them by hand instead of calling libraries.
- kNN classifies by majority vote of nearest neighbors; decision trees split data by the best feature; naive Bayes uses conditional independence.
- Logistic regression is gradient-trained classification; SVM finds a maximum-margin hyperplane; AdaBoost combines weak learners.
- Unsupervised methods (k-means, hierarchical) reveal structure without labels.
- Match the algorithm to the data shape and problem type before implementing.
- Verify each implementation against the framework version on a reference dataset.

## Verification
- Compare each from-scratch implementation's predictions to a trusted library's on the same data.
- Confirm the implementation is correct on a tiny, hand-computable example first.

