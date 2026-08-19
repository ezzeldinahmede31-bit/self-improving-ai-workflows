---
name: understanding-linux-kernel
description: Applies Bovet & Cesati's Understanding the Linux Kernel to the internals of Linux as it actually runs: kernel architecture and the role of interrupts, process and thread representation, process scheduling, memory addressing and allocation, the virtual filesystem and the page cache, and device drivers, with the 2.6-era structures that still shape today's kernel. Use when the user says 'Linux kernel internals', 'kernel architecture', 'task struct', 'process scheduling Linux', 'page allocation', 'slab', 'virtual filesystem', 'inode cache', 'kernel locking', 'Bovet Cesati', or when debugging or tuning kernel-adjacent behavior.
---

# Understanding the Linux Kernel (Bovet & Cesati)

This book reads the Linux kernel source as the authority and explains what each subsystem does. This skill applies that source-grounded view to systems work.

## Kernel architecture

- The kernel runs in a privileged mode with its own stack per process; interrupts and exceptions preempt normal flow.
- Most kernel work happens in process context; interrupts run in interrupt context with limited capabilities.
- Trace a request from the system call through the subsystems; the path is the truth.

## Processes and scheduling

- A task struct represents every execution context; threads share the task's resources.
- The scheduler and its classes choose the next runnable task; the policy determines latency and throughput.
- Signals and timers are delivered in process context; handle them where the kernel allows.

## Memory management

- The kernel manages physical pages with allocators and virtual ranges with the page table.
- The slab allocator serves kernel objects; the page cache serves file-backed pages.
- Tuning memory means knowing which pool a pressure signal applies to.

## The virtual filesystem

- The VFS abstracts every file system behind inode and dentry structures.
- The page cache accelerates reads and defers writes; the dirty page budget shapes write throughput.
- A file system is a set of operations on these structures; mount, lookup, and read follow the common path.

## Pairs with
linux-programming-interface, linux-kernel-development, operating-systems-three-easy-pieces, unix-operating-system-design, systems-performance-profiling
