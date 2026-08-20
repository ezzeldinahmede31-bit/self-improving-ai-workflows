---
name: pgm-inference-variable-elimination
description: Applies the inference chapters of Koller & Friedman's Probabilistic Graphical Models to answer queries from a graphical model: variable elimination and its complexity, belief propagation on trees, junction trees, approximate inference by sampling and variational methods. Use when the user says 'variable elimination', 'belief propagation', 'junction tree', 'exact inference', 'approximate inference', 'sampling inference', or when probabilities must be computed from a graphical model. Pairs with: probabilistic-graphical-models, bayesian-reasoning-machine-learning, algorithmic-math-reasoner, formal-math-logic-verification-engine.
---
# Inference in Probabilistic Graphical Models

## When to use
Use when probabilities must be computed from a graphical model, or when the user asks about variable elimination, belief propagation, or approximate inference.

## Core mechanics
- Run variable elimination with an elimination order.
- Propagate beliefs on tree-structured models.
- Use junction trees for exact inference on more complex graphs.
- Fall back to sampling for large models.
- Apply variational methods when sampling is too slow.
- Report the complexity of the chosen method.

## Verification
- Verify elimination results against enumeration on a small model.
- Check belief propagation against variable elimination.
- Test approximate methods against exact results where feasible.
