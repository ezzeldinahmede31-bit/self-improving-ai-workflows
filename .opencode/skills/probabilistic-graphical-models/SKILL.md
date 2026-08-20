---
name: probabilistic-graphical-models
description: Applies Koller & Friedman's Probabilistic Graphical Models to represent and reason about uncertainty: Bayesian networks and Markov networks, the conditional-independence semantics, exact inference by variable elimination and belief propagation, learning from data, and the model families that capture structure. Use when the user says 'probabilistic graphical model', 'Bayesian network', 'Markov random field', 'variable elimination', 'belief propagation', 'graphical model learning', 'Koller', or when reasoning under uncertainty needs a structured representation. Pairs with: bayesian-reasoning-machine-learning, machine-learning-probabilistic-perspective, pattern-recognition-machine-learning, algorithmic-math-reasoner.
---
# Probabilistic Graphical Models

## When to use
Use when representing and reasoning about uncertainty with structured models, or when the user asks about Bayesian networks, Markov random fields, or graphical-model inference and learning.

## Core mechanics
- Choose the graph family that matches the independence structure.
- Encode conditional-independence assumptions in the graph.
- Use variable elimination for exact inference on small models.
- Use belief propagation on trees and junction trees for structured graphs.
- Learn parameters and structure from data.
- Use approximate inference for large models.

## Verification
- Verify inference results against brute-force enumeration on a small model.
- Check that learned parameters reproduce the data statistics.
- Test that independence assumptions match the domain.
