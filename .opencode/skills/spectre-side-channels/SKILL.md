---
name: spectre-side-channels
description: "Closes leaks through physics: timing, cache, speculation, and power. Use when the user says 'side channel', 'Spectre', 'Meltdown', 'cache timing', 'constant-time', 'speculative execution', 'power analysis', 'SGX attack', 'timing attack', or when secrets share hardware with adversaries."
---

# Spectre & Side-Channel Defense

Distilled from the Kocher/Spectre-Meltdown lineage and the constant-time
cryptography practice: software correctness means nothing if the HARDWARE
broadcasts secrets through timing, power, or speculation. Defend the
physical layer of abstraction too.

## Purpose

Eliminate secret-dependent observable behavior (time, cache, power, EM) in
security-critical code, and contain what cannot be eliminated.

## The leak taxonomy (recognize each shape)

1. **Timing.** Early exits, table lookups by secret index, variable-time
   arithmetic (division/modulo). Fix: constant-time algorithms (no secret-
   dependent branches/memory addresses), verified with timing harnesses
   (dudect-style statistics, not eyeballing).
2. **Cache.** Prime+Probe / Flush+Reload: attacker infers victim access
   patterns from cache timing. Fix: no secret-indexed tables (bitsliced/
   vectorized crypto), cache partitioning/isolation where available,
   constant-time code as the baseline.
3. **Speculation (Spectre v1/v2/v4, Meltdown).** CPU executes past bounds
   checks and leaks via cache. Fix: speculation barriers (lfence) at trust
   boundaries, retpoline/IBRS for branch-target injection, site isolation
   for cross-origin data, microcode + kernel page-table isolation kept
   current. Variant list changes yearly — track vendor guidance, don't
   memorize a fixed set.
4. **Power/EM.** Differential analysis extracts keys from power traces of
   naive implementations. Fix: masking (split secrets across shares),
   hiding (noise, shuffling), and hardware with DPA countermeasures for
   payment/smartcard-grade targets.
5. **Microarchitectural leftovers.** Port contention, TLB, MDS buffers
   (RIDL/Fallout/ZombieLoad): flush sensitive buffers on context switch at
   trust boundaries; keep hyperthreading risk assessment current (disable
   across mutually-untrusted tenants when the threat model says so).

## Engineering rules

- Crypto and secret-handling code is constant-time BY CONSTRUCTION and
  tested by measurement — "looks constant-time" has failed repeatedly
  (compiler optimizations reintroduce branches; verify the BINARY/behavior).
- Secrets never share speculative/physical domains with attacker code
  without a stated barrier: process isolation, site isolation, enclaves —
  each with its documented residual (Foreshadow-style enclave leaks are the
  reminder).
- Cloud tenancy: know your co-tenancy exposure; noisy-neighbor is the
  benign face of shared hardware.

## Verification

Side-channel review ships with: secret inventory, per-secret leak-surface
table (timing/cache/speculation/power), mitigations mapped per cell,
measurement evidence (timing harness results), and residual risks accepted
in writing. Unmeasured constant-time claims are rejected.

## Pairs with

- `aumasson-serious-crypto` (constant-time primitives),
  `secure-enclaves-confidential-computing-v2` (hardware isolation),
  `bpf-performance-tools` (measurement), `linux-kernel-scheduler`
  (context-switch behavior).
