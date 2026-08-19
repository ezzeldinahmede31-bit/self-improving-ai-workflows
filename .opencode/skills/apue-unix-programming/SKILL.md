---
name: apue-unix-programming
description: Applies Stevens & Rago's APUE to real Unix/Linux system programming: file I/O and descriptors, files and directories, processes and environment, signals, terminal and advanced I/O, and interprocess communication including pipes, FIFOs, message queues, semaphores, shared memory, and sockets. Use when the user says 'Unix programming', 'file descriptors', 'process fork', 'signals', 'terminal I/O', 'poll select epoll', 'interprocess communication', 'pipes', 'shared memory', 'socket programming', 'APUE', 'Stevens', or when writing programs that talk directly to the operating system.
---

# Advanced Programming in the UNIX Environment (Stevens & Rago)

APUE is the definitive guide to the POSIX programming interface. This skill applies its discipline of checking every return value and handling every error path.

## File and descriptor discipline

- Every system call can fail; check the return value and handle the error before proceeding.
- Distinguish regular files from devices and descriptors; the operations differ even when the API looks uniform.
- Understand buffering and caching: reads and writes go through the kernel, and sync behavior varies by descriptor type.

## Processes and signals

- fork duplicates the process; know exactly which state is copied and which is shared.
- Signals are asynchronous; keep signal handlers tiny and set flags for the main flow to read.
- wait and waitpid reap children; ignoring them leaks zombie processes.

## Advanced and terminal I/O

- poll, select, and epoll multiplex many descriptors; choose by the number of descriptors and their activity pattern.
- Terminal I/O is line- or character-mode depending on termios settings; set the mode explicitly.
- Nonblocking I/O changes the error model: EAGAIN and EWOULDBLOCK are expected, not fatal.

## Interprocess communication

- Pipes and FIFOs are the simplest streams; message queues, semaphores, and shared memory add structure.
- Sockets are the general mechanism across hosts; always specify the family, type, and protocol explicitly.
- Pick the IPC to match the coupling: stream for producer-consumer, shared memory for bulk state, semaphores for mutual exclusion.

## Pairs with
linux-programming-interface, operating-systems-three-easy-pieces, c-programming-language, understanding-linux-kernel, code-execution-guided-swemaster
