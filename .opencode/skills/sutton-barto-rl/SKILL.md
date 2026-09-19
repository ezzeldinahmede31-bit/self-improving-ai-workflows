---
name: sutton-barto-rl
description: "Designs reinforcement learning from MDPs to policy gradients: Bellman, TD, and actor-critic. Use when the user says 'MDP', 'Bellman equation', 'value iteration', 'Q-learning', 'policy gradient', 'actor-critic', 'exploration exploitation', 'reward shaping', 'Sutton Barto', or when an agent must learn sequential decisions from rewards."
---

# Sutton & Barto Reinforcement Learning

Distilled from Sutton & Barto *Reinforcement Learning: An Introduction*:
all of RL is generalized policy iteration — evaluate the current policy,
improve toward greedy, repeat — under the trial-and-error + delayed-reward
contract.

## Purpose

Formulate any sequential decision problem as an MDP and choose the learning
algorithm its structure (model? function approximation? partial observability?)
permits.

## The core (in dependency order)

1. **MDP contract.** States, actions, rewards, transitions, discount gamma.
   Return = discounted future reward; policies map states to actions. Write
   the tuple down — most "RL failures" are malformed MDPs (unobserved state,
   misspecified reward, wrong horizon).
2. **Bellman optimality.** v* satisfies v*(s) = max_a E[r + gamma v*(s')].
   Dynamic programming (policy/value iteration) solves small finite MDPs
   exactly; it is also the template every approximate method imitates.
3. **Model-free prediction.** Monte Carlo (episode averages, unbiased, slow)
   vs TD(0) (bootstrap, biased, online): the bias-variance dial of RL.
   Eligibility traces (TD-lambda) interpolate the dial smoothly.
4. **Control with function approximation.** SARSA/Q-learning + linear or deep
   approximators; the deadly triad (bootstrapping + off-policy + function
   approximation) diverges — stabilize with targets (DQN), trust regions
   (TRPO/PPO clipping), or go policy-based.
5. **Policy gradients and actor-critic.** REINFORCE with baselines to cut
   variance; actor proposes, critic evaluates (A2C/A3C). Continuous actions
   and stochastic policies live here — value-only methods cannot.
6. **Exploration and reward design.** Epsilon-greedy/UCB/Thompson for the
   explore-exploit trade; curiosity/intrinsic motivation for sparse rewards.
   Reward shaping must be potential-based or it changes the optimal policy —
   shaping bugs are policy bugs.

## Verification

Each RL design ships with: the MDP tuple, algorithm + which triad leg was
defused, exploration schedule, evaluation protocol (multiple seeds,
interquartile mean — never one lucky seed), and the reward's optimal-policy
invariance argument.

## Pairs with

- `deep-reinforcement-learning-hands-on` (implementation),
  `rl-autonomous-agents` (agent framing), `rlhf-agent-alignment` (human
  feedback as reward), `thinking-probabilistic` (uncertainty),
  `experiment-code` (multi-seed evaluation).
