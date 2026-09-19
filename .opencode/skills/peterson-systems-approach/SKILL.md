---
name: peterson-systems-approach
description: "Builds networks as systems: layering, SDN, and end-to-end design. Use when the user says 'systems approach', 'SDN', 'OpenFlow', 'end-to-end principle', 'congestion control design', 'Peterson Davie', or when network architecture must be reasoned about, not just configured."
---

# Peterson Systems Approach to Networks

Distilled from Peterson & Davie *Computer Networks: A Systems Approach*:
networks are SYSTEMS — requirements drive architecture, and every mechanism
is judged by how the whole behaves. The end-to-end principle rules: put
function where the knowledge is.

## Purpose

Design and debug networks architecturally: from application requirements
down to the mechanism that satisfies them, with SDN as the modern control
story.

## The principles

1. **Requirements first.** Throughput, latency, loss, availability, security —
   quantified per application class (bulk transfer vs interactive vs real-time
   have OPPOSITE needs). No mechanism discussion before the requirements table.
2. **Layering as decomposition, not religion.** Each layer offers a service
   using the layer below; strict layering bends where performance demands
   (cross-layer hints for wireless/mobile). Judge a layer by its service
   contract, not its purity.
3. **End-to-end argument.** Reliability, security, and naming belong at the
   endpoints unless an in-network implementation is provably sufficient AND
   cheaper. Middleboxes that break end-to-end (NATs, transparent proxies)
   create the bugs you will debug for a decade — account for them explicitly.
4. **Congestion as control theory.** AIMD stability, fairness (max-min),
   router mechanisms (RED/ECN marking, fair queueing) vs endpoint adaptation.
   Design rule: signals must reach the sender faster than the oscillation
   period, or control becomes chaos.
5. **SDN: separate control from forwarding.** Centralized control plane
   computes, switches forward match-action tables (OpenFlow lineage, P4 for
   programmability). Wins: global optimization (traffic engineering),
   consistent policy. Costs: controller scale/failure domains, control-loop
   latency. Apply where the network is one admin domain with real
   optimization headroom (datacenter/WAN), not everywhere by fashion.

## Design protocol

Requirements table → end-to-end placement decisions → per-layer mechanisms
→ failure analysis (partition? controller loss? overload?) → measurement
plan (what proves each requirement holds).

## Verification

Network design ships with: quantified requirements, placement rationale per
function, congestion-control story with stability argument, SDN scope
justified (or explicitly rejected), and the measurement dashboard defined.
Mechanisms without requirements are hobbies.

## Pairs with

- `computer-networking-top-down` (protocol detail),
  `tcp-ip-illustrated` (TCP mechanics),
  `designing-event-driven-systems` (control/data separation),
  `sre-devops-automation` (operating networks).
