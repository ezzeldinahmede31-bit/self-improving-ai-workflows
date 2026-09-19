---
name: groth-zk-proofs
description: "Proves statements without revealing secrets: SNARKs, commitments, and circuits. Use when the user says 'zero-knowledge', 'zk-SNARK', 'zk-STARK', 'Groth16', 'PLONK', 'commitment scheme', 'trusted setup', 'circuit', 'private transactions', 'selective disclosure', or when verification must not imply revelation."
---

# Groth Zero-Knowledge Proofs

Distilled from Groth'16, the PLONK/Halo line, and applied ZK practice
(Zcash, Semaphore, identity): prove "I know x such that P(x)" while x stays
secret — with succinct verifiers that make blockchains and credentials work.

## Purpose

Add privacy-preserving verifiability: age/identity/membership/solvency proven
on-chain or to a verifier, secrets never leaving the prover.

## The toolkit (use in this order of practicality)

1. **Commitments first.** Pedersen/hash commitments (hiding + binding) solve
   half of all "private X" problems without any proof system: commit now,
   reveal selectively later. Reach for full ZK only when the verifier must be
   convinced of a PROPERTY, not just a value.
2. **SNARKs that ship.** Groth16 (tiny proofs, per-circuit trusted setup),
   PLONK (universal setup, flexible), Halo2 (no trusted setup via recursion),
   STARKs (transparent setup, larger proofs, quantum-friendlier). Choice =
   setup ceremony tolerance × proof size × prover time × audit maturity.
3. **Circuits are programs with constraints.** Write the statement as an
   arithmetic circuit (R1CS/Plonkish): every wire justified, range checks
   explicit (under-constrained circuits are THE bug class — missing booleanity
   checks have drained real funds). Reuse audited gadgets ( Poseidon hashes,
   EdDSA verify, Merkle proofs) instead of hand-rolling.
4. **Trusted setup done right.** Per-circuit MPC ceremonies (many
   participants, one honest suffices) or transparent systems to skip the
   ceremony. Toxic waste handling documented; ceremony transcript published.
   "Trust us" setups are rejected.
5. **Nullifiers and identity patterns.** Nullifier hashes prevent double-spend/
   double-signal while preserving anonymity (Semaphore pattern). Selective
   disclosure credentials: prove predicates (age ≥ 18, member of set) from
   issued attributes without showing the attributes.

## The bug classes (audit every circuit for these)

- Under-constrained wires (prover can lie). Missing range checks. Mismatched
  field arithmetic vs intended integer semantics. Trusted-setup reuse across
  different circuits. Proof malleability where non-malleability is assumed.

## Verification

ZK review ships with: statement formalized, system choice justified
(setup/proof/prover trade table), constraint audit (every wire justified),
ceremony evidence or transparency argument, and a malicious-prover test
(forged witness must FAIL verification). Untested soundness is theater.

## Pairs with

- `applied-cryptography-engineering` (primitives beneath),
  `aumasson-serious-crypto` (hash/commitment choices),
  `formal-math-logic-verification-engine` (constraint reasoning),
  `swc-smart-contract-security` (on-chain verification).
