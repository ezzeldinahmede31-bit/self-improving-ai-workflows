---
name: mit-computation-structures
description: "Builds computers from gates to operating systems the 6.004 way: logic, FSMs, ISAs, pipelines, caches. Use when the user says 'computation structures', 'CMOS', 'finite state machine', 'ISA design', 'single-cycle CPU', 'pipelining hazards', 'cache coherence', 'virtual memory', '6.004', or when hardware behavior must be derived, not guessed."
---

# MIT Computation Structures

Distilled from MIT 6.004 (Ward/Halstead): a computer is abstractions all the
way down — each layer hiding the one below with a contract. Master the
contracts and you can reason across all of them.

## Purpose

Derive hardware behavior from first principles: from transistors to a
running program, naming each layer's contract and cost.

## The stack (each layer: contract + key mechanism + cost)

1. **Digital logic.** CMOS gates -> combinational logic (truth tables,
   multiplexers, decoders, adders); timing (setup/hold, critical path sets
   max clock). Then sequential: latches/flip-flops give STATE; registers +
   clock = synchronous discipline.
2. **Finite state machines.** Any controller is states + transitions + outputs
   (Mealy/Moore). Design method: state diagram -> encoding -> next-state
   logic -> output logic. Unused states get defined transitions (no mystery
   lockups).
3. **Instruction sets.** An ISA is the hardware/software contract: registers,
   addressing modes, instruction formats. RISC discipline: few simple
   instructions, load/store architecture, fixed encoding — compiler-friendly
   by design.
4. **Single-cycle to pipelined CPU.** Datapath + control for fetch/decode/
   execute/memory/writeback. Then pipeline it: throughput up, hazards appear
   (data: forward or stall; control: predict or flush; structural: duplicate
   or serialize). Hazard handling IS the pipeline design.
5. **Memory hierarchy.** Registers -> caches -> main -> disk: each level
   bigger/slower. Cache mechanics (lines, associativity, write policies);
   locality (temporal/spatial) is the only reason any of it works. Virtual
   memory: pages, TLBs, protection as a side effect of translation.
6. **Synchronization and I/O.** Interrupts, DMA, memory-mapped I/O;
   atomic primitives (test-and-set, LL/SC) as the seed of all concurrency
   control above.

## Design discipline

- Every optimization states its invariant (what stays correct) and its price
  (area, power, complexity, or latency elsewhere).
- Simulate before building: a waveform or trace beats an argument.
- Bottleneck thinking: clock = slowest stage; throughput = narrowest pipe.

## Verification

For any claim about performance or correctness: the layer it lives at, the
contract it relies on, and a concrete trace (cycle-level or miss-rate) that
shows it. Hand-waving across layers is rejected.

## Pairs with

- `digital-logic-computer-design` (gate depth),
  `computer-architecture-quantitative` (measurement),
  `computer-organization-design` (datapath detail),
  `multiprocessor-concurrency` (above the atomics).
