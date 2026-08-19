---
name: structured-computer-organization
description: Applies Tanenbaum's Structured Computer Organization to the multi-level view of computers: digital logic, microarchitecture and microprogramming, the instruction set level, the operating system machine, and assembly language, with the argument that a computer is a hierarchy of levels each implemented by the one below. Use when the user says 'structured computer organization', 'levels of abstraction computer', 'microarchitecture', 'microprogramming', 'instruction set level', 'assembly level', 'Tanenbaum structure', 'layered computer', or when explaining or designing the levels from gates to programs.
---

# Structured Computer Organization (Andrew S. Tanenbaum)

Tanenbaum argues a computer is best understood as a ladder of levels, each one implemented in the level below. This skill uses that ladder to reason at the right altitude.

## The level ladder

- Name the level you are working at (logic, microarchitecture, ISA, OS machine, assembly, high-level) and stay there.
- Each level is defined by its instruction set; the level below implements it.
- Moving down a level trades convenience for control; move down only when the problem requires it.

## Microarchitecture

- The microarchitecture implements the ISA with a datapath, control, and microinstructions.
- Microprogramming sequences the datapath; the microprogram is a program for the control store.
- Performance is decided here: pipelining, caching, and forwarding are microarchitecture choices.

## The instruction set level

- The ISA is the contract the OS and compilers see; it hides the microarchitecture below.
- CISC and RISC differ in instruction complexity and the amount of hardware versus software work.
- Every high-level construct lowers to a sequence of ISA instructions; the lowering is the cost.

## The OS machine and assembly

- The OS machine level adds system calls, virtual memory, and processes on top of the ISA.
- Assembly language is a symbolic ISA; every assembly line maps to one machine instruction.
- Structure your reasoning top-down and verify bottom-up: the program defines the stack, the stack defines the flow.

## Pairs with
computer-organization-design, computer-system-architecture, nand-to-tetris-elements-computing, operating-systems-three-easy-pieces, computer-systems-programmers-perspective
