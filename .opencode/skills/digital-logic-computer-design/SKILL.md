---
name: digital-logic-computer-design
description: Applies Morris Mano's digital design and computer organization texts to the hardware foundations of computing: number systems, Boolean algebra, combinational and sequential logic, registers and counters, memory and the processor data path, and the organization that turns gates into a working computer. Use when the user says 'digital design', 'Boolean algebra', 'logic gates', 'flip flop', 'sequential logic', 'register', 'adder', 'decoder', 'computer organization', 'Mano', or when the gate-level truth behind hardware behavior matters.
---

# Digital Design and Computer Organization (M. Morris Mano)

Mano is the standard introduction from Boolean algebra to a working processor. This skill applies that bottom-up understanding to hardware-adjacent software and to building a mental model of the machine.

## Number systems and logic

- Binary, hexadecimal, and two's complement are the representation; every conversion must be exact.
- Boolean algebra simplifies logic; a simpler expression is a cheaper circuit.
- Karnaugh maps and algebraic identities find the minimal form.

## Combinational logic

- Gates combine into functions: adders, decoders, multiplexers, encoders; each has a truth table and a cost.
- Design from the required function, then choose gates that realize it.
- Verify the truth table before wiring; a gate-level error is invisible in simulation until it is too late.

## Sequential logic

- Flip-flops introduce state; registers hold values and counters step them.
- Clocks synchronize state changes; setup and hold constraints bound the clock speed.
- Finite state machines describe control; write the state diagram before the logic.

## Computer organization

- A processor is registers plus a datapath plus control that executes instructions.
- Memory hierarchy (registers, cache, main memory) hides latency with locality.
- Microinstructions and the instruction cycle are the machinery behind a program counter stepping through code.

## Pairs with
computer-organization-design, nand-to-tetris-elements-computing, computer-system-architecture, structured-computer-organization, inside-the-machine
