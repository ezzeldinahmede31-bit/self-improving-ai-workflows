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
