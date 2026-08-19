---
name: tcpip-illustrated-implementation
description: Applies Wright & Stevens' TCP/IP Illustrated Volume 2 to the actual implementation of the BSD protocol stack: mbufs, interface layer, IP and ICMP processing, ARP, routing, and the TCP state machine with its timers, sequence handling, and the details that make the stack correct. Use when the user says 'TCP/IP implementation', 'mbuf', 'TCP state machine', 'IP processing', 'ARP cache', 'routing table BSD', 'TCP timer', 'Wright Stevens', 'BSD stack', or when the internals of the protocol stack explain a network behavior.
---

# TCP/IP Illustrated, Volume 2: The Implementation (Wright & Stevens)

Volume 2 is the source-grounded tour of a real TCP/IP stack. This skill applies its implementation detail to diagnosing and designing networked systems.

## Buffers and the interface

- The stack passes data in buffers (mbufs) that carry the packet and its metadata.
- The interface layer is the boundary to the device; drivers fill and drain the queue.
- Buffer ownership and the free list are the core bookkeeping; leaks and double-frees are the classic bugs.

## IP and ICMP

- IP is a best-effort forwarding service; every packet is a header plus payload that routers may drop.
- ICMP reports errors and diagnostics; many behaviors (unreachable, redirect, timeout) come from ICMP.
- Fragmentation and reassembly are the cost of path MTU differences; keep the message small enough to avoid them.

## ARP and routing

- ARP maps addresses to link-layer addresses on a shared wire; the cache is the fast path.
- The routing table selects the next hop; longest-prefix match is the selection rule.
- The kernel chooses the route, then ARP resolves the neighbor; both must agree for delivery.

## The TCP state machine

- TCP is a state machine: listen, syn-sent, established, close-wait, and the rest; every transition has a cause.
- Timers (retransmit, persist, keepalive, time-wait) drive reliability and recovery.
- Sequence and acknowledgment handling is exact; off-by-one here corrupts the byte stream.

## Pairs with
tcp-ip-illustrated, computer-networks-tanenbaum, tcpip-transactions-http-unix, linux-programming-interface, systems-performance-profiling
