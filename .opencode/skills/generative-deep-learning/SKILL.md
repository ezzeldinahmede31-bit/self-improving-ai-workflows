---
name: generative-deep-learning
description: Applies David Foster's Generative Deep Learning to design, train, and evaluate generative models — variational autoencoders (VAE), generative adversarial networks (GAN), diffusion models, and transformers — with the variational-inference and adversarial-game math behind each. Covers latent-space reasoning, the reparameterization trick, mode collapse diagnosis, and when each family wins. Use when the user says 'build a generative model', 'VAE', 'GAN', 'diffusion model', 'image generation model', 'autoencoder', 'latent space', 'reparameterization trick', 'mode collapse', 'FID score', 'Generative Deep Learning', 'Foster', 'text-to-image training', or when choosing and training a model that creates new data. Pairs with: deep-learning-goodfellow, machine-learning-design-patterns, building-ml-powered-applications, experiment-code, data-analysis.
---

# Generative Deep Learning

Transfers David Foster's framework for building generative models: pick the family that matches the data and the goal, then reason about it in latent space instead of as a black box.

## When to use
- Choosing a generative family (VAE / GAN / diffusion / transformer) for a data-creation task.
- Debugging a generative model that produces poor or collapsed samples.
- Teaching or justifying a generative architecture with its objective function.

## Family selection
1. VAE: continuous latent space, best when you want meaningful, interpolatable representations and stable training; the evidence lower bound (ELBO) is the training objective.
2. GAN: sharp realistic samples via an adversarial game; diagnose mode collapse and discriminator saturation when samples repeat or stall.
3. Diffusion: best-in-class image quality with a denoising objective over a forward noising process; slower inference unless distilled.
4. Transformers: generative modeling of sequences (text, code, music) with autoregressive next-token prediction.

## Core mechanics
- The reparameterization trick makes the VAE latent sampling differentiable.
- Adversarial training alternates generator and discriminator; balance the two to avoid collapse.
- Diffusion trains a noise-prediction network over a fixed variance schedule; sampling iterates the reverse process.
- Latent-space arithmetic (e.g., analogy directions) is where generative models earn their usefulness.

## Verification discipline
- Evaluate with task-appropriate metrics (FID, likelihood, human preference) and compare against a baseline family on the same data.
- Inspect samples qualitatively in grids; a single loss number hides mode collapse.
- Hold out a real validation set; generative metrics on training data are meaningless.

## Pairs with
deep-learning-goodfellow, machine-learning-design-patterns, building-ml-powered-applications, experiment-code, data-analysis.