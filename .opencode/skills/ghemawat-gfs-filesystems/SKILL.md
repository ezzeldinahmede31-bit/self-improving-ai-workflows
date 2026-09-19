---
name: ghemawat-gfs-filesystems
description: "Stores exabytes across commodity machines: GFS/HDFS architecture and operations. Use when the user says 'distributed filesystem', 'GFS', 'HDFS', 'NameNode', 'chunkserver', 'replication', 'erasure coding', 'data locality', 'Ghemawat', or when blobs must survive machine deaths routinely."
---

# Ghemawat GFS Distributed Filesystems

Distilled from Ghemawat et al. *The Google File System* (SOSP'03) and the
HDFS lineage: assume failures are routine, optimize for huge sequential
access, and keep one metadata brain with many dumb chunkservers.

## Purpose

Store and serve massive files on unreliable hardware with predictable
performance — the pattern under HDFS, Colossus, and every data lake.

## The architecture (roles and contracts)

1. **Single master, many chunkservers.** Master holds NAMESPACE + chunk
   mapping (in RAM — metadata scale is the ceiling); chunkservers hold 64MB+
   chunks as plain Linux files. Clients ask the master WHERE, then talk data
   directly to chunkservers (control and data planes separated).
2. **Replication first, erasure later.** Default 3 replicas across failure
   domains (rack-aware placement); hot files get more. Erasure coding for
   cold data (space saving ~50%) with slower rebuild — tier by temperature.
3. **Append-optimized mutations.** Record appends (the GFS signature op):
   lease a primary per chunk, order mutations there, replicate in chain.
   Relaxed consistency that works: defined regions (successful appends land
   at-least-once in order) + checksums everywhere (detect corruption, re-
   replicate from good copies).
4. **Master resilience.** Operation log + checkpoints for fast recovery;
   shadow/mirrored masters for read scaling and failover; chunkserver
   heartbeats carry load + corruption reports (master re-replicates
   proactively). The master is the SPOF — engineer it like one (or shard
   the namespace: HDFS Federation / Colossus evolution).
5. **Locality scheduling.** Move COMPUTE to data (map tasks on replica
   hosts); rack-local before off-rack; straggler mitigation by speculative
   re-execution. Network is the bottleneck — design around it, not through it.

## Operations honesty

- Small files are poison (one metadata entry per file regardless of size) —
  bundle them (SequenceFiles, HAR, columnar formats).
- Rebalancing is continuous: decommission, disk failures, and hotspots all
  trigger re-replication; throttle it or it eats the cluster.
- Checksums on read AND in background scrubbing; silent corruption is the
  failure you never hear about.

## Verification

Storage design ships with: metadata RAM budget, replica/erasure policy per
temperature tier, append consistency statement, master failover story, and a
fault-injection test (kill chunkservers mid-write, verify checksums +
re-replication). Untested recovery = no recovery.

## Pairs with

- `petrov-lsm-storage-compaction` (what lives on the chunks),
  `fundamentals-of-data-engineering` (lakes on top),
  `streaming-systems` (compute-to-data), `sre-workbook-practices`
  (operating the cluster).
