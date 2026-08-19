---
name: network-security-private-communication
description: Applies Kaufman, Perlman & Speciner's Network Security to protect communication in the real world: the goals (confidentiality, integrity, authentication), the primitives (hashes, symmetric and public-key encryption, signatures), the key-exchange protocols (Diffie-Hellman, IKE), and the practical systems (SSL/TLS, IPsec, Kerberos, SSH) with their real failure modes. Use when the user says 'network security', 'encryption', 'hash', 'digital signature', 'Diffie Hellman', 'key exchange', 'TLS', 'IPsec', 'Kerberos', 'authentication protocol', 'Kaufman Perlman', or when designing or reviewing a security protocol.
---

# Network Security: Private Communication in a Public World (Kaufman, Perlman, Speciner)

This book teaches secure communication the way it really works, including the failure modes that compromise real protocols. This skill applies its threat-aware discipline to protocol and integration security.

## Security goals and primitives

- Name the goals first: confidentiality, integrity, and authentication; a protocol serves the goals it states.
- Hashes give integrity but not secrecy; encryption gives secrecy; signatures give authenticity; combine deliberately.
- Never design your own cryptographic primitive; choose vetted, standard ones.

## Key establishment

- Symmetric key exchange over an untrusted channel needs an established secret; Diffie-Hellman provides it with signatures to prevent impersonation.
- Public keys need a trust anchor (CA, out-of-band, TOFU); the anchor is the weakest point.
- Forward secrecy means a compromised long-term key does not reveal past sessions; prefer ephemeral keys.

## The real systems

- TLS provides channel security for web and API traffic; validate the certificate chain and the host name.
- IPsec secures the network layer; Kerberos provides ticket-based authentication in a realm.
- SSH authenticates hosts and users and encrypts the session; know which host key you accept.

## Failure modes

- Real protocols fail through implementation and configuration errors, not broken math.
- Downgrade, renegotiation, and padding-oracle attacks abuse protocol flexibility; disable what you do not need.
- Replay protection and freshness bounds are part of the design, not an afterthought.

## Pairs with
applied-cryptography-engineering, web-security-browser-internals, security-engineering-threat-modeling, tcp-ip-illustrated, security-and-hardening
