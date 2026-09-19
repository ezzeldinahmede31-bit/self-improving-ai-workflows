---
name: shoham-multiagent-systems
description: "Designs strategic multi-agent systems: game forms, social choice, and protocols. Use when the user says 'multiagent systems', 'social choice', 'voting rules', 'Shoham Leyton-Brown', 'mechanism with verification', 'Nash implementation', 'distributed mechanism design', or when self-interested agents share rules."
---

# Shoham Multiagent Systems

Distilled from Shoham & Leyton-Brown *Multiagent Systems*: game theory +
computation — equilibria are necessary but not sufficient; add complexity,
communication, and protocol design, and systems become engineerable.

## Purpose

Design agent societies (markets, voting, negotiations, teams) whose
equilibria are good, reachable, and computable — then implement the rules
that get you there.

## The toolkit (beyond basic game theory)

1. **Game representations that scale.** Normal/extensive form for analysis;
   compact forms for structure: congestion/action-graph games (payoffs from
   counts, not profiles), Bayesian games (types for private information).
   Representation size decides computability — choose it deliberately.
2. **Equilibrium + computation.** Nash existence is free; FINDING equilibria
   is PPAD-complete in general (Lemke-Howson for 2-player, support
   enumeration small cases). Correlated equilibrium (choreographer device)
   is polynomial via linear programming — often the reachable compromise.
   State the solution concept AND its complexity, always together.
3. **Social choice machinery.** Voting rules compared axiomatically
   (Condorcet vs Borda vs plurality — no rule satisfies everything: know
   Arrow/Gibbard-Satterthwaite boundaries); fair division (cake-cutting
   protocols, envy-freeness vs proportionality); matching (Gale-Shapley
   stability for two-sided markets like residency/school choice).
4. **Negotiation and teamwork.** Alternating-offers protocols, concession
   strategies with deadlines (time pressure as mechanism); joint intentions
   (commitment + conventions) for collaborative teams; role allocation under
   uncertainty.
5. **Verification-flavored mechanisms.** Audits and spot-checks that make
   honesty the equilibrium (cheating detectable with enough probability);
   distributed mechanism design where no trusted center exists (consensus +
   incentives co-designed).

## Verification

Agent-society design ships with: representation + size analysis, solution
concept with complexity class, impossibility boundaries checked (Arrow/
Gibbard-Satterthwaite where voting/choice involved), and simulation evidence
(agents actually converging in the implemented protocol). Theory without the
simulation is a proposal.

## Pairs with

- `roughgarden-game-theory` (equilibrium + PoA core),
  `enterprise-multi-agent-systems` (implementation),
  `pgm-inference-variable-elimination` (Bayesian agents),
  `thinking-model-router` (frame selection).
