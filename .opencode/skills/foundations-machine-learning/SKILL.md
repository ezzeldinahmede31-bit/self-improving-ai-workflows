---
name: foundations-machine-learning
description: Applies Mohri, Rostamizadeh & Talwalkar's Foundations of Machine Learning to reason about learning algorithms with a theoretical backbone: PAC learning, Rademacher complexity, margin-based bounds, SVM and kernels, boosting, online learning, and learning with structured outputs. Use when the user says 'Rademacher complexity', 'PAC bound', 'margin theory', 'Mohri', 'SVM theory', 'online learning', 'structured prediction', or when the theoretical guarantees of a learning algorithm matter. Pairs with: understanding-machine-learning, learning-with-kernels, algorithmic-math-reasoner, formal-math-logic-verification-engine.
---
# Foundations of Machine Learning

## When to use
Use when the theoretical guarantees of a learning algorithm matter, or when the user asks about Rademacher complexity, margin bounds, or SVM theory.

## Core mechanics
- Use Rademacher complexity to bound generalization.
- Derive margin-based bounds for large-margin methods.
- Build SVM and kernel methods with their guarantees.
- Analyze boosting and online learning.
- Extend the theory to structured outputs when needed.
- Keep the analysis honest about what is proven.

## Verification
- Reproduce the bounds on a small dataset.
- Verify that empirical error matches the theory.
- Test kernels against the guarantees on synthetic data.
