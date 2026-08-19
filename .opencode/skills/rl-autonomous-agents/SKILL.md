---
name: rl-autonomous-agents
description: "Applies reinforcement learning to autonomous agents: define the reward signal, the policy, exploration, and the safety constraints, and know when RL is worth the complexity versus supervised or heuristic control. Covers reward design pitfalls and the evaluation that proves a learned policy. Use when the user says 'reinforcement learning', 'reward design', 'learned policy', 'RLHF', 'bandit', 'reward hacking', or 'train an agent to act'."
---
# rl-autonomous-agents

Reinforcement learning trains an agent by trial, feedback, and reward rather than by labeled examples. This skill encodes when RL is the right tool, how to design a reward that encodes the real goal, how to bound exploration, and how to evaluate a learned policy honestly against the task it must do.

## Core principles
- The reward defines the objective; a mis-specified reward produces a mis-specified agent.
- RL is a heavy lever: prefer supervised, heuristic, or interactive control until the problem clearly needs it.
- Exploration is bounded and safe: the agent cannot take irreversible actions during learning.
- The environment is a simulation or sandbox first; the policy transfers to the real system only after validation.
- Reward hacking is expected: an agent optimizes what you reward, so reward and eval must be aligned.
- A learned policy is judged by real-task metrics, not by the reward curve alone.

## Key patterns
- Reward specification: encode the task outcome plus penalties for unsafe or wasteful behavior.
- Bandit-first: for simple decisions, contextual bandits beat full RL and need far less data.
- Policy iteration loop: act in the environment, collect returns, update the policy, and re-evaluate.
- Safety envelope: hard constraints outside the policy's control stop dangerous actions regardless of the reward.
- Sim-to-real: train in a sandbox with realistic noise, then validate in a staging environment before live use.
- Eval contract: a fixed set of scenarios grades the learned policy against the heuristic baseline.

## Applying this to n8n/Python automation
- Use RL only for decisions with a clear, repeated reward signal; model everything else with rules or supervised heuristics.
- Prototype in Python against a sandboxed environment before wiring any learned policy into n8n.
- Keep a heuristic baseline running and compare the learned policy against it on a fixed scenario set.
- Put the safety envelope as a separate node: policy output passes through hard validation before any action.
- Log rewards, actions, and outcomes per episode so the policy's behavior is auditable.

## Hard rules
- Never run an RL agent with an unsafe reward or unbounded exploration.
- Never replace a working heuristic with a learned policy without beating it on the eval set.
- Never deploy a learned policy without a hard safety envelope outside its control.
- Never judge a policy by its reward curve alone; grade it on the real-task scenarios.

## Pairs with
autonomous-agent-patterns, ai-engineering-foundation-models, evaluation, machine-learning-design-patterns, designing-machine-learning-systems, build-gates-pipeline
