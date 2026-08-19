---
name: computer-system-architecture
description: Applies Morris Mano's Computer System Architecture to the organization of a complete computer system: register transfer logic, basic computer organization and its instruction cycle, central processor design, microprogrammed control, and memory and I/O organization. Use when the user says 'computer system architecture', 'register transfer', 'instruction cycle', 'microprogrammed control', 'basic computer', 'memory organization', 'I/O organization', 'Mano architecture', or when the internal organization of a processor must be understood or taught.
---

# Computer System Architecture (M. Morris Mano)

Mano's architecture text builds a complete, small computer and explains every part. This skill applies that full-system view to reasoning about real processors.

## Register transfer

- Register transfer language describes data movement; every instruction is a sequence of transfers.
- The control unit sequences transfers with a clock; each microstep moves data through the datapath.
- Describe hardware behavior in transfer statements before implementing it.

## The instruction cycle

- Fetch, decode, execute: the cycle repeats for every instruction and drives the whole machine.
- The instruction format defines opcode and operand fields; the format is the interface to the ISA.
- Interrupts interrupt the cycle; the saved state makes resumption exact.

## Control design

- Hardwired control is fast but rigid; microprogrammed control is flexible and uniform.
- The control memory holds microinstructions; the sequencer steps through them.
- Design the control before the datapath; the two must agree on every transfer.

## Memory and I/O

- Memory organization includes the cache, main memory, and the address decode that maps them.
- I/O is programmed, interrupt-driven, or DMA; each trades CPU cost against throughput.
- The bus is the shared highway; arbitration decides who moves data when.

## Pairs with
digital-logic-computer-design, computer-organization-design, structured-computer-organization, nand-to-tetris-elements-computing, inside-the-machine
