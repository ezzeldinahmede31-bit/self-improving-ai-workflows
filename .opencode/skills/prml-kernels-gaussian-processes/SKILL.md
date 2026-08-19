---
name: prml-kernels-gaussian-processes
description: Applies the kernel-methods chapters of Christopher Bishop's Pattern Recognition and Machine Learning (PRML): the kernel trick, common kernel functions, kernel-based models for regression and classification, and Gaussian processes with their predictive uncertainty and hyperparameter learning. Use when the user says 'kernel trick', 'Gaussian process', 'kernel function', 'RBF kernel', 'covariance function', 'Bayesian kernel regression', 'GP hyperparameters', 'uncertainty prediction', or when a model must make smooth predictions with calibrated uncertainty on small data. Pairs with: pattern-recognition-machine-learning, machine-learning-probabilistic-perspective, formal-math-logic-verification-engine, algorithmic-math-reasoner.
---
# Kernels and Gaussian Processes (PRML)

Transfers Bishop's treatment of kernels and Gaussian processes: replace explicit feature maps with similarity functions, and get predictive uncertainty for free.

## When to use
- Small-data regression/classification where uncertainty estimates matter.
- Choosing and justifying a kernel for an SVM or kernel model.
- Modeling smooth functions with Gaussian processes and learning their hyperparameters.

## Core ideas
1. The kernel trick: K(x,x') = phi(x)^T phi(x') lets models use feature spaces implicitly; choose the kernel to encode the similarity you believe in.
2. Common kernels (RBF, polynomial, linear) and their inductive biases; combine or add kernels for structured similarity.
3. Gaussian process regression: place a GP prior over functions, condition on data, and get a posterior with mean and variance at any input.
4. Learn kernel hyperparameters by maximizing the marginal likelihood (evidence), with care against overfitting.

## Practice rules
- Normalize inputs before kernel methods; RBF kernels are scale-sensitive.
- Use GP predictive variance to flag low-confidence regions and drive active data collection.
- Validate hyperparameter fits with held-out log marginal likelihood where possible.

## Verification discipline
- Compare kernel choice on the same folds; the kernel is the model's prior.
- Sanity-check GP predictions against a hand-computed posterior on a tiny dataset.
- Watch for overconfident GPs when the kernel is misspecified.

## Pairs with
pattern-recognition-machine-learning, machine-learning-probabilistic-perspective, formal-math-logic-verification-engine, algorithmic-math-reasoner.
