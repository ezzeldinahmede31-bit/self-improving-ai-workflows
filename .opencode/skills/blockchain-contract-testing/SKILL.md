---
name: blockchain-contract-testing
description: "Blockchain smart contract testing distilled. Use when testing contracts, invariants, fuzzing, reentrancy, gas bounds, upgrade safety."
---

# Blockchain Contract Testing

## Purpose

Test contracts like money depends on it: unit plus invariant plus fuzz, reentrancy and access control, gas bounds, upgrade safety.

## When to use

Use when the user says 'smart contract test', 'Solidity test', 'reentrancy', 'invariant test', 'Foundry fuzz', 'gas test', 'upgrade test'.

## Steps

1. Unit-test every external function with happy plus revert paths.
2. Assert invariants (conservation, access, pausing) across randomized call sequences.
3. Fuzz with stateful harnesses; triage every new crash path.
4. Test reentrancy guards and pull-payment patterns explicitly.
5. Bound gas per function; test upgrades preserve storage layout plus behavior.

## Anti-patterns

- Happy-path tests only on value-moving code.
- Invariants assumed instead of asserted under fuzz.
- Push payments to untrusted receivers.
- Upgrades deployed without storage-gap checks.

## Example

Foundry invariant sketch: `assert(token.totalSupply() == sum(balances))` held across handler sequences.

## Verification

Invariants fuzz-proven, reentrancy tested, gas bounded, upgrades storage-safe.

## Pairs-with

zeller-fuzzing-book, security-testing-owasp-fuzz, penetration-test-planning, formal-math-logic-verification-engine.
