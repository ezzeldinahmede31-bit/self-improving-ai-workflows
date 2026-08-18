---
name: hands-on-ai-python
description: Applies Prateek Joshi's Artificial Intelligence with Python to implement classic AI algorithms from scratch in Python — search (BFS, DFS, A*), constraint satisfaction, adversarial game search (minimax, alpha-beta), knowledge representation, probability and Bayesian inference, and fundamentals of machine learning, neural networks, natural language processing, and computer vision. Covers the algorithmic core behind modern AI so the agent can reason about any AI system rather than only calling libraries. Use when the user says 'implement A*', 'BFS DFS search', 'minimax', 'alpha-beta pruning', 'constraint satisfaction', 'Bayesian inference', 'AI from scratch in Python', 'Joshi', 'knowledge representation', 'build a search agent', 'explain how an AI algorithm works', or when a task needs the algorithmic backbone of an AI system explained or implemented. Pairs with: clrs-algorithm-mastery, algorithmic-math-reasoner, deep-learning-goodfellow, code-execution-guided-swemaster, tdd-sandbox-proof-engine.
---

# Hands-On AI with Python

Transfers Prateek Joshi's from-scratch implementations of the classic AI algorithm toolkit: understand and implement the search, game, constraint, and probabilistic machinery that every modern AI system builds on.

## When to use
- Implementing or explaining classical AI algorithms (search, games, CSP, Bayesian inference).
- Building the algorithmic core of an agent before adding learned components.
- Understanding what a library call actually computes.

## The classic toolkit
1. Search: BFS for unweighted shortest paths, DFS with backtracking for exhaustive exploration, A* with an admissible heuristic for informed search.
2. Adversarial search: minimax with alpha-beta pruning for turn-based games; the evaluation function decides strength.
3. Constraint satisfaction: backtracking with forward checking and constraint propagation (arc consistency).
4. Probabilistic reasoning: Bayesian inference with prior, likelihood, and posterior; Naive Bayes as the workhorse classifier.
5. Learning: gradient descent, perceptrons, and the forward/backward pass as the core of neural networks.

## Implementation discipline
- Represent states explicitly so the algorithm's transitions are testable.
- Verify each algorithm on a hand-checkable example before scaling the input.
- Use the classic algorithm to validate library-based implementations (evidence over memory).

## Pairs with
clrs-algorithm-mastery, algorithmic-math-reasoner, deep-learning-goodfellow, code-execution-guided-swemaster, tdd-sandbox-proof-engine.