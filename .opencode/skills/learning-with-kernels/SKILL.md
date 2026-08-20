---
name: learning-with-kernels
description: Applies Scholkopf & Smola's Learning with Kernels to build kernel methods with mathematical grounding: kernels and feature spaces, the representer theorem, RKHS, SVM and its variants, kernel ridge regression, and kernel-based learning algorithms. Use when the user says 'kernel method', 'kernel trick', 'RKHS', 'representer theorem', 'Scholkopf Smola', 'kernel ridge', 'SVM kernel', or when a kernel method needs a rigorous grounding. Pairs with: prml-kernels-gaussian-processes, gaussian-processes-machine-learning, foundations-machine-learning, algorithmic-math-reasoner.
---
# Learning with Kernels

## When to use
Use when a kernel method needs rigorous grounding, or when the user asks about the kernel trick, RKHS, or the representer theorem.

## Core mechanics
- Define kernels as inner products in feature spaces.
- Use the representer theorem to justify kernel predictors.
- Work in the RKHS when analyzing the method.
- Build SVM and kernel ridge regression from the theory.
- Choose and combine kernels for the data.
- Scale kernel methods with approximations when needed.

## Verification
- Verify that a kernel matrix is positive semidefinite.
- Check that the representer theorem form matches the solution.
- Compare kernel prediction against a linear baseline.
