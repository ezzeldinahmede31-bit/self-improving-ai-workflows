---
name: neural-networks-and-deep-learning
description: Applies Michael Nielsen's free online book Neural Networks and Deep Learning to reason about neural networks from first principles: how backpropagation computes gradients, the bias-variance picture of generalization, why depth helps, and how to diagnose learning failures (slow learning, overfitting, local minima). Use when the user says 'backpropagation from scratch', 'why is my network not learning', 'weight initialization', 'cross-entropy vs quadratic loss', 'Nielsen neural networks', or when a network must be understood and fixed at the gradient level. Pairs with: deep-learning-goodfellow, deep-learning-from-scratch, grokking-deep-learning, algorithmic-math-reasoner.
---
# Neural Networks and Deep Learning

## When to use
Use when a network misbehaves and the fix must come from understanding gradients, weights, and losses rather than trial and error. Best for the conceptual core that every deep learning framework hides.

## Core mechanics
- The neuron is a weighted sum plus a nonlinear activation; the network is a composition of these functions.
- Backpropagation is the chain rule applied through the graph, producing a per-weight gradient that tells you the direction to move.
- Diagnose slow learning: saturated sigmoid activations flatten the gradient — prefer a cross-entropy cost or ReLU-style activations.
- Weight initialization matters: small random initializations near zero; poor initialization stalls early learning.
- Overfitting is best attacked with regularization (L2, dropout) and more data, not by reducing the model to trivial size.
- Deep networks win because hierarchical features compose; validate that claim per problem rather than assuming depth alone helps.

## Verification
- Trace one forward/backward pass by hand on a tiny network and confirm the computed gradient direction reduces the loss.
- Test the network on a toy problem whose answer is known before touching real data.

