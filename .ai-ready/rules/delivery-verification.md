# Deliver only what is proven (user rule #2)

Never hand over a workflow that has not actually RUN end-to-end with no
problems. Audit the user's original commands one-by-one with evidence:

    REQ -> evidence -> PASS/FAIL/PARTIAL

See `.opencode/skills/n8n-delivery-verification-gate/SKILL.md`. A workflow that
only "validates green" but was never executed is NOT done.
