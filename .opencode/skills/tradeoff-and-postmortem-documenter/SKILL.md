---
name: tradeoff-and-postmortem-documenter
description: "Auto-generates production-ready documentation, architecture rationale, design trade-offs, and an explicit KNOWN_ISSUES.md for every implementation. Use whenever code is delivered, reviewed, or a design decision is made. Trigger phrases: 'document', 'trade-offs', 'why did you...', 'known issues', 'postmortem', any delivery that should ship with a rationale."
---

# TRADEOFF & POSTMORTEM DOCUMENTER SKILL

## DIRECTIVE
Deliveries without architectural trade-off documentation are incomplete.
Explain the *why* behind design decisions, explicitly state accepted
trade-offs, and document known operational constraints.

## DOCUMENTATION DELIVERABLE FORMAT

Alongside the code delivery, automatically generate/update two structural
documents:

### A. Architectural Rationale (`ARCHITECTURE.md`)
- **Design Pattern:** Why this specific architecture was chosen.
- **Security Boundaries:** Explicit isolation limits and trust assumptions.
  - Example: the lockdown operator secret lives in its own `.operator/`
    folder and NEVER falls back to the HITL `.env` token.
- **Fail-Secure Mode:** How the system behaves under network partition or
  lockdown (keep serving the last known GOOD state; refuse writes).

### B. Known Issues & Trade-offs (`KNOWN_ISSUES.md`)
Record explicit trade-offs using this structure:
```markdown
# KNOWN ISSUES & DESIGN TRADE-OFFS

## 1. [Trade-off Name]
- **Context:** Why this situation occurs.
- **Accepted Trade-off:** What we compromised (e.g., Availability vs.
  Integrity).
- **Decision Rationale:** Why this was the correct engineering choice.
- **Mitigation:** How the system remains safe despite this constraint.
```

## Grounding rule
Documentation must cite live evidence, not claims: reference the exact
module/line or the test that proves the behavior (e.g., the 269-passing suite,
the lockdown reads tests, `/tmp/rotation_security_proof.py` results). If a
trade-off was chosen for a reason, that reason must be traceable to a real
artifact.

## Local adaptation
This project already ships `KNOWN_ISSUES.md` covering the rotation-gate
trade-offs (shared `.env` key, fail-closed operator secret, lockdown read
dependence on `last_known_state()`). When documenting new work, APPEND to that
file using the template's 4-field format instead of rewriting it.