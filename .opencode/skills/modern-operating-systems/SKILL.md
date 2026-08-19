---
name: modern-operating-systems
description: Applies Tanenbaum's Modern Operating Systems to the design and operation of OS-level software: processes and threads, scheduling, memory management (paging, segmentation, virtual memory), file systems, input/output, deadlock, virtualization, and distributed systems, with the trade-offs each design makes. Use when the user says 'modern operating systems', 'processes and threads', 'scheduler', 'virtual memory', 'paging', 'file system design', 'deadlock', 'OS design', 'Tanenbaum', 'kernel', 'system calls', or when reasoning about how the operating system provides or constrains a service.
---

# Modern Operating Systems (Andrew S. Tanenbaum)

Tanenbaum explains what an operating system is for: multiplexing hardware safely and fairly. This skill applies those mechanisms to sizing, debugging, and designing systems software.

## Processes and threads

- A process owns resources; threads own execution. Use threads for parallelism within a process and processes for isolation.
- Context switches cost; the scheduler chooses the frequency at which to pay that cost.
- A thread is the right unit when sharing memory, a process when isolation matters more than speed.

## Memory management

- Virtual memory decouples address space from physical memory; paging is the mechanism, and the page table the map.
- Locality keeps the working set resident; thrashing is the symptom of a working set larger than memory.
- Choice of page size and replacement policy shapes performance; match them to the workload.

## File systems and I/O

- File systems trade durability, speed, and space; journaling and copy-on-write are the modern durability answers.
- I/O is layered: device drivers, buffering, and the system-call interface; know where the buffering happens.
- Asynchronous I/O overlaps computation with transfers; the event model beats blocking when latency is high.

## Deadlock and virtualization

- Deadlock requires hold-and-wait, no preemption, circular wait, and mutual exclusion; break one condition to prevent it.
- Consistent lock ordering and timeouts prevent the most common deadlocks.
- Virtualization multiplexes the hardware itself; the hypervisor makes the same trade-offs the OS makes.

## Pairs with
operating-systems-three-easy-pieces, operating-system-concepts, multiprocessor-concurrency, linux-programming-interface, systems-performance-profiling
