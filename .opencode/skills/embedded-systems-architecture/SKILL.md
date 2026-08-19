---
name: embedded-systems-architecture
description: Applies Tammy Noergaard's Embedded Systems Architecture to designing and programming embedded systems: the embedded development environment and toolchain, CPU and memory, devices and interrupts, and the embedded OS versus bare-metal decision, with real board-level practice. Use when the user says 'embedded systems', 'bare metal', 'embedded OS', 'RTOS', 'firmware', 'device driver embedded', 'interrupt handler', 'cross compiler', 'memory mapped I/O', 'Noergaard', or when writing software that runs on constrained hardware.
---

# Embedded Systems Architecture (Tammy Noergaard)

Embedded systems couple software directly to hardware constraints. This skill applies the embedded discipline: know the hardware, manage resources tightly, and treat every byte and tick as real.

## The embedded environment

- Embedded development crosses the host-target boundary: cross-compile, flash, and debug on the device.
- The toolchain, linker script, and startup code define where code and data live.
- On-target debugging (JTAG, serial, trace) is the reliable way to see the truth.

## CPU and memory

- The CPU and its peripherals are memory-mapped; device registers are read and written as addresses.
- The memory map is fixed by the SoC; the linker must honor it exactly.
- RAM and flash budgets are hard; choose data structures that fit the available memory.

## Devices and interrupts

- Interrupt handlers run with the main flow suspended; keep them short and defer the work.
- Polling is simpler and deterministic; interrupts scale better for rare, urgent events.
- Every device has a register contract; read the datasheet before writing the driver.

## OS versus bare metal

- A real-time OS gives scheduling, timers, and synchronization at the cost of footprint and jitter.
- Bare-metal code has full control but must implement everything itself.
- Match the choice to the deadline: hard real-time needs guarantees, soft real-time can tolerate scheduling.

## Pairs with
computer-organization-design, operating-systems-three-easy-pieces, real-time-systems-liu, c-programming-language, computer-system-architecture
