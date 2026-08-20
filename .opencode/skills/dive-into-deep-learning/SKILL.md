---
name: dive-into-deep-learning
description: Applies the open-source Dive into Deep Learning (Zhang, Lipton, Li, Smola) to learn and build deep learning with code-first interactive notebooks: linear and softmax regression, multilayer perceptrons, CNNs, RNNs and modern sequence models, attention and transformers, optimization algorithms, and the computational performance practices (GPUs, data loaders, distributed training). Use when the user says 'D2L', 'dive into deep learning', 'code-first deep learning', 'attention and transformers', 'optimization for deep learning', 'GPU training', 'sequence modeling with attention', or when learning or building deep learning with runnable code. Pairs with: deep-learning-with-python, deep-learning-illustrated, machine-learning-pytorch-scikit-learn, litellm-tier-router.
---
# Dive into Deep Learning

## When to use
Use when you want deep learning taught through runnable code (PyTorch/MXNet style) and when a topic needs both math and an executable example. Best for the full curriculum from regression to transformers.

## Core mechanics
- Every chapter pairs the math with an executable notebook: derive, then implement, then train on a real dataset.
- Start from linear regression and softmax classification as the simplest learnable models, then compose layers into MLPs.
- Convolutional networks exploit translation invariance for grids; RNNs and attention model sequential dependence.
- Attention and the transformer are the modern sequence primitive: self-attention relates positions, multi-head attention expands capacity, and the model composes into encoder/decoder stacks.
- Choose optimization with the loss landscape in mind: SGD with momentum, Adam, learning-rate schedules; watch for vanishing/exploding gradients.
- Make computation fast and correct: vectorized batches, GPU residency, efficient data loading, and distributed training for large models.

## Verification
- Reproduce each model's published loss/accuracy curve on the reference dataset before adapting it.
- Confirm gradients flow by checking that training loss strictly decreases on a small batch.

