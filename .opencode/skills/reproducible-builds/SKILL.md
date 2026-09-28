---
name: reproducible-builds
description: "Reproducible builds skill (canonical digests, double-build comparison, volatile-key stripping). Use when a rebuild must prove identical output, when timestamps or random ids pollute artifacts, or when 'worked yesterday' needs an honest answer. Trigger phrases: 'rebuild check', 'deterministic artifact', 'digest compare', 'بناء متكرر'."
---

# Reproducible Builds (Same Inputs, Same Artifact)

Code: `reproducibility.py` (stdlib only). `canonical()` gives a
deterministic encoding; `digest()` its sha256; `strip_volatile()`
drops run ids/timestamps before comparison; `check_rebuild()` runs a
builder twice and reports reproducible true/false with the digest. A
builder embedding wall-clock time or unseeded randomness is reported
non-reproducible — the module reports the fact, never hides it.

## When to use

- Release pipelines: rebuild → digest compare → ship or stop.
- Flaky "changed with no code change" investigations.
- Golden artifacts: store digest beside the file, re-verify later.

## Verification

- `tests/test_p0b_prov_repro.py` reproducibility half green
  (determinism, nondeterminism trip, volatile stripping).
- Non-reproducible verdicts route to fix-the-builder, not to waivers.

## Pairs with

`provenance-lineage` (digest beside the chain), `supply-chain-security`
(sign the digest), `deploy-signoff-governance`, `build-gates-pipeline`.
