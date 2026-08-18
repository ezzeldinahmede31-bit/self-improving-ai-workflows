---
name: deep-learning-goodfellow
description: Applies the Deep Learning book (Goodfellow, Bengio, Courville) as the theoretical foundation for building and debugging neural networks — the deep feedforward stack, backpropagation and its chain-rule derivation, regularization (weight decay, dropout, batch norm, data augmentation), optimization (SGD and its variants, learning-rate schedules), convolution and pooling, sequence modeling with RNNs and attention, and the practical craft of capacity, overfitting, and hyperparameter choice. Use when the user says 'backpropagation', 'why is my network overfitting', 'dropout', 'batch normalization', 'SGD vs Adam', 'learning rate', 'convolutional network', 'RNN', 'vanishing gradient', 'Goodfellow deep learning', 'capacity', 'regularization', 'deep learning theory', or when a training run behaves unexpectedly and the fix must come from first principles rather than trial and error. Pairs with: generative-deep-learning, building-ml-powered-applications, designing-machine-learning-systems, experiment-code, data-analysis.
---
# Deep Learning (Goodfellow, Bengio, Courville)

Transfers the Deep Learning book's theoretical lens so training problems are diagnosed from first principles: capacity, optimization, and generalization, not random parameter tweaking.

## When to use
- Debugging a training run (no learning, overfitting, instability, slow convergence).
- Choosing architecture and regularization for a new task.
- Reasoning about why a deep network does or does not generalize.

## Core mechanics
1. Deep feedforward networks approximate functions by composition; depth buys representational efficiency.
2. Backpropagation is the chain rule applied to the computation graph; verify gradients with finite differences on a toy model.
3. Regularization trades training fit for generalization: weight decay shrinks weights, dropout ensembles sub-networks, batch norm stabilizes internal covariate shift, data augmentation expands the effective dataset.
4. Optimization: SGD with momentum and adaptive methods (Adam) plus learning-rate schedules; the learning rate is the single most sensitive hyperparameter.

## Architecture selection
- Convolutions for spatially-structured data (images, signals) with weight sharing and pooling.
- RNNs/attention for sequences; attention mitigates vanishing gradient and long-range dependency failure.

## Verification discipline
- Watch train vs validation curves separately; divergence between them is overfitting, flat curves are underfitting or an optimization failure.
- Verify a single batch overfits completely before trusting the pipeline.
- Track gradient norms; vanishing or exploding gradients indicate depth/init problems.
- Reproduce published-baseline accuracy on a standard dataset before claiming a novel tweak.

## Pairs with
generative-deep-learning, building-ml-powered-applications, designing-machine-learning-systems, experiment-code, data-analysis.