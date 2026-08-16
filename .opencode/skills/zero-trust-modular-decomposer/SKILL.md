---
name: zero-trust-modular-decomposer
description: "Enforces strict modular architecture, breaking implementations into single-responsibility files (7-10 modules) with zero-trust isolation boundaries. Use whenever building or refactoring backend/security logic. Trigger phrases: 'build', 'refactor', 'implement feature', 'modularize', any non-trivial code task."
---

# ZERO-TRUST MODULAR DECOMPOSER SKILL

## DIRECTIVE
Reject single-file or monolithic implementations for complex tasks. Force a
strict Separation of Concerns (SoC) by decomposing the codebase into
dedicated, loosely-coupled modules.

## MODULARITY MANDATE
Every non-trivial backend/security request MUST be split into a structure
respecting these boundaries:

```
project_root/
├── core/
│   ├── engine.py          # Pure business logic (no auth or direct I/O)
│   └── state_machine.py   # State transitions & execution gates
├── security/
│   ├── auth_verifier.py   # Live token & HMAC verification
│   └── ssrf_guard.py      # Egress IP & network filtering
├── resilience/
│   ├── lockdown.py        # Emergency isolation & circuit breakers
│   └── rollback.py        # Failure recovery & transaction cleanup
├── audit/
│   └── audit_store.py     # Immutable logs & proof history
└── tests/
    ├── test_unit.py       # Core logic tests
    └── test_adversarial.py # Edge cases & attack payloads
```

The modules may be adapted to the project, but the 4 boundary layers (core /
security / resilience / audit) must survive.

## DECOMPOSITION RULES
- **Rule 1:** No single file shall exceed 200 lines of code.
- **Rule 2:** Security verification MUST live in a separate file from
  business logic execution.
- **Rule 3:** State mutations MUST be validated by a separate policy gate
  before execution.

## Local adaptation
This project maps onto the same boundaries: `feedback_loop.py` =
`security/auth_verifier` + `resilience/lockdown`, `auto_self_evolver.py` =
`core/engine` + `audit/audit_store`, `security_gate.py` =
`security/ssrf_guard`. When decomposing, keep this mapping so existing wiring
and the 269-test suite still pass (`venv/bin/python -m pytest`).