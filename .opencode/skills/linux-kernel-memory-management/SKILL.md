---
name: linux-kernel-memory-management
description: Applies the memory-management chapters of Robert Love's Linux Kernel Development to understand how the kernel manages physical and virtual memory: the page allocator, the slab allocator, page tables and the TLB, and the interactions with virtual memory and the page cache. Use when the user says 'how does the kernel allocate memory', 'page allocator', 'slab allocator', 'buddy system', 'page tables', 'TLB', 'high memory', 'kmalloc versus vmalloc', 'kernel memory', 'Robert Love', or when debugging memory behavior or sizing kernel memory.
---

# Linux Kernel Development: Memory Management

The kernel allocates memory through a layered set of allocators, each tuned for a different access pattern. Robert Love's Linux Kernel Development walks the hierarchy from the page allocator up through slab caches and into the virtual memory system. This skill encodes that model so memory behavior is explained and debugged correctly.

## The Page Allocator
- The kernel manages physical memory in pages, using a buddy system that splits and coalesces blocks in powers of two.
- The buddy allocator keeps external fragmentation low and makes allocation fast on the hot path.
- Each node and zone maintains its own lists; allocation requests specify the zone and the movement allowed for the requested page.
- The page allocator is the foundation — every other allocation path ends here.

## The Slab Allocator
- Small kernel objects (task structs, inodes, dentries) are allocated from slab caches, one cache per object type.
- Slabs are prebuilt per-CPU and reused, so frequent object create-and-destroy avoids the page allocator entirely.
- Cache coloring and per-CPU slabs keep the fast path lock-free and cache-friendly.
- When debugging memory growth, look at slab usage for the object type that grows without bound.

## Page Tables and the TLB
- Each process has its own page table mapping virtual to physical addresses; the TLB caches the translations that the hardware recently used.
- A TLB miss forces a page-table walk, which is why large pages and locality matter for performance.
- The kernel uses high memory and kmap for pages not permanently mapped, and the direct map for the bulk of physical memory.
- Changing page tables (fork, mmap, munmap) flushes TLB entries, so minimizing table churn improves throughput.

## kmalloc versus vmalloc and the Page Cache
- kmalloc gives physically contiguous memory from the slab/page allocator and is the right choice for most kernel buffers.
- vmalloc gives virtually contiguous memory backed by discontiguous physical pages, for large or rarely-touched buffers where physical contiguity is not required.
- The page cache holds file contents in memory; it is the largest consumer of kernel memory and the main reason read performance improves on repeat access.
- When reasoning about memory pressure, split the picture into anonymous memory, page cache, and slab — each responds to a different remedy.

## Pairs with
linux-kernel-development, understanding-linux-kernel, operating-systems-three-easy-pieces, systems-performance-profiling, computer-systems-programmers-perspective
