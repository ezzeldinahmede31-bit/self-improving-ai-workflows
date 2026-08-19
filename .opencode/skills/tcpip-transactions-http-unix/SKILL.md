---
name: tcpip-transactions-http-unix
description: Applies Stevens' TCP/IP Illustrated Volume 3 to the specialized and application protocols around TCP: TCP for Transactions (T/TCP), the HTTP/1.0 protocol in detail, NNTP, and the UNIX domain protocol for local communication. Use when the user says 'T/TCP', 'transactional TCP', 'HTTP 1.0', 'NNTP', 'Unix domain socket', 'Stevens volume 3', 'local IPC socket', or when a specialized transport or application protocol needs precise understanding.
---

# TCP/IP Illustrated, Volume 3: TCP for Transactions, HTTP, NNTP, and the UNIX Domain Protocol (Stevens)

Volume 3 covers the protocols adjacent to the core stack, including local Unix-domain communication that every system service uses. This skill applies those specifics.

## T/TCP

- TCP for Transactions reduces the handshake cost for request-response patterns by carrying data in the handshake.
- The protocol trades a little safety for latency; know when the trade is worth it.
- Fast open-style optimizations in modern stacks revisit the same idea: save a round trip.

## HTTP in detail

- HTTP/1.0 defines the request line, headers, and body; every later version extends these primitives.
- Connection semantics (close versus keep-alive) dominate perceived latency on the web.
- Cache headers and methods define what a proxy may store and replay.

## UNIX domain protocols

- Unix domain sockets communicate within one host with no IP stack overhead.
- They support stream and datagram modes plus the special pathname-addressing scheme.
- Choose Unix domain sockets over TCP for local IPC: lower latency, no port allocation.

## NNTP and the family

- NNTP moves news articles over TCP; it is the ancestor of many modern subscription protocols.
- Each application protocol follows the same shape: greeting, commands, responses, and connection management.

## Pairs with
tcpip-illustrated-implementation, tcp-ip-illustrated, high-performance-browser-networking, linux-programming-interface, webhook-automation
