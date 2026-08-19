---
name: prml-mixture-models-em
description: Applies the latent-variable and mixture-model chapters of Christopher Bishop's Pattern Recognition and Machine Learning (PRML): mixtures of Gaussians, the EM algorithm and its derivation, k-means as a limit of EM, and the use of latent variables for clustering, missing data, and representation. Use when the user says 'mixture of Gaussians', 'EM algorithm', 'expectation maximization', 'latent variable', 'k-means', 'soft clustering', 'Gaussian mixture model', 'missing data', or when clustering data that naturally comes from several groups or when some data is incomplete. Pairs with: pattern-recognition-machine-learning, machine-learning-probabilistic-perspective, data-science-from-scratch, algorithmic-math-reasoner.
---
# Mixture Models and EM (PRML)

Transfers Bishop's latent-variable view of clustering: unobserved cluster labels make mixture models a probabilistic foundation under k-means.

## When to use
- Clustering data that comes from several groups (soft vs hard assignments).
- Estimating models when data is incomplete or when latent variables explain the structure.
- Understanding why EM converges and when it finds bad local optima.

## Core framework
1. Model the data as a mixture of component distributions; the missing cluster label is a latent variable.
2. EM alternates: E-step computes responsibilities (probability each point belongs to each component), M-step re-estimates parameters from those responsibilities.
3. k-means is the hard-assignment limit of EM on a mixture of Gaussians with shared, spherical covariance.
4. EM also fits models with missing data and general latent-variable models beyond clustering.

## Practice rules
- Run EM from multiple initializations; it converges to a local optimum, not necessarily the global one.
- Choose the component count with held-out likelihood or information criteria, not eyeballing.
- Report cluster uncertainty (responsibilities), not only the hard assignment.

## Verification discipline
- Check monotone likelihood increase across iterations as an EM sanity check.
- Validate the model on held-out data (log-likelihood), not training fit.
- Compare against k-means on the same data to confirm the probabilistic value.

## Pairs with
pattern-recognition-machine-learning, machine-learning-probabilistic-perspective, data-science-from-scratch, algorithmic-math-reasoner.
