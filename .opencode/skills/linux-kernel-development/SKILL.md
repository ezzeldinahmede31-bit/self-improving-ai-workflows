---
name: linux-kernel-development
description: Applies Robert Love's Linux Kernel Development to writing and understanding kernel code: kernel development basics and the coding style, process management, scheduling, system call design, kernel data structures, interrupts and bottom halves, synchronization and locking, timers, memory management, and the art of working on an existing large codebase. Use when the user says 'kernel development', 'write a system call', 'kernel module', 'bottom half', 'workqueue', 'RCU', 'kernel locking', 'kernel style', 'Robert Love', 'Linux kernel module', or when writing or reviewing code that runs in the kernel.
---

# Linux Kernel Development (Robert Love)

Love's book is the practical companion for people writing kernel code. This skill applies its discipline: follow the existing style, use the right mechanism, and never break the interface.

## Working inside the kernel

- The kernel has a strict coding style; follow it exactly because reviewers enforce it.
- Read the existing code for the subsystem before writing; the pattern to extend is already there.
- Kernel code runs with the whole machine at stake: one bug panics the system.

## Processes, scheduling, and syscalls

- Each task is a task_struct; scheduling policies choose which runnable task executes.
- A system call is the controlled entry point: define a clear API, validate all input, and return errno-style errors.
- Keep the critical path small; kernel code is measured in latency and overhead.

## Concurrency and bottom halves

- Interrupts preempt everything; defer work with bottom halves, tasklets, and workqueues.
- Choose the lock that matches the access: spinlocks for short sections, mutexes where blocking is allowed.
- RCU lets readers run without locking while writers publish new versions safely.

## Memory and timers

- Kernel memory is scarce and low-latency; use the allocator that matches the object size and lifetime.
- Timers and delay mechanisms have different precision and context; pick by the requirement.
- Never hold a lock across a sleep; the kernel will deadlock and the machine will hang.

## Pairs with
understanding-linux-kernel, linux-programming-interface, multiprocessor-concurrency, operating-systems-three-easy-pieces, code-execution-guided-swemaster
