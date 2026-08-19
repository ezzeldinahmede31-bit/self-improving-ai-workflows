---
name: operating-system-concepts
description: Applies Silberschatz, Galvin & Gagne's Operating System Concepts (the 'dinosaur book') to the fundamentals and practice of operating systems: process and thread management, CPU scheduling, synchronization, deadlocks, memory management, virtual memory, file systems, I/O systems, and protection and security. Use when the user says 'operating system concepts', 'dinosaur book', 'process synchronization', 'semaphore', 'monitor', 'CPU scheduling', 'deadlock', 'page replacement', 'file system', 'Silberschatz', 'Galvin', or when a system-service decision must be grounded in OS fundamentals.
---

# Operating System Concepts (Silberschatz, Galvin, Gagne)

This is the standard text on OS concepts with working examples. This skill maps each concept to the practice of building and debugging system software.

## Processes and scheduling

- Model work as processes and threads with an explicit lifecycle: ready, running, blocked, terminated.
- Choose the scheduler by the goal: response time for interactive, throughput for batch, fairness for shared systems.
- Priorities and aging balance responsiveness with the risk of starvation; document the policy.

## Synchronization and deadlocks

- Critical sections protect shared state; the mechanism (mutex, semaphore, monitor) must match the access pattern.
- Prevent deadlock by ordering resources, or detect and recover; prevention is simpler than recovery.
- Test synchronization under contention: races hide until the schedule is unlucky.

## Memory and virtual memory

- Paging and segmentation organize address space; the page table is the map the MMU walks.
- Page replacement policies trade future behavior against cost; LRU-style policies fit most workloads.
- Keep the working set inside the resident set to avoid thrashing.

## Protection and file systems

- Protection is a matrix of subjects, objects, and rights; least privilege is the design rule.
- File systems must survive crashes; journaling and metadata discipline are the standard guarantees.
- Choose the file system by workload: many small files, large sequential files, or metadata-heavy directories.

## Pairs with
modern-operating-systems, operating-systems-three-easy-pieces, operating-systems-concepts, multiprocessor-concurrency, linux-programming-interface
