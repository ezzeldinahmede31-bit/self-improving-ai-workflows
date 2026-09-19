---
name: roughgarden-game-theory
description: "Analyzes strategic systems: equilibria, incentives, and mechanisms. Use when the user says 'Nash equilibrium', 'price of anarchy', 'mechanism design', 'auction', 'incentive', 'truthful bidding', 'congestion game', 'selfish routing', 'VCG', 'Roughgarden', 'game theory', or when agents with their own objectives share a system."
---

# Roughgarden Algorithmic Game Theory

Distilled from Nisan/Roughgarden/Tardos/Vazirani's *Algorithmic Game Theory*
and Roughgarden's *Twenty Lectures*: think in equilibria first, optimize
second — the system will go to equilibrium whether you plan for it or not.

## Purpose

Predict where a multi-agent system settles and design rules so that the
settlement is good — for routing, auctions, pricing, matching, and protocol
design.

## Core toolkit

1. **Best response -> Nash equilibrium.** Each player maximizes own utility
   given others' strategies. An NE is a fixed point: nobody wants to deviate
   alone. Find it by iterated best response; mixed strategies (randomize)
   guarantee existence in finite games.
2. **Equilibrium quality: Price of Anarchy.** PoA = worst-NE welfare /
   optimal welfare. If PoA is near 1, selfishness is harmless — skip central
   control. If large, the system NEEDS coordination (tolls, caps, scheduling).
3. **Congestion / potential games.** When each player's cost depends only on
   When each player's cost depends only on the number of agents sharing
   the same resource, an exact potential function exists and
   best-response dynamics converge. Recognize this shape: it makes analysis
   easy and convergence free.
4. **Mechanism design (invert the game).** Instead of predicting behavior
   under fixed rules, DESIGN rules for desired behavior: dominant-strategy
   truthfulness (VCG: charge each player their externality), individual
   rationality (participation must beat opting out), budget balance. Gibbard-
   Satterthwaite warning: with 3+ outcomes, no rule is always truthful —
   restrict the domain (e.g. single-parameter) to get positive results.
5. **Auctions that work.** Second-price (Vickrey): bidding true value is
   dominant. First-price: shade bids by competition. Revenue equivalence:
   under standard assumptions the format doesn't matter — the INFORMATION
   structure does.

## Engineering translation

- Rate limits / quotas / backoff = mechanism design on APIs.
- Load balancing = congestion game; add latency-based costs to push PoA to 1.
- Any voting/feature-prioritization scheme: check strategy-proofness before
  trusting the outcome.

## Verification

State: players, strategies, payoffs, the equilibrium concept used, and the
efficiency claim (PoA bound or mechanism properties). No payoffs written down
= no game analyzed.

## Pairs with

- `thinking-second-order`/`thinking-in-systems-primer` (incentive effects),
  `clrs-np-completeness` (hardness of finding equilibria),
  `microservices-patterns` (distributed agents in practice).
