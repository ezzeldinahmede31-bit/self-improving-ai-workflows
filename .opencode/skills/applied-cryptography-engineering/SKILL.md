---
name: applied-cryptography-engineering
description: Applies the cryptography discipline of Security Engineering (Ross Anderson): use vetted schemes correctly — authenticated encryption, key generation and storage, random-number hygiene, and resistance to side channels — while never inventing or misconfiguring crypto. Covers threat models for keys and data at rest/in transit, and the audit questions that expose weak usage. Use when the user says 'encrypt this data', 'choose an encryption scheme', 'key management', 'random number generator', 'RNG', 'authenticated encryption', 'AES-GCM', 'side channel', 'timing attack', 'password hashing', 'key rotation', 'salt', 'nonce', 'crypto review', or when code must handle secrets, keys, or ciphertext safely. Pairs with: security-engineering-threat-modeling, security-and-hardening, web-security-browser-internals, build-gates-pipeline.
---

# Applied Cryptography Engineering

Transfers the cryptography discipline from Security Engineering (Ross Anderson) to code that handles secrets and ciphertext: use vetted primitives correctly, protect keys, and refuse the common misuse patterns that defeat otherwise-strong algorithms.

## When to use
- Choosing encryption, hashing, or key-derivation for a feature.
- Auditing existing crypto usage for common failures.
- Handling secrets, keys, or tokens in storage, transit, or logs.

## The usage rules
1. Never design or hand-roll a cipher, MAC, or key schedule; use a vetted library.
2. Prefer authenticated encryption (e.g. AES-GCM) so tampering is detectable; a bare cipher allows undetected modification.
3. Randomness: use the OS CSPRNG for keys, salts, and nonces; a predictable source makes any scheme breakable.
4. Password storage: use a memory-hard password-hashing function with a unique salt per account, never a fast hash.
5. Keys: separate key material from ciphertext, restrict access, and rotate on a schedule; a leaked key must be revocable.

## Side-channel awareness
- Constant-time comparisons for secrets (compare MACs and tokens with a constant-time primitive).
- Avoid secret-dependent branching and indexing that leak timing information.
- Document the threat model: what an attacker with read/write access could learn.

## The audit checklist
- Is a vetted primitive used, or something hand-made?
- Is encryption authenticated?
- Are keys random, protected, and rotatable?
- Is any secret ever logged, echoed, or committed?

## Pairs with
security-engineering-threat-modeling, security-and-hardening, web-security-browser-internals, build-gates-pipeline.