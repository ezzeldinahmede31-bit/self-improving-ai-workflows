# Marketplace Pass

Use this when buying or self-hosting source could plausibly beat OSS, SaaS, or custom build for speed, ownership, or cost.

## Gate

Before a final recommendation, explicitly record one outcome:

- `Marketplace checked`: search CodeCanyon/Envato Market at least once, include 2-5 plausible marketplace candidates when any exist, and explain why each is accepted, rejected, or left unverified.
- `Marketplace skipped`: state the concrete reason marketplace scripts do not fit this task.

Do not skip the pass for self-hosted apps, admin panels, AI chat/workflow tools, SaaS starters, dashboards, CRM, LMS, booking, ecommerce, chatbot widgets, automation modules, payment/subscription integrations, or reusable app modules that could plausibly be bought with source.

When the pass is required but expected to be low-fit, still do a quick pass. Likely rejection is not a reason to skip verification.

## Search Queries

- `<feature> CodeCanyon script REST API OAuth`
- `<feature> Envato Market <stack> script API`
- `<feature> PHP Laravel CodeCanyon API`
- `<feature> React Node CodeCanyon webhook`
- `<feature> WordPress plugin API OAuth Envato`

## Evaluate Marketplace Candidates

- Integration proof: documented REST/GraphQL API, webhooks, OAuth/OIDC/social login/SSO, embed/admin surfaces, or clear extension points. Do not infer these from screenshots.
- Source and customization: source access, framework/version, dependency age, install path, update workflow, ability to fork/patch, and whether critical code is encrypted or vendor-locked.
- Marketplace health: last update date, changelog quality, author history, sales/reviews/comments trend, support status, live demo quality, docs depth, and responsiveness to security/compatibility issues.
- License and usage fit: regular/extended license fit, SaaS/client/multi-tenant redistribution limits, update/support duration, renewal cost, and whether the user's intended deployment is allowed.
- Security posture: auth implementation, password/session handling, tenant isolation, file upload safety, dependency vulnerabilities, payment handling, and data export/backup path.

Treat marketplace scripts as serious candidates, not automatic winners. They are strongest when the user wants a common self-hosted workflow quickly and accepts source-level ownership.

Downgrade or reject marketplace scripts when APIs/auth/export are unverified, the framework is stale, customization would be extensive, the license is unclear, support/updates look weak, or purchase is required to verify a critical claim.

If purchase is required to verify a critical claim, classify confidence as `MEDIUM` or lower until verified.
