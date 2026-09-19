---
name: architect-elevator-staff
description: "Lead architecture across all floors: executives, managers, engineers. Use when the user says 'convince management', 'architecture leadership', 'staff engineer', 'tech strategy', 'elevator', 'align stakeholders', 'architecture vision', or needs influence without authority and decisions that stick."
---

# Architect Elevator (Staff-Level Leadership)

Distilled from Hohpe *Software Architect Elevator* (ride the elevator:
boardroom to engine room), Larson *Staff Engineer*, Brown *Software
Architecture for Developers* (technical leadership), Fairbanks *Design
It!*, *12 Essential Skills for Software Architects*, *37 Things One
Architect Knows*. Architecture without influence is journaling.

## The protocol

1. **Ride the elevator.** Same decision in three languages: executive
   (money/risk/speed), manager (capacity/dependencies/dates),
   engineer (contracts/failure-modes/rollout). One message per floor —
   never carry engine-room detail to the boardroom.
2. **Advice as options, not orders.** Staff-level output = written
   options with trade-offs + a recommendation + reversibility note.
   Decisions get made by owners; your job is making the right one
   choosable. Pairs with `architecture-decision-framework`.
3. **Build the smallest coalition.** Find the engineer who feels the
   pain and the manager who owns the budget. A prototype that removes
   one real pain beats ten alignment meetings.
4. **Govern lightly.** Fitness functions over review boards
   (`fitness-function-engineering`): automate the invariants, discuss
   only the exceptions. Heavyweight governance gets routed around.
5. **Teach in public.** Design docs, tech talks, office hours. Every
   repeated explanation is a missing document — write it once, link
   it forever. Pairs with `c4-architecture-communication`.
6. **Track bets, not tasks.** Architecture roadmap = list of open bets
   with expiry dates. Revisit expired bets explicitly: double down or
   kill. Silent bets become legacy.

## Verification

Leadership ships with: per-floor messaging, written options + ADRs,
one automated fitness function per invariant, public teaching artifact,
bet list with expiries. Influence without artifacts = hallway talk.

## Pairs with

- `architecture-decision-framework` (ADRs),
  `c4-architecture-communication` (diagrams that land),
  `fitness-function-engineering` (automated governance),
  `team-topologies` (org shape), `staff-engineer-leadership`,
  `tradeoff-and-postmortem-documenter` (record).
