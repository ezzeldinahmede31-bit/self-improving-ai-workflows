# KNOWN ISSUES — key-rotation security hardening (final audit)

Small, intentional trade-offs and leftovers from the last security round.
These are NOT bugs in the shipped behavior; they are documented decisions that
a future change may revisit.

## 1. RULES_HMAC_KEY still shares the `.env` file with the HITL token
The **operator secret** is now fully separated (own env var + dedicated 0600
`.operator/rotation_override.secret` file). The **rules HMAC key**
(`RULES_HMAC_KEY`, `auto_self_evolver.DEFAULT_HMAC_KEY_PATH`) still lives in the
project-root `.env` — the same file `hitl_gate.py` reads `HITL_SECURITY_TOKEN`
from. The two are different keys on different concerns, but a single-file
compromise leaks both fingerprints. Moving `RULES_HMAC_KEY` to its own 0600
file (like the operator secret) is a clean follow-up.

## 2. Unprovisioned operator secret = fail-closed release (by design)
If neither `ROTATION_OPERATOR_SECRET` env var nor
`.operator/rotation_override.secret` exists, `FeedbackLoop.operator_secret` is
`None` and `release_lockdown()` always returns `INVALID_OVERRIDE`. A lockdown
then cannot be lifted until an operator provisions the secret and restarts /
re-initializes the process. This is the safe default — a missing credential
must never fall back to the HITL token (that is exactly what this round fixed).
Operators must provision the secret once via `FeedbackLoop.set_operator_secret()`
or the env var.

## 3. Migration note: prior HITL-token-as-operator-secret deployments
Before this round, `SystemOrchestrator` passed `security_token` (the HITL
token) as `operator_secret`. Deployments that relied on that behavior will now
find `release_key_lockdown(HITL_TOKEN)` rejected until they provision a
separate operator secret. Intended, but worth a runbook note.

## 4. Lockdown reads depend on `rule_state.last_known_state()`
During a rate-limit lockdown, reads serve the last known GOOD audited snapshot
from `feedback.db` (so pre-incident rules keep enforcing) instead of the
on-disk `rules.json` (treated as attacker-tainted). If no `rule_state` snapshot
was ever recorded (nothing promoted yet), reads return `[]` during lockdown
even if the on-disk store is actually intact. Availability trade-off, chosen in
favor of never trusting a possibly-rotated store mid-incident.

## 5. Operator secret file is strict: 0600 regular file, no symlinks
`_load_operator_secret()` requires a regular file with mode exactly 0600 and
rejects symlinks. A legitimate setup that symlinked the secret file would
resolve to `None` (fail closed). Use a real file or the env var instead.
