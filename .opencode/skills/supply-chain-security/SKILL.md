---
name: supply-chain-security
description: "Supply-chain security skill (Python SBOM, lockfile verify, skill-hash verify, honest vuln-scan, artifact signing). Use when onboarding dependencies, verifying installed skills against the lockfile, or signing a build artifact. Trigger phrases: 'SBOM', 'verify lockfile', 'skill hash check', 'سلسلة التوريد'."
---

# Supply-Chain Security (SBOM + Verify + Sign)

Code: `supply_chain.py` (stdlib only, no network). Three checks plus
signing: `python_sbom()` enumerates live distributions (versions +
installer origin); `verify_lockfile()` compares a version lock with
reality; `verify_skill_hashes()` recomputes sha256 over skill files in
`skills-lock.json` (partial lock by design: unlisted = unknown, never
trusted); `vuln_scan()` runs pip-audit when present else reports SKIP
honestly; `sign_file()`/`verify_file_signature()` seal artifacts.

## When to use

- New dependency or skill onboarding; weekly scheduled sweeps.
- Any "is this install what we approved?" question.
- Release time: SBOM + signatures archived with the delivery.

## Verification

- `tests/test_p0b_supply.py` green (SBOM live, lock diff, tamper
  trap, unreadable lock, honest SKIP, sign roundtrip).
- Mismatches quarantine the artifact; unknowns stay untrusted.

## Pairs with

`skill-trust-registry` (per-skill identity), `secret-scanning-lifecycle-adapter`,
`build-gates-pipeline`, `deploy-signoff-governance`.
