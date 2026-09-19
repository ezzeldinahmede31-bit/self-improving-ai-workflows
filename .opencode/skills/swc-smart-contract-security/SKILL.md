---
name: swc-smart-contract-security
description: "Audits smart contracts: reentrancy, access control, oracles, and upgrade safety. Use when the user says 'smart contract audit', 'reentrancy', 'SWC registry', 'flash loan', 'oracle manipulation', 'proxy upgrade', 'access control', 'DeFi hack', or when code directly controls money."
---

# SWC Smart Contract Security

Distilled from the SWC Registry, Trail of Bits/Consensys audit practice, and
the DeFi post-mortem canon: contracts are adversarial public code holding
money — audit like an attacker with the classics checklist open.

## Purpose

Ship contracts where every known bug class has been explicitly excluded, and
the remaining economic assumptions are written down.

## The bug classes (check every finding against this list first)

1. **Reentrancy (SWC-107).** External calls before state updates let
   attackers re-enter. Fix: checks-effects-interactions pattern, reentrancy
   guards, pull-payments over push. Test with a malicious-callee harness —
   every external call gets one.
2. **Access control (SWC-105/106).** Missing/wrong modifiers on sensitive
   functions (mint, pause, upgrade, withdraw). Enumerate every state-changing
   function × every role; unprotected = critical. Ownable is a start,
   role-based with timelocks is the finish.
3. **Arithmetic and precision.** Overflow (now checked by default in modern
   Solidity — verify the version), rounding direction in favor of the
   protocol (not the attacker), decimal scaling across tokens.
4. **Oracles and price feeds.** Single-source spot prices are manipulable
   (flash-loan attacks). Use TWAP/medianizers with staleness + deviation
   guards; define the circuit-breaker behavior BEFORE the incident.
5. **Upgradeability.** Proxy patterns (transparent/UUPS/diamond): storage
   layout compatibility across upgrades, initializer discipline (no
   uninitialized implementation), upgrade timelock + multisig. An upgradeable
   contract's security = current code + every future code — govern
   accordingly.
6. **Economic invariants.** The code can be "correct" and the protocol
   insolvent: collateral factors, liquidation incentives, slippage limits,
   sandwich/MEV exposure. State the invariant (e.g. "system always
   overcollateralized by x%") and the monitor that pages when it wobbles.

## Audit process (fixed order)

- Scope freeze + build clean (pinned deps, no warnings). Slither/static
  suite green. Manual line-by-line against the bug classes. Malicious-
  counterparty tests (reentrant callee, evil token with callbacks/fees,
  governance attacker). Economic review with the invariant list. Fix,
  re-audit the diff, publish the report with unresolved items explicit.

## Verification

Audit deliverable: scope, tool output, finding per bug-class checked (even
"not present" entries — absence of evidence recorded), malicious-harness
results, invariant monitors deployed. A clean report without the checklist
is an opinion, not an audit.

## Pairs with

- `aumasson-serious-crypto` (signatures, randomness),
  `groth-zk-proofs` (private/on-chain verification),
  `testing-qa-version-control-rpa-v2` (harness discipline),
  `thinking-red-team` (attacker mindset).
