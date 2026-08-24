---
name: pattern-recognition-machine-learning
description: Applies Christopher Bishop's Pattern Recognition and Machine Learning (PRML) to reason rigorously about ML models: probability and decision theory, linear models for regression and classification, the kernel trick, Gaussian processes, latent-variable models (PCA, factor analysis, mixtures, EM), and Bayesian methods including variational inference and sampling. Covers why a model works under uncertainty, not just how to call a library. Use when the user says 'Bishop PRML', 'kernel method', 'Gaussian process', 'EM algorithm', 'latent variable', 'variational inference', 'decision theory', 'Bayesian model selection', 'bias variance', 'generative vs discriminative', or when an ML method needs its probabilistic and mathematical foundation understood before it is applied. Pairs with: elements-of-statistical-learning, machine-learning-probabilistic-perspective, probabilistic-graphical-models, information-theory-inference-learning, algorithmic-math-reasoner.
---

# Pattern Recognition and Machine Learning (Bishop) Skill

## Core Philosophy: Bayesian Thread Throughout

> Where ESL (Hastie et al.) teaches frequentist bias-variance, PRML teaches priors and posteriors. Every model — even SVMs — gets a Bayesian interpretation.

**14 Chapters, single thread:**
1. **Probability & Distributions** → 2. **Linear Regression** → 3. **Linear Classification** → 4. **Neural Networks** → 5. **Kernel Methods** → 6. **Sparse Kernel Machines (SVM/RVM)** → 7. **Graphical Models** → 8. **Mixture Models & EM** → 9. **Approximate Inference** → 10. **Sampling Methods** → 11. **Continuous Latent Variables (PCA/FA)** → 12. **Sequential Data (HMM/LDS)** → 13. **Combining Models**

---

## Chapter-by-Chapter Decision Map

| Ch | Topic | Core Question | Bayesian Answer |
|----|-------|---------------|-----------------|
| **1** | Intro | What is pattern recognition? | Model p(x), p(Cₖ), p(x\|Cₖ) → decide via p(Cₖ\|x) |
| **2** | Probability | How to represent uncertainty? | Conjugate priors, exponential family, sufficient statistics |
| **3** | Linear Regression | How to fit w? | MLE → Bayesian linear regression (Gaussian prior → Gaussian posterior) |
| **4** | Linear Classification | How to separate classes? | Generative (LDA) vs Discriminative (logistic) → Bayesian logistic (Laplace approx) |
| **5** | Neural Networks | How to learn basis functions? | Bayesian NN: prior over weights → posterior (intractable → approx) |
| **6** | Kernel Methods | How to go non-linear? | Dual representation → kernel trick → Gaussian Processes (full Bayesian) |
| **7** | Sparse Kernel Machines | How to be sparse? | SVM (frequentist margin) → RVM (Bayesian, automatic relevance determination) |
| **8** | Graphical Models | How to structure dependencies? | Directed (Bayes nets) + Undirected (Markov fields) → d-separation, factorization |
| **9** | Mixture Models & EM | How to cluster? | Latent variables z → E-step (responsibilities) / M-step (params) |
| **10** | Approximate Inference | How to compute intractable posteriors? | Variational Bayes (ELBO), Expectation Propagation, Laplace |
| **11** | Sampling Methods | How to sample from posteriors? | MCMC (Metropolis-Hastings, Gibbs), Hybrid/Hamiltonian Monte Carlo |
| **12** | Continuous Latent Variables | How to reduce dimensionality? | PCA (max variance), Factor Analysis (shared + private variance), ICA |
| **13** | Sequential Data | How to model time? | HMM (discrete latent), LDS (continuous latent), Kalman filter/smoother |
| **14** | Combining Models | How to ensemble? | Bayesian model averaging, boosting, committees |

---

## Key Decision Frameworks

### Generative vs Discriminative
| Aspect | Generative (model p(x\|Cₖ)) | Discriminative (model p(Cₖ\|x)) |
|--------|----------------------------|--------------------------------|
| **Examples** | LDA, Naive Bayes, HMM | Logistic, SVM, Neural Net |
| **Data efficiency** | Higher (uses p(x)) | Lower |
| **Missing data** | Handles naturally | Hard |
| **Outliers** | Sensitive | Robust |
| **When to use** | Small data, missing values, interpretability | Large data, pure prediction |

### Exact vs Approximate Inference
| Method | Applies When | Cost | Accuracy |
|--------|--------------|------|----------|
| **Exact (sum-product, Kalman)** | Trees, linear-Gaussian | O(NK²) | Exact |
| **Variational Bayes** | Factorizable q(z) | Fast | Lower bound (ELBO) |
| **Expectation Propagation** | Factorizable, moment matching | Medium | Often better than VB |
| **MCMC** | Any (asymptotically) | Slow | Asymptotically exact |

### Model Selection (Bayesian)
- **Bayes Factor**: p(D\|M₁)/p(D\|M₂) — marginal likelihood ratio
- **BIC**: log p(D\|θ̂) - (d/2)log N — Laplace approx to marginal likelihood
- **Cross-validation**: Frequentist alternative (Bishop Ch 1.5)

---

## Practical Rules from PRML

### When to Use Gaussian Processes (Ch 6)
- Small/medium data (< 10K points)
- Need **uncertainty quantification** (not just point predictions)
- Kernel choice = prior over functions
- **Exact inference**: O(N³) — use sparse GP (inducing points) for scale

### When to Use RVM over SVM (Ch 7)
- Need **probabilistic outputs** (not just decisions)
- Want **automatic sparsity** (ARD priors)
- Fewer support vectors → faster prediction
- **Trade-off**: Non-convex optimization (local optima possible)

### EM Algorithm (Ch 9) — Correct Application
1. **E-step**: Compute responsibilities γ(zᵢₖ) = p(zᵢₖ=1\|xᵢ, θ)
2. **M-step**: Maximize expected complete-data log-likelihood
3. **Convergence**: Log-likelihood never decreases
4. **Initialization matters**: K-means for GMM, multiple restarts

### Variational Inference (Ch 10) — Checklist
- [ ] Choose factorized q(z) = ∏ qᵢ(zᵢ)
- [ ] Derive ELBO = E[log p(x,z)] - E[log q(z)]
- [ ] Coordinate ascent: optimize each qᵢ in turn
- [ ] Monitor ELBO convergence (never decreases)

---

## Modern Relevance (2024+)

| PRML Topic | Modern Equivalent |
|------------|-------------------|
| Bayesian NN (Ch 5) | Bayes by Backprop, MC Dropout, SWAG |
| Gaussian Processes (Ch 6) | GPyTorch, BoTorch, sparse GPs |
| RVM (Ch 7) | Bayesian DL with ARD, Horseshoe priors |
| Variational Bayes (Ch 10) | VAE, β-VAE, amortized VI, normalizing flows |
| MCMC (Ch 11) | HMC/NUTS (Stan, PyMC, NumPyro) |
| HMM/LDS (Ch 13) | Deep State Space Models, RNNs with latent states |
| Model Averaging (Ch 14) | Deep Ensembles, SWAG, Monte Carlo Dropout |

---

## Trigger Phrases

`Bishop PRML`, `kernel method`, `Gaussian process`, `EM algorithm`, `latent variable`, `variational inference`, `decision theory`, `Bayesian model selection`, `bias variance`, `generative vs discriminative`

---

## Pairings

- `elements-of-statistical-learning` — frequentist counterpart
- `machine-learning-probabilistic-perspective` — Murphy's unified view
- `probabilistic-graphical-models` — Koller & Friedman's deep dive
- `information-theory-inference-learning` — MacKay's coding perspective
- `algorithmic-math-reasoner` — mathematical rigor