# SECURITY_MODEL — enforceable rules (all tested, see redteam_report)

1. **Deny > Ask > Allow**, evaluated per-segment on quote-aware-split
   commands; worst tier wins. Unmatched Bash = ASK (no implicit allow).
2. **Normalization**: sudo rm, absolute-path rm, python rmtree, bash -c,
   ${IFS}, git push -f/--force/--force-with-lease, reset --hard, clean -fd,
   chmod 777, curl|sh, fork-bombs, .env-to-net pipes = DENY.
3. **Approvals are external**: plan JSON cannot self-approve. Tokens bind
   (session, step, command-hash), TTL 300-600s, single-use; replay/wrong-task/
   stale/mutated commands rejected.
4. **Pre-execution gating**: sandbox/monitor/cron/symbols/loop all call the
   gate BEFORE launch. Gate failure = no execution, ever.
5. **Sandbox default-deny**: net OFF, workdir contained (/tmp or project),
   policy pre-check, output capped, die-with-parent.
6. **Secrets**: secret-path denies across Read/Glob/Grep/Edit/Write with
   realpath resolution; audit log redacts keys/tokens/JWTs/cookies.
7. **Untrusted data is DATA**: web/file/MCP text flows only into gated tools;
   cannot alter policy, routing, approvals, or security mode (R-tests prove).
8. **Destructive ops**: never auto-retried, idempotency-keyed, pause on ASK.
9. **Fail-closed**: corrupt policy/state -> DENY/quarantine, never allow.

Limitations (explicit): no kernel MAC beyond bwrap; no eBPF egress meter
(URL gate covers metadata/private-IP); MCP transport trust = TLS only.

## Hardening round 2026-10-07 (additive, no boundary weakened)
10. **Durable state, same fail-closed semantics**: persistent root with
    checksums + schema envelope; corrupt/mismatched/future-schema -> quarantine
    + RuntimeError, never silent load. once() grants are atomic under one
    exclusive lock (bench-found race fixed: N racers -> exactly 1 grant).
11. **Sandbox depth**: child env sanitized (PATH/LANG/TZ only, HOME=workdir;
    no secret/LD_PRELOAD inheritance), pseudo-fs workdirs refused,
    symlink-resolving containment, prlimit AS 1GB + CPU 120s (NPROC cap
    omitted: breaks unprivileged userns on this kernel — documented, not
    silently missing), close_fds. bwrap REMAINS isolation, NOT a MAC boundary.
12. **MCP explicit trust** (scripts/mcp_trust.py + allowlist policy):
    unknown server DENY; new/pending server ASK; trusted server ALLOW only
    within granted capabilities/tools; new capability ASK (re-authorization);
    hostname/pin/expiry/revocation enforced; disabled server DENY.
    MCP RESULTS remain untrusted data -> verify-before-commit (ResultVerifier).
13. **Tool-result trust**: execute -> observe -> INDEPENDENTLY verify
    (file_exists/file_contains/exit/contains specs; ResultVerifier journal).
    Forged success claims fail verification, never commit.
14. **Secrets**: backup scrubs secret-shaped values to references (never raw);
    audit redacts pre-write; sweep test guards state/backups/audit.
