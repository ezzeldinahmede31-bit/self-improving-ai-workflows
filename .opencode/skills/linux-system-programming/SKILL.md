---
name: linux-system-programming
description: Applies Linux System Programming (Robert Love) to performance-conscious Linux code and automation: a fast, practical tour of the syscall interface, file I/O, buffered I/O, process management, IPC, and threads, with the performance trade-offs spelled out. Covers read/write and the stdio layer, scatter/gather and epoll, fork/exec, pipes, sockets, and pthread basics. Use when the user says 'buffered or unbuffered', 'why is file I/O slow', 'use epoll', 'scatter gather', or 'write a fast Linux utility'.
---
# linux-system-programming

Robert Love condenses how Linux system programming really works in practice, with attention to performance and the choices a programmer makes every day.
Use this skill when automation code touches files, processes, or threads and must run fast and predictably.
It is the pragmatic middle ground: enough syscall depth to write correct, fast Linux code without the full reference.

## Core principles
- The syscall layer is the truth; stdio buffering sits above it and changes behavior and speed.
- File I/O performance is dominated by buffer sizes, syscall overhead, and how well access patterns match the page cache.
- A process is fork followed by exec; the intermediate state is fully yours.
- IPC is a ladder of choices, from pipes through sockets to shared memory, each with a cost profile.
- Threads share an address space, so data races are possible without locking.
- A slow program usually signals a wrong data structure or access pattern, not a missing optimization.

## Key patterns
- Choosing syscall-based versus stdio-based I/O for the access pattern.
- Looping over partial reads and writes until completion.
- poll and epoll for multiplexing many descriptors without threads.
- Fork plus exec with controlled file-descriptor inheritance.
- pthread create/join with explicit mutex usage for worker parallelism.
- Scatter/gather I/O for moving many buffers in one call.

## Applying this to scripting/automation/code
- Pick buffered I/O for line-oriented log processing and unbuffered paths for high-throughput binary transfers.
- Use large read buffers in pipeline scripts to cut syscall overhead dramatically.
- Use subprocess with close_fds or preexec options to shape descriptor inheritance in Python wrappers.
- Multiplex webhook and long-poll handles with selectors instead of one thread each.
- Bound worker thread pools in n8n Code nodes and treat shared state as needing a lock.
- Prefer a few large reads over many tiny ones in every data path.

## Hard rules
- Never call write once and assume the full payload moved.
- Never mix buffered and unbuffered access on the same descriptor without flushing.
- Never spawn an unbounded thread per connection.
- Never forget that fork duplicates the whole address space.
- Never read or write a descriptor after closing it.
- Never assume a socket is ready because a poll returned; re-check the event mask.

## Pairs with
operating-systems-three-easy-pieces, computer-systems-programmers-perspective, systems-performance-profiling, code-execution-guided-swemaster, n8n-code-nodes-official
