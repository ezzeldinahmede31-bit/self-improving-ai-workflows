---
name: perlman-interconnections
description: "Designs robust bridging and routing: spanning trees, link-state, and self-stabilization. Use when the user says 'spanning tree', 'link-state routing', 'distance vector', 'TRILL', 'DECnet', 'Perlman', 'loops in bridged networks', or when packets must survive topology changes."
---

# Perlman Interconnections

Distilled from Radia Perlman's *Interconnections*: bridges and routers are
distributed algorithms with physical consequences — loops melt networks, so
correctness (self-stabilization, loop-freedom) outranks cleverness, always.

## Purpose

Build and troubleshoot L2/L3 interconnection that converges correctly after
any topology change — and understand WHY each protocol looks the way it does.

## The canon (each with its invariant)

1. **Spanning tree (STP/RSTP/MSTP).** Bridges flood unknowns; loops make
   floods eternal — so compute a loop-free tree: elect root, kill redundant
   ports (blocking), reconverge on change. Costs: convergence time (RSTP
   fixes STP's slowness via handshake), wasted links (all traffic on the
   tree). TRILL/SPB answer: route with link-state at L2 instead of pruning
   to a tree — know both, pick by scale.
2. **Distance vector (Bellman-Ford, RIP).** Tell neighbors your distances;
   unbounded metric growth is the failure mode; split horizon + poison reverse are
   bandages, not cures. Simple and small-diameter only — the protocol to
   outgrow, with full understanding of why.
3. **Link state (OSPF/IS-IS).** Flood topology, compute locally (Dijkstra):
   fast convergence, full map, hierarchical areas for scale (backbone +
   areas contain flooding). Design areas around failure domains and
   summarization points — area borders are where you think.
4. **Self-stabilization as requirement.** Every distributed algorithm here
   must converge from ANY state (reboot with garbage memory, corrupted
   packets, duplicated messages). Test by fault injection, not by happy-path
   demo: kill links, partition, duplicate, reorder — then watch convergence.
5. **Bridging vs routing judgment.** Bridge (plug-and-play, flat, flood-
   dependent) inside failure-contained domains; route (hierarchical,
   summmarized, policy-expressing) across them. VLANs stretch L2 with
   discipline; VXLAN/overlays carry L2 semantics across L3 fabrics when
   migration demands it.

## Troubleshooting order (loops first, always)

Storm symptoms → find the loop (spanning-tree state per port, expected root
vs actual) → fix redundancy design → then look at routing (flapping?
summarization leak? MTU black holes?). Nine meltdowns in ten are L2 loops
or their cousins.

## Verification

Network change ships with: topology map, protocol choice justified by scale,
convergence test results (link-kill + partition drills), loop-prevention
story. "It converged in the lab" without fault injection is untested.

## Pairs with

- `computer-networks-tanenbaum` (protocol detail),
  `peterson-systems-approach` (architecture),
  `sre-devops-automation` (operating fabrics),
  `thinking-five-whys-plus` (outage analysis).
