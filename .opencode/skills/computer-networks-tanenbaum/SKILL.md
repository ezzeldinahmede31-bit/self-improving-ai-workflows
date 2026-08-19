---
name: computer-networks-tanenbaum
description: Applies Tanenbaum's Computer Networks to the full protocol stack from the physical layer up: transmission media and encoding, link layer and Ethernet, the network layer and routing, transport and the TCP/UDP distinction, and the application layer with DNS and HTTP, plus security and network management. Use when the user says 'computer networks', 'protocol stack', 'OSI model', 'TCP/IP layers', 'routing', 'Ethernet', 'congestion control', 'DNS', 'Tanenbaum networks', 'network layers', or when a network design or protocol behavior must be understood end to end.
---

# Computer Networks (Andrew S. Tanenbaum)

Tanenbaum's networks text is the reference tour of the protocol stack. This skill applies that layered model to designing and debugging networked systems.

## The layered stack

- Each layer solves one class of problem and hands a clean interface upward; keep the layering explicit.
- Encapsulation means each layer adds its own header; the same bytes travel in different wrappers at different layers.
- Errors are handled at the layer that can detect and recover from them.

## The network layer

- Routing chooses paths; distance-vector and link-state protocols trade convergence speed against complexity.
- Addressing (IP) and forwarding are separate concerns; the routing table is the bridge.
- Subnetting and CIDR shape the addressing plan; design the plan before addresses are assigned.

## Transport

- TCP provides reliable, ordered byte streams with flow and congestion control; UDP provides datagrams with none.
- Congestion control (slow start, congestion avoidance) protects the network; it is the reason TCP behaves as it does.
- Choose the transport by the requirement: ordering and reliability versus low latency and low overhead.

## The application layer

- DNS maps names to addresses and is the first thing every request touches.
- HTTP is the application protocol of the web; caching, methods, and status codes shape behavior.
- Security (TLS, firewalls, VPNs) crosses every layer; apply it where the threat lives.

## Pairs with
tcp-ip-illustrated, computer-networking-top-down, tcpip-illustrated-implementation, high-performance-browser-networking, network-security-private-communication
