---
name: prince-vision-models
description: "Models vision probabilistically: image formation, inference, and learning. Use when the user says 'computer vision models', 'Prince vision', 'image formation model', 'face recognition model', 'probabilistic vision', 'subspace methods', or when vision needs models with uncertainty, not just networks."
---

# Prince Computer Vision Models

Distilled from Simon Prince *Computer Vision: Models, Learning, and
Inference*: vision = probabilistic inference about the world from images —
model the world, model the imaging, invert with Bayes. Networks are one
inference engine among several.

## Purpose

Solve vision problems by modeling: what varies in the world, how imaging
maps world to pixels, and how to invert the map under uncertainty.

## The framework (world → image → inference)

1. **Model the world first.** Identity/expression/pose/lighting as latent
   variables with priors (subspace models: PCA/factor analysis for faces;
   mixture models for multimodal appearance). The model's capacity must
   match the variation — under-modeling shows as systematic errors on
   specific subgroups.
2. **Model the imaging.** Geometric (projection, pose) + photometric (BRDF,
   illumination, shading) + noise (sensor characteristics). Inverse graphics
   thinking: if you can render it, you can invert it (analysis by synthesis
   as the gold standard when tractable).
3. **Inference machinery.** MAP/MLE estimation; EM for latent variables;
   Bayesian model comparison for model choice; MCMC/variational where exact
   inference dies. Match algorithm to model structure (chains → dynamic
   programming, trees → belief propagation, dense → sampling/variational).
4. **Learning the models.** Maximum likelihood on labeled data; structure
   learning where the graph itself is unknown; discriminative vs generative
   chosen by data regime (generative wins scarce-data, discriminative wins
   abundant-data — the classic tradeoff, stated per problem).
5. **Modern bridge.** Deep features as learned measurements inside the same
   probabilistic scaffolding (CNN embeddings + probabilistic heads preserve
   uncertainty where pure networks discard it); evaluation with calibration
   (predicted probabilities must match frequencies) alongside accuracy.

## Verification

Vision solution ships with: world + imaging models stated, inference method
with convergence evidence, calibration numbers (not just accuracy), and
failure slices by variation type (pose/lighting/occlusion). Accuracy without
calibration and slices is a leaderboard entry, not a system.

## Pairs with

- `computer-vision-algorithms-applications` (classical algorithms),
  `deep-learning-vision-systems` (network substrate),
  `pattern-recognition-machine-learning` (probabilistic foundation),
  `bayesian-reasoning-machine-learning` (inference depth).
