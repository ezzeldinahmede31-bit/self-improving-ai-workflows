---
name: demarco-bears-risk
description: "Manages project risk explicitly: identification, quantification, and mitigation. Use when the user says 'risk management', 'risk register', 'mitigation plan', 'Waltzing with Bears', 'DeMarco risk', 'what could kill this project', or when a plan assumes everything goes right."
---

# DeMarco Waltzing with Bears

Distilled from DeMarco & Lister *Waltzing with Bears*: risk management is
project management for grown-ups — any plan without explicit risk handling
is a hope with a Gantt chart. Dance with the bears (name them) or get eaten
by them (unnamed).

## Purpose

Surface every project-killing risk early, price it, and buy it down
deliberately — so surprises become line items, not obituaries.

## The practice

1. **Identify by brainstorming fears.** Whole team, no judgment round: what
   keeps you up? Categories: requirements volatility, unfamiliar technology,
   staffing/skill gaps, external dependencies, schedule pressure itself.
   Risks nobody voices are risks nobody manages — anonymity option for the
   politically dangerous ones.
2. **Quantify: exposure = probability × impact.** Rough numbers beat precise
   silence: best/likely/worst impact in time and money. Rank by exposure;
   the top five get active management, the rest get watch-listing with trip
   wires. Re-rank monthly — risks age like fish.
3. **Mitigate four ways.** Avoid (drop the risky approach), transfer
   (contracts, insurance, vendors with SLAs), reduce (prototypes, spikes,
   phased delivery), accept with contingency (reserve budget/schedule owned
   explicitly — not hidden padding). Every top risk has a named owner and a
   next action with a date.
4. **Track visibly.** Risk register reviewed at every status meeting (new
   risks? retired? changed exposure?). Trip wires defined in advance ("if
   API delivery slips past X, we switch to plan B") — decisions pre-made
   beat panic later.
5. **Schedule risk explicitly.** Every estimate carries its uncertainty into
   the plan (see estimation skill); the project buffer is sized from summed
   exposures, not from optimism. A plan with no buffer has already spent its
   luck.

## Verification

Risk review delivers: ranked register with exposures, owners + next actions
on the top five, contingency reserves sized and visible, trip wires armed.
A risk first mentioned at the post-mortem was a process failure — log it as
one.

## Pairs with

- `mcconnell-software-estimation` (uncertainty quantification),
  `thinking-pre-mortem` (prospective hindsight),
  `risk-management-failure-mode-autonomous` (technical FMEA),
  `berkun-making-things-happen` (driving mitigations).
