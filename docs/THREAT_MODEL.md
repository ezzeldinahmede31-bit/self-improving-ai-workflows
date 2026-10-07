# THREAT_MODEL — actors, surfaces, mitigations (tested in R1-R10, T14/T17)

## Actors
- Malicious webpage/file/PDF/issue/MCP result (prompt/command injection).
- Malicious/compromised subagent or skill (escalation attempt).
- Local attacker: symlink swaps, PATH hijack, state-file tampering, pid reuse.
- Network: SSRF to metadata/private IPs, DNS tricks, exfil uploads.

## Surfaces -> mitigations (each with a passing test)
| Surface | Mitigation | Test |
|---|---|---|
| Injected shell in content | gate DENY on rm/sudo/push-force/exfil patterns | R7, T14 |
| Chained commands (`; && \|`) | quote-aware split, worst-tier-wins | T12 |
| Symlink to secret | realpath secret check | R1 |
| Approval theft/replay | hash-bound single-use TTL tokens | R2-R4 |
| File swap post-approval | token binds command hash; loop re-gates at exec | R2 |
| Metadata/SSRF URLs | check_url: metadata DENY, private ASK | R5 |
| Secret in logs | redaction pre-write | T16 + audit selftest |
| Secret exfil pipe | exfil regex DENY | T17 |
| State tamper | hash chain verify detects; corrupt quarantine | T21, R8 |
| Concurrent double-exec | idempotency keys + done[] skip | R6, T18 |
| Oversized input DoS | caps (arg scan <5s on 5MB; file 1MB; hits 500) | R10 |
| Runaway agents | caps: 50 steps, deadlines, monitor/cron caps | T23 |

## Out of scope (stated, not hidden)
Kernel exploits, malicious MCP *server binary* (only results are gated),
human coercion, hardware attacks.
