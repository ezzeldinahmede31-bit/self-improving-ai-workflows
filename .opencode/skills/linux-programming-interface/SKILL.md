---
name: linux-programming-interface
description: Applies Michael Kerrisk's The Linux Programming Interface to systems programming on Linux: system calls and library functions, process creation and execution, memory allocation and mapping, signals, timers, threads and synchronization, sockets and network programming, and interprocess communication, with the full POSIX and Linux-specific behavior. Use when the user says 'Linux programming', 'system calls', 'mmap', 'pthreads', 'timers', 'signals', 'socket programming Linux', 'semaphores', 'Kerrisk', 'TLPI', 'Linux syscall', 'process exec', or when writing portable systems code that must handle the Linux API correctly.
---

# The Linux Programming Interface (Michael Kerrisk)

TLPI is the comprehensive reference for the Linux programming interface. This skill applies its emphasis on portability, error checking, and the distinction of syscalls versus library wrappers.

## Syscalls versus libraries

- Know whether you are calling a system call or a library function; the failure modes differ.
- Check errno and the return value on every call; the interface contract defines what each value means.
- Read the man page for the exact semantics and portability notes of each interface.

## Processes and memory

- fork and exec separate process creation from program replacement; use them with their stated semantics.
- mmap maps files or anonymous memory; pick MAP_SHARED versus MAP_PRIVATE by the sharing requirement.
- Track ownership of allocated memory; the book's rule is every allocation has one owner that frees it.

## Threads and synchronization

- pthreads give parallelism within one process; shared state must be protected by a declared mechanism.
- Mutexes, condition variables, and semaphores each fit a specific coordination pattern; choose the simplest correct one.
- Avoid deadlock by a consistent lock ordering documented in the design.

## Networking and IPC

- Sockets follow a fixed lifecycle: create, bind, listen, accept, read/write, close; handle each step's error.
- Choose stream (TCP) versus datagram (UDP) by the reliability and ordering requirements.
- Prefer the syscall whose semantics match the need (signalfd, eventfd, epoll) instead of emulating it.

## Pairs with
apue-unix-programming, operating-systems-three-easy-pieces, understanding-linux-kernel, tcp-ip-illustrated, code-execution-guided-swemaster
