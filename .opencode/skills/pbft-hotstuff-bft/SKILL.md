---
name: pbft-hotstuff-bft
description: "Reaches agreement with adversaries present: BFT protocols from PBFT to HotStuff. Use when the user says 'Byzantine', 'PBFT', 'HotStuff', 'Tendermint', 'view change', 'quorum certificate', 'blockchain consensus', '33% fault tolerance', or when nodes may lie, not just crash."
---

# PBFT & HotStuff Byzantine Fault Tolerance

Distilled from Castro-Liskov *PBFT* (OSDI'99) and Yin et al. *HotStuff*
(PODC'19): crash tolerance needs 2f+1 replicas; Byzantine tolerance needs
3f+1 and signatures — because a liar can vote twice, so quorums must
overlap in an honest node.

## Purpose

Run state-machine replication that survives actively malicious participants,
and know exactly what each protocol generation costs.

## The core (PBFT, three phases + view changes)

1. **Quorum math.** n = 3f+1; every decision needs a quorum certificate of
   2f+1 matching signed messages. Any two quorums intersect in f+1 nodes ≥ 1
   honest — safety rests on that one honest overlap. Memorize: liar-proofing
   costs an extra f replicas over crash tolerance.
2. **Normal case: pre-prepare -> prepare -> commit.** Leader proposes with a
   sequence number; replicas broadcast prepare on matching proposals; on
   2f+1 prepares they broadcast commit; on 2f+1 commits they execute. Three
   all-to-all rounds = O(n²) messages — fine for small committees.
3. **View changes replace bad leaders.** Timeout without progress -> new view
   with collected certificates proving what may have committed; safety
   demands the new leader honor them (the subtle half of every BFT paper —
   review it line by line).
4. **HotStuff: linearize and pipeline.** Threshold signatures compress votes
   to O(n); three chained phases pipeline like a CPU (each block certifies
   its parent); rotating leaders give chain quality (fairness) for free.
   Modern BFT (Tendermint, LibraBFT) is HotStuff with local variations.
5. **Client finality rule.** A client trusts a result after f+1 matching
   replies (one of them guaranteed honest). Fewer replies = hope, not finality.

## Deployment honesty

- Partial synchrony assumed: safety always, liveness only when the network
  behaves (FLP applies to liars too). State the assumption or the proof is
  void.
- Key management IS the system: compromised keys = compromised replica;
  rotation and threshold signing belong in the design, not the appendix.
- Performance claims need the fault model attached (fast path with f=0
  faults says nothing about f faulty).

## Verification

Protocol review ships with: n/f/quorum numbers, phase diagram with message
complexity, view-change safety argument summarized, client finality rule,
and the synchrony assumption stated. Missing numbers = unreviewed.

## Pairs with

- `database-replication-consensus` (crash-tolerant counterpart),
  `herlihy-consensus-transactional-memory` (consensus theory),
  `applied-cryptography-engineering` (signatures, threshold crypto),
  `thinking-red-team` (adversarial review).
