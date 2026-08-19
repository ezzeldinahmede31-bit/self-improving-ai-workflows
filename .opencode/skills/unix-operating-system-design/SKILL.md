---
name: unix-operating-system-design
description: Applies Maurice Bach's The Design of the UNIX Operating System to understand and work with the classic Unix kernel: the file subsystem, process subsystem, system call interface, process control, scheduling, memory management with the page cache, and the layered structure that made Unix portable. Use when the user says 'Unix kernel design', 'Bach', 'file subsystem', 'process subsystem', 'inode', 'system call', 'Unix architecture', 'kernel internals', 'process table', 'buffer cache', or when the behavior of Unix systems programming needs the kernel's reasoning.
---

# The Design of the UNIX Operating System (Maurice J. Bach)

Bach is the canonical tour of the classic Unix kernel, where the ideas behind modern systems come from. This skill applies that internal model to systems programming and debugging.

## The layered kernel

- The kernel is two subsystems, file and process, joined by the system-call interface; trace any call across the layers.
- A system call crosses the user-kernel boundary; know where the boundary is and what changes there.
- The kernel is reentrant and handles interrupts; shared structures are protected by locks.

## Files and the inode

- An inode holds the file's metadata and the map to its blocks; everything about a file starts there.
- File descriptors are indices into a per-process table; dup and fork share the open file description.
- The buffer cache mediates block I/O; flush and sync behavior shapes durability.

## Processes and scheduling

- fork and exec split creation from loading; the child inherits the parent's address space copy.
- The scheduler and the run queue decide which process runs; priorities reflect interactive versus batch work.
- Every process has a table entry; leaking entries (zombies) wastes kernel resources.

## Memory and the page cache

- The kernel pages the address space and caches file pages; the same cache serves reads and writes.
- Layering: logical I/O through the file system, physical I/O through the device drivers.
- The classic design is the foundation; modern kernels extend it but keep the same contracts.

## Pairs with
linux-programming-interface, understanding-linux-kernel, operating-systems-three-easy-pieces, c-programming-language, apue-unix-programming
