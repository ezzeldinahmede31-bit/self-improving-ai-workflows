---
name: deep-learning-from-scratch
description: Applies Seth Weidman's Deep Learning from Scratch to build deep learning systems in pure Python and numpy: the mathematical foundations, building a neural network layer by layer with forward and backward passes, implementing backpropagation, and training with real optimizers — giving full control and understanding over every component. Use when the user says 'deep learning from scratch', 'Weidman', 'implement backpropagation', 'neural network in numpy', 'build a training loop without a framework', or when a component of a deep learning system must be understood by building it. Pairs with: grokking-deep-learning, neural-networks-and-deep-learning, algorithmic-math-reasoner, tdd-sandbox-proof-engine.
---
# Deep Learning from Scratch

## When to use
Use when you must understand and control every component of a deep learning system: implement networks, backpropagation, and optimizers in plain Python and numpy.

## Core mechanics
- Every layer is a function with a forward pass (input to output) and a backward pass (gradient to input and parameters).
- The math foundation is the chain rule: backpropagation multiplies the error gradient backward through each layer.
- Represent batches as matrices; the whole model is composition of layer forward passes.
- Optimizers update parameters from gradients: plain SGD, then momentum and adaptive methods (Adam).
- Build the components as small, single-responsibility modules: layers, losses, optimizers, networks.
- Test each component in isolation before composing them into the full system.

## Verification
- Compare the from-scratch gradients against a finite-difference approximation to prove backpropagation is correct.
- Train the from-scratch model on a toy problem and confirm it reaches the same loss as a reference framework version.

