---
name: health-probes
description: "Health probe skill (credential expiry windows, TCP dependency gates, synthetic runs with mandatory cleanup). Use before executions needing live dependencies, when a secret may expire silently, or when fake traffic must prove the path end-to-end. Trigger phrases: 'pre-flight health', 'credential expiry', 'synthetic probe', 'مسابر الصحة'."
---

# Health Probes (Know Before You Run)

Code: `health_probes.py` (stdlib only). `CredentialHealth` reports
ok/renew-soon/expired/unknown with days-left (undated = unknown,
never assumed). `DependencyHealth` TCP-probes endpoints; `gate()`
blocks dependents on any down host. `SyntheticProbes` runs
act→verify→cleanup with cleanup in a finally: uncleaned runs fail
loudly so fake traffic never pollutes production.

## Verification

- `tests/test_p1d_capacity_health.py` probes half green (windows,
  gate, synthetic clean/dirty, unregistered).
- No execution starts with down dependencies or expired credentials
  unacknowledged.

## Pairs with

`chaos-drills` (fault side), `deployment-controller` (probe source),
`secret-scanning-lifecycle-adapter`, `build-gates-pipeline`.
