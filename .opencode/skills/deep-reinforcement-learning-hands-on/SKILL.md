---
name: deep-reinforcement-learning-hands-on
description: Applies Maxim Lapan's Deep Reinforcement Learning Hands-On to build and train deep RL agents in practice: the RL framework (policies, value functions, returns), classic algorithms (DQN, DDPG, A2C, PPO) implemented in PyTorch, and the practical reality of debugging and evaluating agents in environments like OpenAI Gym. Use when the user says 'deep reinforcement learning hands-on', 'Lapan', 'train a DQN agent', 'PPO', 'A2C', 'deep RL in PyTorch', 'OpenAI Gym agent', or when implementing and debugging a deep RL algorithm. Pairs with: reinforcement-learning-introduction, algorithms-reinforcement-learning, rl-policy-gradient-actor-critic, tdd-sandbox-proof-engine.
---
# Deep Reinforcement Learning Hands-On

## When to use
Use when implementing and debugging deep reinforcement learning agents in practice: selecting an algorithm, training it against an environment, and fixing the many ways training silently fails.

## Core mechanics
- Frame the problem as a Markov decision process: states, actions, rewards, transitions; the goal is a policy maximizing return.
- Two families dominate: value-based (DQN learns Q-values, picks the best action) and policy-based (policy gradient methods like A2C, PPO).
- Use experience replay and target networks to stabilize value-based learning.
- For continuous control use actor-critic methods (DDPG, TD3, SAC) and normalize observations.
- The environment is the contract: define reward, reset, and step correctly; verify the environment before trusting the agent.
- Debug RL from metrics: total return per episode, value estimate, entropy, and exploration — one number is never enough.

## Verification
- Confirm the agent beats a random baseline on the environment before claiming learning.
- Log and plot the return curve across seeds; one lucky seed is not evidence of a working algorithm.

