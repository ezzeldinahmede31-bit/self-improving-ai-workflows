---
name: artificial-intelligence-modern-approach
description: Applies Russell & Norvig's Artificial Intelligence: A Modern Approach (AIMA) as the operating manual for intelligent agents — the agent paradigm, search and planning (uninformed, informed/A*, heuristic), constraint satisfaction, adversarial game search (minimax, alpha-beta), knowledge representation and logical inference, probabilistic reasoning (Bayesian networks), and decision theory with utilities. Maps each classical technique to a concrete modern use: search for graph/planning problems, CSP for scheduling, game search for adversarial agents, Bayes nets for diagnosis under uncertainty. Use when the user says 'AI agent', 'search algorithm', 'A* search', 'heuristic', 'minimax', 'alpha-beta pruning', 'constraint satisfaction problem', 'Bayesian network', 'utility theory', 'knowledge representation', 'Russell Norvig', 'AIMA', 'planning agent', 'rational agent', or when designing an agent's decision loop or choosing the right classical AI technique. Pairs with: ai-agents-architect, clrs-graph-algorithm-design, algorithmic-math-reasoner, autonomous-agents, n8n-agents.
---
# Artificial Intelligence: A Modern Approach (AIMA)

Transfers Russell & Norvig's unified view of AI — every intelligent system is an agent perceiving and acting — and maps each classical technique to a concrete modern use.

## When to use
- Designing an agent's perceive-reason-act loop and choosing its reasoning engine.
- Picking between search, planning, CSP, game search, or probabilistic inference for a decision problem.
- Re-deriving the correct algorithm for a structured decision task instead of reaching for a neural net.

## The agent paradigm
1. Define the environment: fully vs partially observable, deterministic vs stochastic, single vs multi-agent, static vs dynamic.
2. Match the technique to the environment — search and planning for deterministic worlds, game search for adversarial, probabilistic inference for uncertain worlds, decision theory for choices under risk.

## Technique selection
- Uninformed search (BFS/DFS/IDDFS) when no heuristic exists; informed A* with an admissible heuristic when one does.
- Constraint satisfaction when the problem is variables with constraints (scheduling, configuration, Sudoku-style assignment).
- Minimax with alpha-beta pruning for turn-based adversarial games; depth-limited with evaluation when the state space is huge.
- Bayesian networks for reasoning under uncertainty with explicit cause-effect structure; exact or sampled inference.

## Knowledge and decision
- Represent knowledge so inference is sound and complete; choose the formalism for the domain (logical, probabilistic, utility-based).
- Decision theory: choose actions by expected utility, folding in probability and preference, not by certainty.

## Verification discipline
- Prove admissibility of a heuristic before trusting A* optimality.
- Validate a CSP solver on small instances before scaling; check arc consistency early.
- Test game search by playing against a reference or by exhaustive lookahead on small boards.
- Sanity-check Bayesian inference against hand-computed posteriors on toy nets.

## Pairs with
ai-agents-architect, clrs-graph-algorithm-design, algorithmic-math-reasoner, autonomous-agents, n8n-agents.