---
name: aumasson-serious-crypto
description: "Deploys cryptography correctly: modern primitives, key management, and failure modes. Use when the user says 'encrypt this', 'which cipher', 'AES-GCM', 'ChaCha20', 'password hashing', 'Argon2', 'key exchange', 'Ed25519', 'TLS', 'random token', 'Aumasson', 'Serious Cryptography', or when any secret, password, or ciphertext is involved."
---

# Aumasson Serious Cryptography

Distilled from Jean-Philippe Aumasson's *Serious Cryptography*: nearly all
crypto failures are usage failures — wrong primitive, bad randomness, or
leaked keys — not broken math. This skill makes the safe choice the default.

## Purpose

Select primitives and wire them so the common attacks (not the exotic ones)
are already defeated.

## The safe defaults (use these unless a standard forces otherwise)

1. **Threat model first.** Name attacker capabilities (network? disk? memory?
   side channels?) and what "break" means (read? forge? replay?). No threat
   model = no crypto design, only crypto decoration.
2. **Encryption: AEAD always.** AES-256-GCM or ChaCha20-Poly1305. Never raw
   CBC/ECB, never unauthenticated encryption — unauthenticated ciphertext is
   malleable by definition. Nonces: unique per key (counter or 96-bit random;
   never reuse with the same key). Keys: 256-bit from a CSPRNG or KDF.
3. **Hashing: SHA-256/SHA-512 or BLAKE2/BLAKE3.** Passwords are NOT hashed
   with these — use Argon2id (memory-hard) with per-password random salts;
   legacy only: bcrypt/scrypt with proper cost. Never MD5/SHA-1 for security.
4. **Key exchange: X25519 (ECDHE).** Ephemeral keys for forward secrecy;
   authenticate the exchange (signatures or pre-shared identity) or MITM wins.
5. **Signatures: Ed25519.** Deterministic, fast, misuse-resistant. Verify
   before trusting anything; check return values (a skipped verify = no
   signature at all).
6. **Randomness: the OS CSPRNG** (`getrandom`/`BCryptGenRandom`/equivalent).
   Never userspace PRNGs for keys/nonces/tokens. Seed once from the OS; don't
   "add entropy" yourself.
7. **Transport: TLS 1.2+ with certificate verification ON.** Most TLS bugs are
   disabled verification, outdated versions, or wrong hostname checks — verify
   all three explicitly.

## The failure checklist (audit any crypto code against this)

- Hardcoded keys/IVs/salts? Reused nonces? ECB mode? Custom cipher/protocol?
- Passwords hashed with fast hashes? Tokens predictable? Secrets in logs/errors?
- Verification return values ignored? Cert validation disabled "temporarily"?
- Keys with no rotation/revocation story? No AEAD on stored data?

## Verification

Every crypto decision cites: threat model, primitive + parameters, randomness
source, and key lifecycle. Any "custom" construction needs a written reason
why no standard primitive fits — the default answer is no.

## Pairs with

- `applied-cryptography-engineering` (Anderson-side theory),
  `security-and-hardening`/`security-review` (audit),
  `credential-secret-handling` (secret storage), `tls` via
  `network-security-private-communication`.
