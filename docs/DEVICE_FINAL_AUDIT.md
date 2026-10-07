# DEVICE_FINAL_AUDIT — final round evidence (2026-10-07)

## Verdict basis
- E2E T1-T25: 24 PASS / 0 FAIL / 1 BLOCKED (T4 browser-write: user-scope
  boundary, respected not bypassed) -> COWORK_GRADE.
- Redteam R1-R10: 10/10 (incl. 2 real bugs found+fixed this round: .env
  pattern gap, audit-log race).
- Health: READY 10/10. Perf: gate 0.05s, sandbox 0.05s, shot 0.37s.
- pytest: see regression run below (must stay 1123+3 green).

## Files
- New: device_audit.py, device_state.py, device_redteam.py, device_health.py,
  tests/test_device_platform.py, docs/{DEVICE_ARCHITECTURE,SECURITY_MODEL,
  THREAT_MODEL,RECOVERY_MODEL,OPERATIONS,COWORK_PARITY,FINAL_GAP_MATRIX,
  FINAL_GAP_MATRIX_BEFORE}.md
- Rewritten/hardened: device_permissions.py (v2), device_loop.py (v2),
  device_monitor.py (v2), device_cron.py (v2), device_symbols.py (v2),
  device_sandbox.py (net-off default + containment + gate), device_e2e.py
  (T1-T25), device_audit.py (flock), opencode.jsonc (native Ask-first block),
  claude-device-use SKILL.md (§6-§7).
- Artifacts: /tmp/opencode-device/{final_device_audit,final_security_report,
  final_e2e_report}.json + e2e_report.json + redteam_report.json.

## Bugs found and fixed this round (honest list)
1. Loop write_text[:0] TypeError -> consumed-token confusion (test caught).
2. cmd_log printed hash into loop JSON (stdout pollution).
3. Audit append race under concurrency (flock fix; T18 exposed it).
4. Cron selftest cross-run pollution (namespaced reset).
5. .env regex missed rt_secret.env (R1 exposed).
6. Pre-existing TaskScopedJITRAG ingest/query (prior round).

## Residual YELLOW (documented, not hidden)
Browser-write autonomy (boundary), full LSP (LSP-lite honest),
malicious-child adversarial test, full latency tables.
No RED. No known bypasses undocumented.
