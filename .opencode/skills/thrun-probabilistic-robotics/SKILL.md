---
name: thrun-probabilistic-robotics
description: "Localizes and maps under uncertainty: Bayes filters, SLAM, and sensor fusion. Use when the user says 'SLAM', 'particle filter', 'Kalman filter', 'sensor fusion', 'occupancy grid', 'Thrun', 'probabilistic robotics', or when a robot must know where it is from noisy sensors."
---

# Thrun Probabilistic Robotics

Distilled from Thrun/Burgard/Fox *Probabilistic Robotics*: the world is
uncertain and sensors lie — so robots maintain BELIEFS (probability
distributions), update them with Bayes rule, and act on the distribution,
never on a point estimate.

## Purpose

Build navigation and mapping that works in the real world: localization,
mapping, and SLAM as recursive Bayesian estimation with the right filter
per structure.

## The core (belief in, belief out)

1. **Recursive Bayes filter.** belief(x_t) ∝ p(z_t|x_t) ∫ p(x_t|x_{t-1},u_t)
   belief(x_{t-1}): motion model spreads (uncertainty grows), sensor model
   sharpens (measurement focuses). Every filter below is this equation with
   different representations — learn the equation, not just the instances.
2. **Gaussian filters (Kalman family).** KF for linear-Gaussian (optimal,
   closed form); EKF linearizes (works until nonlinearity bites — divergence
   is silent, monitor innovation consistency); UKF samples sigma points
   (better through nonlinearities, same Gaussian faith). Use when uncertainty
   is unimodal and models are smooth.
3. **Nonparametric filters.** Histogram/grid (discrete beliefs, exponential
   in dimensions — fine for low-D like 2D localization); particle filters
   (samples represent arbitrary distributions; proposal quality + resampling
   strategy decide everything; KLD-sampling adapts particle counts).
   Multimodal/global localization lives here.
4. **Mapping.** Occupancy grids (log-odds updates per cell, independence
   assumption stated), feature maps (EKF-SLAM with known correspondences),
   GraphSLAM (poses+landmarks as a sparse graph optimization problem —
   the modern formulation: frontend builds constraints, backend optimizes).
5. **Data association discipline.** Known/unknown correspondence changes
   everything; maximum-likelihood association with gating, multi-hypothesis
   tracking where ambiguity persists. Wrong associations corrupt maps
   silently — validation gates are safety equipment, not tuning.

## Verification

Navigation stack ships with: filter choice justified by distribution shape,
models (motion/sensor) calibrated on logged data, loop-closure strategy,
and trials in representative environments with ground-truth error stats.
Simulation-only validation is a progress report, not proof.

## Pairs with

- `lavalle-planning-algorithms` (acting on the belief),
  `modern-robotics` (platform kinematics),
  `bayesian-reasoning-machine-learning` (inference machinery),
  `think-bayes` (Bayesian intuition).
