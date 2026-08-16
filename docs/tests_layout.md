# Test Scope & Taxonomy

Honest answer to "ما نطاق الـ 130 اختبار؟" — this document names exactly what
each bucket proves and what it does NOT prove.

## Pyramid

| Layer | Where | Proves | Does NOT prove | Runs in CI? |
|-------|-------|--------|----------------|-------------|
| **Unit** | `tests/test_*.py` | Each module's logic in isolation (SQLite temp DBs, monkeypatched sockets/docker) | Nothing about n8n, networking, real tools | ✅ default `pytest` |
| **Integration (local)** | `tests/test_master_orchestrator.py`, `test_cognitive_modules.py`, `test_tool_gateway.py` | Modules wired together; MockRouter substitutes external APIs | Real remote services, real n8n graph execution | ✅ default |
| **Live E2E (optional)** | `tests/test_e2e_live_n8n.py` | Real n8n instance (null create → deploy → test trigger → cleanup) | — | ⏸️ pytest `-m e2e`, needs live n8n |

## What each file covers today

| File | # | Type |
|---|---|---|
| test_hitl_gate.py | 19 | Unit (state machine, tokens, expiry) |
| test_remote_adaptation.py | 23 | Unit+local-integration (MockRouter, backoff, quirk memory) |
| test_security_governance.py | 18 | Unit (SecurityGate, tiered pipeline) |
| test_verifier_engine.py | 15 | Unit (Security+Quality merge, retry loop) |
| test_master_orchestrator.py | 14 | Integration (full orchestrated task end-to-end locally) |
| test_cognitive_modules.py | 27 | Unit+integration (planner, red-team, sandbox, redactor) |
| test_tool_gateway.py | 14 | Unit (OSS adapters mocked) |
| test_production_hardening.py | 28 | Unit (metrics, failover, feedback, versions, cost, fuzzer) |

## The gap the pyramid exposes (and what closes it)

The 130 green tests prove the *decision pipeline* is deterministic on this
machine. They do **not** prove:

1. That a generated workflow body is valid for n8n 2.69.x (community nodes,
   credential ids, parameter enum drift).
2. That a real webhook trigger actually fires and data flows node→node.
3. That remote egress honors the MockRouter when a real external API is behind it.

**Solution added in this pass:**
- `tests/test_e2e_live_n8n.py` marked `@pytest.mark.e2e` — talks to the real
  instance at `EZZELDIN8N_URL` (or MCP), creates a throwaway workflow only if
  `RUN_LIVE_E2E=1`, deploys it, exercises it, then hard-deletes it.
- Normal `pytest` stays green (fast, hermetic, no n8n needed).
- `pytest -m e2e` (with `RUN_LIVE_E2E=1`) exercises the final kilometre.

Run both:

```bash
venv/bin/python -m pytest tests/ -m "not e2e"          # hermetic, 130+ tests
RUN_LIVE_E2E=1 venv/bin/python -m pytest tests/test_e2e_live_n8n.py -m e2e -s
```