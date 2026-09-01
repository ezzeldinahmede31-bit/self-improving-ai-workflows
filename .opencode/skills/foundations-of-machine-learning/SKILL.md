---
name: foundations-of-machine-learning
description: Applies Mohri, Rostamizadeh & Talwalkar's Foundations of Machine Learning to reason about learning algorithms with a theoretical backbone: PAC learning, Rademacher complexity, margin-based bounds, SVM and kernels, boosting, online learning, and learning with structured outputs. Use when the user says 'Rademacher complexity', 'PAC bound', 'margin theory', 'Mohri', 'SVM theory', 'online learning', 'structured prediction', or when the theoretical guarantees of a learning algorithm matter. Pairs with: understanding-machine-learning, learning-with-kernels, algorithmic-math-reasoner, formal-math-logic-verification-engine.
---

# Foundations of Machine Learning (Mohri, Rostamizadeh, Talwalkar) Skill

## Core Philosophy: Algorithmic Analysis with Guarantees

> "Focus on the analysis and theory of algorithms" — every algorithm gets: **generalization bound**, **optimization guarantee**, and **complexity characterization**.

**Three complexity measures (Ch 3):**
| Measure | Type | Computation | Bound Quality |
|---------|------|-------------|---------------|
| **Rademacher complexity** | Data-dependent | NP-hard (empirical), approximable | Tightest, data-dependent |
| **Growth function** | Combinatorial | Finite for VC classes | Looser |
| **VC-dimension** | Combinatorial | Often easy | Distribution-free, classic |

---

## Chapter-by-Chapter Decision Map

| Ch | Topic | Guarantee | When to Use |
|----|-------|-----------|-------------|
| **1** | PAC learning framework | Sample complexity | Binary classification, realizable |
| **2** | Generalization bounds (Rademacher) | Data-dependent | Any hypothesis class |
| **3** | VC-dimension, growth function | Distribution-free | Infinite hypothesis classes |
| **4** | SVMs, margin bounds | Large margin → low Rademacher | Binary classification, high-dim |
| **5** | Kernel methods | RKHS, representer theorem | Non-linear, kernelizable |
| **6** | Boosting (AdaBoost) | Margin distribution | Ensemble, weak learners |
| **7** | On-line learning | Regret bounds | Streaming, adversarial |
| **8** | Multi-class | Error-correcting codes, one-vs-all | K-class problems |
| **9** | Ranking | Pairwise, listwise | Information retrieval |
| **10** | Regression | Rademacher for real-valued | Continuous outputs |
| **11** | Algorithmic stability | Uniform / hypothesis stability | SGD, regularized ERM |
| **12** | Dimensionality reduction | PCA, kernel PCA, bounds | Feature extraction |
| **13** | Learning automata/language | Angluin's L*, regular languages | Grammar induction |
| **14** | Reinforcement learning | MDPs, bandits, Q-learning | Sequential decisions |

---

## Rademacher Complexity (Ch 2-3) — The Modern Standard

**Definition**: Rₙ(ℋ) = E_σ [sup_{h∈ℋ} (1/n) Σ σᵢ h(xᵢ)] where σᵢ ~ Rademacher(±1)

**Generalization bound** (with prob 1-δ):
```
L_D(h) ≤ L_S(h) + 2 Rₙ(ℋ) + O(√(log(1/δ)/n))
```

**Advantages over VC bounds:**
- Data-dependent (uses training data distribution)
- Tighter for structured classes (kernels, neural nets)
- Leads to margin bounds for SVMs

**Key bounds:**
| Hypothesis Class | Rademacher Bound |
|------------------|------------------|
| Linear (‖w‖ ≤ Λ) | Λ √(tr(K)/n) |
| RKHS (kernel K) | √(tr(K)/n) |
| Neural net (L layers) | O(L √(log n / n)) |
| Decision tree (depth d) | O(√(d/n)) |

---

## Margin Theory for SVMs (Ch 4)

**Margin bound** (with prob 1-δ):
```
L_D(h) ≤ L_S^γ(h) + O(√(R²/γ²n)) + O(√(log(1/δ)/n))
```
where γ = margin, R = data radius.

**Key insight**: Large margin → small effective Rademacher complexity → good generalization even in infinite dimensions.

**Kernel trick**: SVM in RKHS = linear SVM in feature space → margin bounds transfer.

---

## Boosting & Margin Distribution (Ch 6)

| Algorithm | Guarantee | Bound |
|-----------|-----------|-------|
| **AdaBoost** | Margin distribution | L_D ≤ Pr[margin ≤ θ] + O(√(d log(n/θ)/n)) |
| **Gradient Boosting** | Functional gradient descent | Convergence in function space |

**Key insight**: Boosting minimizes exponential loss → maximizes margins → generalization.

---

## Online Learning (Ch 7) — Regret Bounds

| Algorithm | Regret | Setting |
|-----------|--------|---------|
| **Perceptron** | O(R²/γ²) | Linear separable |
| **Winnow** | O(log n) | Sparse relevant features |
| **OGD** | O(√T) | Convex losses |
| **Weighted Majority** | O(√(T log N)) | Expert advice |

**Online-to-batch conversion**: Average online predictor → batch generalization.

---

## Structured Outputs (Ch 8-9)

| Problem | Approach | Guarantee |
|---------|----------|-----------|
| **Multi-class** | Error-correcting codes, CSMC | O(log K) factor |
| **Ranking** | Pairwise/listwise reduction | AUC bounds |
| **Structured (sequences, trees)** | Margin-based structured SVM | Rademacher for structured ℋ |

---

## Decision Framework

```
Need theoretical guarantee for algorithm choice?
├── Yes → Which framework?
│   ├── Distribution-free (worst-case) → VC-dimension (Ch 3)
│   ├── Data-dependent (tighter) → Rademacher complexity (Ch 2)
│   ├── Algorithm-specific → Stability (Ch 11)
│   └── Online/streaming → Regret bounds (Ch 7)
├── Specific algorithm?
│   ├── SVM → Margin bounds (Ch 4)
│   ├── Kernel methods → RKHS bounds (Ch 5)
│   ├── Boosting → Margin distribution (Ch 6)
│   └── Deep learning → Stability + Rademacher (Ch 2, 11)
└── No → Empirical validation
```

---

## Practical Rules

- **Rademacher** for data-dependent, tight bounds
- **VC-dimension** for distribution-free, combinatorial
- **Margin** for SVM/kernel methods
- **Stability** for SGD, regularized ERM, differential privacy
- **Regret** for online, streaming, adversarial settings
- **Structured prediction** → reduce to margin-based binary

---

## Trigger Phrases

`Rademacher complexity`, `PAC bound`, `margin theory`, `Mohri`, `SVM theory`, `online learning`, `structured prediction`

---

## Pairings

- `understanding-machine-learning` — Shalev-Shwartz & Ben-David's VC focus
- `learning-with-kernels` — Schölkopf & Smola's kernel methods
- `algorithmic-math-reasoner` — mathematical rigor
- `formal-math-logic-verification-engine` — mechanical verification