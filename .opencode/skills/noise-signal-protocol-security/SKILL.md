---
name: noise-signal-protocol-security
description: "Designs and audits secure messaging: Noise handshakes, Double Ratchet, and formal verification. Use when the user says 'Signal protocol', 'Double Ratchet', 'Noise framework', 'X3DH', 'forward secrecy', 'post-compromise security', 'Tamarin', 'ProVerif', 'secure messaging', or when conversations must stay secret past key theft."
---

# Noise & Signal Protocol Security

Distilled from the Noise spec (Perrin), the Signal/X3DH/Double-Ratchet
papers (Marlinspike et al.), and the Tamarin/ProVerif verification
tradition: secure messaging = strong handshake + continuous key healing +
machine-checked proof.

## Purpose

Build or audit messaging that guarantees confidentiality, authenticity,
forward secrecy, and post-compromise recovery — with proofs, not promises.

## The stack (each layer's job)

1. **Noise handshake patterns.** Two parties, DH exchanges in named patterns
   (NN/NK/XK/IK/XX): static keys authenticate, ephemerals provide secrecy.
   Pattern choice = authentication-vs-anonymity trade stated up front.
   Handshake payloads encrypted as early as possible (psk support where a
   shared secret pre-exists).
2. **X3DH bootstraps async trust.** Prekeys published to a server let Alice
   talk to offline Bob: identity + signed prekey + one-time prekey combined
   in 4 DH operations. Server is untrusted for secrecy (only for availability)
   — verify this separation in review.
3. **Double Ratchet heals continuously.** DH ratchet (new ephemeral per
   round-trip: post-compromise security — a stolen key heals after one honest
   round trip) + symmetric ratchet (per-message keys from KDF chains: even a
   leaked message key exposes nothing else). Out-of-order tolerance via
   skipped-key storage (bounded — state the bound).
4. **Properties to demand.** Forward secrecy (past messages survive future
   compromise), post-compromise security (future messages survive past
   compromise after healing), deniability where required (OTR-style malleable
   transcripts vs Signal's practical trade-offs), sealed sender for metadata
   minimization.
5. **Verify formally.** Model the protocol in Tamarin or ProVerif: secrecy
   and authentication lemmas, adversary = Dolev-Yao network control. A
   handshake without a checked model is a sketch. Re-verify on EVERY change
   (protocol edits invalidate proofs silently).

## Audit checklist (run on any messaging design)

- Key lifecycle: generation (CSPRNG), storage (sealed enclave/second factor),
  rotation cadence, revocation story. No lifecycle = no security.
- Metadata: who-talks-to-whom, when, how much — minimized, padded, or
  accepted in writing.
- Group messaging: sender keys or pairwise sessions? Membership changes
  re-key? (Groups are where E2EE designs quietly weaken.)
- Backup/restore: encrypted backups reintroduce old keys — scope the
  secrecy claim across restores explicitly.

## Verification

Messaging review ships with: property table (claimed/proven per property),
Tamarin/ProVerif model + lemma results, key-lifecycle diagram, metadata
assessment, and the group-messaging caveat section. Unproven properties are
labeled aspirations.

## Pairs with

- `aumasson-serious-crypto` (primitives), `applied-cryptography-engineering`
  (theory), `formal-math-logic-verification-engine` (proof mechanics),
  `network-security-private-communication` (transport layer).
