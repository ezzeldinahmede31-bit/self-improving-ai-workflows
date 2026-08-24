---
name: deep-learning-goodfellow
description: Applies the Deep Learning book (Goodfellow, Bengio, Courville) as the theoretical foundation for building and debugging neural networks — the deep feedforward stack, backpropagation and its chain-rule derivation, regularization (weight decay, dropout, batch norm, data augmentation), optimization (SGD and its variants, learning-rate schedules), convolution and pooling, sequence modeling with RNNs and attention, and the practical craft of capacity, overfitting, and hyperparameter choice. Use when the user says 'backpropagation', 'why is my network overfitting', 'dropout', 'batch normalization', 'SGD vs Adam', 'learning rate', 'convolutional network', 'RNN', 'vanishing gradient', 'Goodfellow deep learning', 'capacity', 'regularization', 'deep learning theory', or when a training run behaves unexpectedly and the fix must come from first principles rather than trial and error. Pairs with: generative-deep-learning, building-ml-powered-applications, designing-machine-learning-systems, experiment-code, data-analysis.
---

# Deep Learning (Goodfellow, Bengio, Courville) Skill

## Core Philosophy: Theory → Practice Gap

> This book fills the gap between "it works in the demo" and "it works reliably at scale" by grounding every technique in mathematical first principles.

**Three Parts:**
1. **Applied Math & ML Basics** (Ch 2-5): Linear algebra, probability, numerical computation, ML fundamentals
2. **Modern Practical Deep Networks** (Ch 6-12): Feedforward, regularization, optimization, CNNs, RNNs, methodology
3. **Deep Learning Research** (Ch 13-20): Autoencoders, representation learning, GANs, Monte Carlo, approximate inference

---

## Part I: Mathematical Foundations

| Chapter | Core Concepts | Practical Relevance |
|---------|---------------|---------------------|
| **2: Linear Algebra** | Eigendecomposition, SVD, PCA, norms | Weight initialization, dimensionality reduction |
| **3: Probability & Info Theory** | Distributions, KL divergence, cross-entropy | Loss functions, Bayesian perspective, variational inference |
| **4: Numerical Computation** | Overflow/underflow, conditioning, gradient descent | Mixed-precision training, numerical stability |
| **5: ML Basics** | Capacity, overfitting, regularization, bias-variance | Model selection, hyperparameter tuning |

---

## Part II: Core Architectures & Training

### Ch 6: Deep Feedforward Networks
- **Universal Approximation Theorem**: 1 hidden layer → any continuous function
- **Depth efficiency**: Deep nets represent some functions exponentially more compactly
- **Activation functions**: ReLU (sparse gradients), sigmoid/tanh (saturation), Leaky ReLU, ELU

### Ch 7: Regularization for Deep Learning
| Technique | Mechanism | When to Use |
|-----------|-----------|-------------|
| **L2 (Weight Decay)** | Adds λ‖w‖² to loss | General default |
| **L1** | Adds λ‖w‖₁ → sparsity | Feature selection |
| **Dropout** | Randomly zeros units during training | Large nets, overfitting |
| **Batch Normalization** | Normalizes layer inputs → stable gradients | Deep nets, faster convergence |
| **Data Augmentation** | Synthetic examples via transforms | Vision, audio, NLP |
| **Early Stopping** | Halts when val loss rises | Free regularization |
| **Parameter Sharing** | Tie weights (CNNs, RNNs) | Structured data |

### Ch 8: Optimization for Training Deep Models
| Challenge | Theory | Practical Fix |
|-----------|--------|---------------|
| **Ill-conditioning** | Hessian eigenvalues vary widely | BatchNorm, adaptive LR |
| **Local minima** | Rare in high-D; saddle points dominate | Momentum, noise injection |
| **Vanishing/exploding gradients** | Chain rule product → 0 or ∞ | Residual connections, gradient clipping, better init |
| **Saddle points** | High-D: many negative eigenvalues | Momentum escapes flat regions |

**Optimizers:**
- **SGD + Momentum**: Velocity accumulates gradient direction
- **Nesterov**: Looks ahead before updating
- **AdaGrad**: Per-parameter LR (accumulates squared grads)
- **RMSprop**: Exponential moving average of squared grads
- **Adam**: Momentum + RMSprop (default choice)

### Ch 9: Convolutional Networks
**Why CNNs work:**
1. **Sparse interactions** (local receptive fields)
2. **Parameter sharing** (same kernel across space)
3. **Equivariant representations** (translation → translation)

| Component | Purpose |
|-----------|---------|
| **Convolution** | Feature extraction with shared weights |
| **Pooling** | Downsampling, translation invariance |
| **Strided convolution** | Learned downsampling |
| **Dilated convolution** | Expanded receptive field without pooling |

### Ch 10: Sequence Modeling (RNNs)
| Architecture | Handles | Limitation |
|--------------|---------|------------|
| **Vanilla RNN** | Variable-length sequences | Vanishing gradients |
| **LSTM** | Long-term dependencies | 3 gates, complex |
| **GRU** | LSTM simplified | 2 gates, faster |
| **Bidirectional** | Past + future context | Not for real-time |

**Teacher forcing**: Feed ground truth during training, not predictions.

### Ch 11: Practical Methodology
| Decision | Guidance |
|----------|----------|
| **Dataset size** | More data > better model > regularization |
| **Hyperparameters** | LR first, then batch size, then architecture |
| **Debugging** | Overfit single batch → check gradient flow → check loss curve |
| **Baselines** | Linear model → shallow net → deep net |

### Ch 12: Applications
Vision (ImageNet, detection, segmentation), NLP (translation, LM), Speech, Recommender systems.

---

## Part III: Research Frontiers (2016 snapshot)

| Topic | Key Insight | Modern Evolution |
|-------|-------------|------------------|
| **Autoencoders** | Compression → representation learning | VAEs, denoising, contractive |
| **Representation Learning** | Disentangling factors of variation | Self-supervised (SimCLR, BYOL, MAE) |
| **Structured Probabilistic Models** | Graphical models + deep nets | Normalizing flows, diffusion |
| **Monte Carlo Methods** | Sampling for intractable integrals | MCMC, HMC, SMC |
| **Approximate Inference** | Variational inference, EM | ELBO, mean-field, amortized VI |
| **GANs** (Goodfellow invention) | Generator vs Discriminator min-max | StyleGAN, CycleGAN, BigGAN, diffusion |

---

## Debugging Checklist (from Ch 11)

When training fails:
1. [ ] **Overfit one batch** → loss should go to ~0
2. [ ] **Gradient check** → numerical ≈ analytical
3. [ ] **Visualize activations/gradients** → dead units? exploding?
4. [ ] **Simplify** → fewer layers, smaller net, no regularization
5. [ ] **Check data** → labels correct? preprocessing leakage?
6. [ ] **Learning rate sweep** → log scale 10⁻⁵ to 10⁻¹
7. [ ] **Compare to baseline** → does a linear model beat it?

---

## Decision Framework

| Symptom | Likely Cause | First Fix |
|---------|--------------|-----------|
| Train loss ↓, val loss ↑ | Overfitting | More data, dropout, weight decay, early stop |
| Train loss flat | Underfitting / LR too low | Increase LR, bigger model, better init |
| Loss NaN / exploding | Exploding gradients | Gradient clipping, lower LR, better init |
| Loss oscillates | LR too high | Reduce LR, add momentum |
| Slow convergence | Ill-conditioning | BatchNorm, Adam, residual connections |
| Vanishing gradients (RNN) | Long sequences | LSTM/GRU, residual, gradient clipping |

---

## Trigger Phrases

`backpropagation`, `why is my network overfitting`, `dropout`, `batch normalization`, `SGD vs Adam`, `learning rate`, `convolutional network`, `RNN`, `vanishing gradient`, `Goodfellow deep learning`, `capacity`, `regularization`, `deep learning theory`

---

## Pairings

- `generative-deep-learning` — VAEs, GANs, diffusion
- `building-ml-powered-applications` — production ML systems
- `designing-machine-learning-systems` — Chip Huyen's ML lifecycle
- `experiment-code` — iterative ML experiments
- `data-analysis` — statistical validation