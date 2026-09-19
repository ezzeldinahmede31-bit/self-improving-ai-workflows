---
name: swim-gossip-membership
description: "Spreads information and tracks membership epidemically: gossip, SWIM, and anti-entropy. Use when the user says 'gossip protocol', 'membership', 'failure detection', 'SWIM', 'anti-entropy', 'epidemic broadcast', 'cluster membership', or when nodes must agree on who is alive without a master."
---

# SWIM Gossip & Membership

Distilled from the SWIM paper (Das et al.) and the epidemic-protocols
tradition (Demers et al.): rumors spread exponentially fast with constant
per-node cost — the scalable alternative to heartbeating everyone.

## Purpose

Build failure detection and state dissemination that stays cheap as the
cluster grows: O(1) work per node per round, detection in seconds.

## The mechanisms

1. **Gossip math.** Each round, each node contacts k random peers; infected
   set grows ~exponentially (like an epidemic) — full coverage in O(log n)
   rounds with O(1) messages per node. Fanout k=2..3 suffices; more is
   insurance, not speed.
2. **SWIM failure detection.** Probe a random member directly each period;
   on timeout, ask k random others to probe indirectly (distinguishes crashed
   target from a cut link to self). Suspect (not dead) on indirect failure —
   confirmation via gossip before marking faulty. Tunable knobs: probe
   period (detection speed) vs message load; suspicion timeout (false-
   positive rate).
3. **Dissemination piggybacked.** Membership updates (join/suspect/alive/
   dead) ride on probe/ack messages with versioning; infected-then-removed
   (bounded retransmit) keeps traffic flat. Anti-entropy (periodic full-state
   Merkle sync) heals whatever gossip missed — run it slowly in the
   background, always.
4. **Seed and join discipline.** New nodes join via seed list, get the
   membership snapshot, then gossip normally. Seeds are bootstrap only, never
   special afterward (no master in disguise). Network partitions heal by
   merge: version vectors decide, humans get paged on split-brain writes.

## Failure honesty

- Gossip gives probabilistic guarantees: "with high probability within T
  seconds", never deterministic. Safety-critical decisions need stronger
  primitives (consensus) on top.
- NAT/firewalls break random peering — plan relay/seed roles for hostile
  networks.
- Clock skew corrupts suspicion timeouts; use monotonic clocks for timing.

## Verification

Cluster design ships with: fanout, probe period, suspicion timeout with the
false-positive math shown, anti-entropy period, and a chaos test (kill N
nodes + partition, measure detection time and spurious suspicions). No chaos
test = unproven detector.

## Pairs with

- `shapiro-crdts` (what gets disseminated),
  `distributed-control-systems-design` (coordination),
  `monitoring-logging-alerting-distributed` (observing the cluster),
  `rate-limit-and-cost-guard` (message budgets).
