# Recommendation Output

Use this before writing the final answer. Keep the decision first and the evidence compact.

## Decision Lead

Start with one of these:

- `Use <tool>` when one option is clearly best.
- `Prototype <tool A> and <tool B>` when uncertainty is mostly practical fit.
- `Use native <stack feature>` when the user's stack already solves it simply.
- `Build custom` only after explaining why existing options are not suitable.

## Standard Recommendation Shape

Include:

1. Short rationale in plain language.
2. Comparison table with the strongest options and a custom-build baseline, including confidence, effort, cost model, lock-in, source/license type, and source quality.
3. Integration sketch for the recommended path: auth, data flow, API/webhook/embed points when relevant, hosting, migration/export, and code the app still needs.
4. Rejected alternatives and why they failed must-have, confidence, cost, lock-in, or operational requirements.
5. Marketplace pass: `checked` or `skipped`, with accepted/rejected marketplace candidates or the concrete skip reason.
6. Risks and tradeoffs that could change the decision.
7. Minimal proof-of-concept plan with 2-5 concrete steps and explicit keep/discard criteria.
8. Source links used for current facts.

## Proof Of Concept Plan

For implementation-oriented requests, propose an atomic proof of concept:

1. Integrate or trial one candidate only.
2. Rewrite the smallest representative workflow.
3. Verify with tests, demo flow, or real sample data.
4. Keep the candidate only if verification passes; otherwise discard and restore the prior path.
5. Repeat for the next candidate only when needed.

## Existing App Audit Output

When running Existing App Audit Mode, use this shape instead:

1. Stack detected: framework, runtime, DB, auth, hosting/deploy, key packages, and unknowns.
2. Opportunity table: current custom area, repo evidence, suggested native/tool alternative, confidence, effort (`S/M/L`), expected code removed or maintenance reduced, and risk.
3. Top recommendations: 1-3 items with the best effort-to-impact ratio.
4. Keep custom: areas that look domain-specific or cheaper to maintain as-is.
5. Research notes and source links for current external facts.
6. Minimal proof-of-concept plan for the first recommendation only.

## Common Failure Patterns

- Starting with vendor demos or GitHub popularity before defining the need.
- Comparing tools without a custom-build baseline.
- Trusting search snippets, marketplace claims, live demos, reviews, or old blog posts without primary-source verification.
- Recommending OSS only because it exists, without checking maintenance, license, security, and API fit.
- Ignoring commercial script marketplaces when a table-stakes self-hosted app module could be bought with source and integrated faster.
- Recommending marketplace scripts without checking license fit, update/support posture, API/auth/export proof, framework age, and security implications.
- Recommending SaaS without checking data export, renewal/usage pricing, auth model, audit logs, and exit path.
- Replacing domain-specific product logic with a generic package that forces awkward workflows.
- Ignoring the cost of glue code, migrations, operational ownership, and support burden.
- Choosing the highest score when one low-scoring must-have should be disqualifying.
