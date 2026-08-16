---
name: tdd-sandbox-proof-engine
description: "Enforces Test-Driven Development (TDD) in a clean sandbox: code is only considered valid if companion unit tests pass 100% and the execution log is attached. Use whenever writing or changing any code. Trigger phrases: 'write code', 'implement', 'fix the bug', or any task that produces a function/module."
---

# TDD SANDBOX PROOF ENGINE

## DIRECTIVE
Code without executable test verification is considered a hallucination. Always
write unit tests FIRST or alongside the code and verify passing execution in a
clean sandbox.

## EXECUTION STEPS
1. **Write Specification & Tests:** Write modular tests covering normal flow,
   null inputs, and malformed data.
2. **Execute in Sandbox:** Run `pytest` / `jest` in a clean environment.
   (This project: `venv/bin/python -m pytest <new_test> -q`.)
3. **Refine Code:** Iterate on the implementation until test failure count = 0.
4. **Deliver Code + Test Suite:** Output code only alongside its verified test
   execution log (the actual `N passed` line, not "should pass").

## Verification contract
- Every delivered change includes the command used and its real output.
- If a test cannot run in this environment, say why instead of claiming success.
- Never paste "PASS" you did not observe; `run_probe`-style silent "ok" is a
  hallucination by definition.

## Local adaptation
This project uses `venv/bin/python -m pytest` (pytest.ini: `-m "not e2e"`).
Docker sandboxing is not required here — the venv plus the existing test suite
is the sandbox.