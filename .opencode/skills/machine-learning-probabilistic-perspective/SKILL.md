---
name: machine-learning-probabilistic-perspective
description: Applies Kevin Murphy's Machine Learning: A Probabilistic Perspective to view all of machine learning through probability: Bayesian inference and conjugate priors, graphical models (Bayesian networks, Markov random fields), generative vs discriminative models, Monte Carlo sampling and MCMC, approximate inference (variational), and the probabilistic treatment of classification, regression, and unsupervised learning. Use when the user says 'probabilistic machine learning', 'Bayesian inference', 'conjugate prior', 'MCMC', 'graphical model', 'generative model', 'Murphy', 'uncertainty quantification', or when a model must carry calibrated uncertainty rather than a point prediction. Pairs with: pattern-recognition-machine-learning, machine-learning-probabilistic-perspective, probabilistic-graphical-models, think-bayes, formal-math-logic-verification-engine.
---

# Machine Learning: A Probabilistic Perspective (Murphy) Skill

## Core Philosophy: Probability as the Unifying Language

> "Every ML algorithm is a special case of probabilistic inference" — Murphy's 1,100-page argument that probability theory provides the grammar connecting all ML methods.

**Three pillars:**
1. **Bayesian inference** — priors, likelihoods, posteriors, model comparison
2. **Graphical models** — Bayes nets, Markov random fields, conditional independence
3. **Approximate inference** — variational, MCMC, particle filtering for intractable posteriors

---

## Chapter-by-Chapter Decision Map

| Ch | Topic | When to Use |
|----|-------|-------------|
| **1-2** | Probability review, Bayesian basics | Foundation for all ML reasoning |
| **3** | Generative vs discriminative | Choose model family: Naive Bayes vs logistic |
| **4** | Gaussian models | Linear regression, GDA, LDA, QDA |
| **5** | Bayesian statistics | Conjugate priors, MAP vs MLE, model evidence |
| **6** | Frequentist stats | MLE, confidence intervals, bias-variance |
| **7** | Linear regression | Bayesian linear reg, ARD, sparsity |
| **8** | Logistic regression | Classification, probit, multinomial |
| **9** | Multi-class / ordinal | Softmax, hierarchical softmax |
| **10** | Neural networks | Probabilistic NN, dropout as Bayesian approx |
| **11** | Kernel methods | GP, RVM, kernel ridge regression |
| **12** | Sparse linear models | Lasso, spike-and-slab, horseshoe prior |
| **13** | Graphical models | Bayes nets, d-separation, I-maps |
| **14** | Mixture models & EM | GMM, latent variables, clustering |
| **15** | Latent variable models | Factor analysis, PCA, ICA, CCA |
| **16** | Sequential data | HMM, LDS, Kalman filter/smoother |
| **17** | Approximate inference | Variational (mean-field, ELBO), EP |
| **18** | MCMC | Metropolis-Hastings, Gibbs, HMC, NUTS |
| **19** | Particle filtering | Sequential Monte Carlo, SMC |
| **20** | Model comparison | Bayes factors, BIC, cross-validation |
| **21** | Information theory | Entropy, KL, mutual info, rate-distortion |
| **22-28** | Advanced topics | Deep learning (ch 28), topic models, RL |

---

## Generative vs Discriminative — Decision Framework

| Aspect | Generative (p(x,y)) | Discriminative (p(y\|x)) |
|--------|---------------------|--------------------------|
| **Examples** | Naive Bayes, LDA, HMM, GMM | Logistic, SVM, Neural Net |
| **Data efficiency** | Higher (uses p(x)) | Lower |
| **Missing data** | Handles naturally | Hard |
| **Outliers** | Sensitive | Robust |
| **Prior knowledge** | Easy to encode (priors) | Harder |
| **When to use** | Small data, missing values, interpretability | Large data, pure prediction |

---

## Graphical Models (Ch 13) — Cheat Sheet

| Model | Structure | Inference | Use When |
|-------|-----------|-----------|----------|
| **Bayes Net (Directed)** | DAG, causal | Variable elimination, belief prop | Causal reasoning, expert systems |
| **Markov Net (Undirected)** | Factors, cliques | BP, MCMC | Spatial, image, social networks |
| **Factor Graph** | Bipartite vars/factors | Sum-product, max-product | General message passing |

**d-separation**: Read conditional independencies from graph structure.

---

## Approximate Inference — When Exact Fails

| Method | Scales To | Accuracy | Implementation |
|--------|-----------|----------|----------------|
| **Variational (mean-field)** | Large models | Lower bound (ELBO) | Coordinate ascent, black-box VI |
| **Expectation Propagation** | Medium | Often better than VI | Moment matching |
| **MCMC (Gibbs, MH, HMC)** | Any (asymptotic) | Exact | Stan, PyMC, NumPyro |
| **Particle Filter (SMC)** | Sequential/online | Sequential | Bootstrap filter, APF |

**Rule**: Try variational first (fast), MCMC for validation, PF for streaming.

---

## Decision Framework

```
Is uncertainty quantification required?
├── Yes → Full Bayesian (MCMC / VI / GPs)
│   ├── Small data → Conjugate models, exact inference
│   ├── Medium → Variational Bayes, HMC/NUTS
│   └── Large → Stochastic VI, SGD + dropout
└── No → Discriminative / point estimate
    ├── Interpretable → Linear/logistic with Bayesian regularization
    ├── Accuracy → XGBoost, Neural Net
    └── Structured output → CRF, structured prediction
```

---

## Practical Rules

- **Conjugate priors** → closed-form posteriors (Gaussian-Gaussian, Beta-Bernoulli, Dirichlet-Multinomial)
- **MAP ≠ Bayesian** — MAP is point estimate; full posterior = uncertainty
- **Model evidence p(D\|M)** → automatic Occam's razor for model selection
- **ELBO** → optimize lower bound, not log-likelihood directly
- **Gaussian Processes** → non-parametric, uncertainty built-in, O(N³) exact

---

## Trigger Phrases

`probabilistic machine learning`, `Bayesian inference`, `conjugate prior`, `MCMC`, `graphical model`, `generative model`, `Murphy`, `uncertainty quantification`

---

## Pairings

- `pattern-recognition-machine-learning` — Bayesian counterpart (Bishop)
- `probabilistic-graphical-models` — Koller & Friedman deep dive
- `bayesian-reasoning-machine-learning` — Barber's approach
- `formal-math-logic-verification-engine` — mechanical verification