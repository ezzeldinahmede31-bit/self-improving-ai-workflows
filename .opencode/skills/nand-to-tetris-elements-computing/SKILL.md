---
name: nand-to-tetris-elements-computing
description: Applies Nisan & Schocken's The Elements of Computing Systems (Nand to Tetris) to build a working computer from first principles: from NAND gates through Boolean logic and the ALU, to a CPU and RAM, a machine language, a virtual machine, a compiler for a high-level language, and finally the operating system running on it. Use when the user says 'nand to tetris', 'build a computer', 'elements of computing systems', 'ALU', 'hack computer', 'virtual machine', 'compiler', 'from gates to OS', 'Nisan Schocken', or when the full stack from hardware to software must be understood by building it.
---

# The Elements of Computing Systems (Nisan & Schocken)

Nand to Tetris proves you can build a complete, working computer from a single primitive. This skill applies that build-it-yourself discipline to understand every layer.

## From gates to a machine

- NAND alone can express every Boolean function; the ALU and memory are built from it hierarchically.
- Design each chip by specification, test it on the truth table, then compose it upward.
- The hardware platform defines the machine language that programs will speak.

## The CPU and memory

- The CPU fetches, decodes, and executes instructions; the program counter sequences them.
- Memory is registers, RAM, and the screen and keyboard maps; addresses select which.
- Every instruction is a contract linking the hardware and the assembler.

## The virtual machine and compiler

- A virtual machine abstracts the hardware; the compiler emits VM commands.
- The compiler translates high-level statements into VM operations with a clean stack discipline.
- Stack-based computation keeps the semantics simple and the implementation portable.

## The operating system on top

- The OS level adds memory management, I/O services, and the language runtime.
- Build each layer so the one above needs no knowledge of the one below.
- The finished machine runs the same program the highest level wrote; the whole ladder works as one.

## Pairs with
digital-logic-computer-design, structured-computer-organization, computer-organization-design, dragon-book-compilers, sicp-abstraction-and-interpretation
