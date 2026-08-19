---
name: computer-networking-top-down
description: Applies Kurose & Ross' Computer Networking: A Top-Down Approach to the Internet stack as applications see it: application-layer protocols (HTTP, DNS, sockets), transport (TCP and UDP, reliable data transfer, congestion control), the network layer and IP, the link layer, and the security of the network, always grounded in the applications that use it. Use when the user says 'Kurose Ross', 'top down networking', 'HTTP', 'DNS', 'sockets', 'TCP congestion control', 'IP addressing', 'reliable data transfer', 'network security', or when a network behavior must be understood from the application's point of view.
---

# Computer Networking: A Top-Down Approach (Kurose & Ross)

Kurose & Ross starts from the applications and descends into the machinery they use. This skill applies that order of reasoning to network design and debugging.

## The application layer first

- Every network program is an application protocol over a transport; name the transport and the message format first.
- HTTP is request-response; keep-alive and caching shape its cost and latency.
- Sockets are the API; the choice of stream versus datagram determines reliability and ordering guarantees.

## Reliable transfer and TCP

- Reliable data transfer over an unreliable network needs sequencing, acknowledgments, and retransmission.
- TCP's congestion control adapts the send rate to the network; the sawtooth behavior is by design.
- Throughput and latency are the two quantities that matter; one connection's behavior depends on both.

## The network and link layers

- IP provides a best-effort, connectionless service over a hierarchy of routers.
- Routing protocols agree on paths; the forwarding table is what every packet consults.
- The link layer frames bits for the local wire; switches forward within a LAN, routers across networks.

## Network security

- Security spans the stack: TLS at the transport, IPSec at the network, WPA at the link.
- Threats follow the layers; the mitigation belongs at the layer where the attack operates.
- Verify the security of each hop; the chain is as strong as its weakest protocol.

## Pairs with
tcp-ip-illustrated, computer-networks-tanenbaum, high-performance-browser-networking, web-security-browser-internals, network-security-private-communication
