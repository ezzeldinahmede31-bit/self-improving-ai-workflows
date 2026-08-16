# Existing App Audit

Use this when the skill is invoked inside an existing app without a narrow feature request, or when the user asks what custom code could be replaced by native stack features or maintained tools.

## Workflow

1. Detect the stack from manifests, lockfiles, Docker/Compose files, framework config, routes, DB/schema files, auth config, job/queue config, CI files, package imports, and deployment files.
2. Inventory custom-built capabilities, especially auth, billing, admin panels, CMS/content, search, file uploads, email/notifications, analytics, feature flags, chat, queues, scheduling, observability, permissions, CRUD scaffolding, webhooks, integrations, import/export, and AI tooling.
3. Classify each capability:
   - `Keep custom`: domain-specific, core differentiator, or already simpler than an integration.
   - `Check native`: likely covered by the current framework, SDK, platform, DB, hosting provider, or existing dependency.
   - `Research replacement`: table-stakes feature with meaningful maintenance/security/ops cost.
   - `Defer`: too little evidence or too risky to recommend without product constraints.
4. Research only the highest-leverage `Check native` and `Research replacement` items first.
5. Prefer current-stack/native solutions before adding new services or dependencies.
6. Produce an opportunity report, not a rewrite plan by default.

Do not suggest replacing every custom component. Prioritize places where existing solutions reduce ongoing maintenance, security exposure, operational burden, or non-differentiating product work.

## Evidence To Collect

- File paths and symbols showing custom implementation.
- Current dependencies that may already cover the need.
- External/native candidate links from primary sources.
- Confidence, migration effort, operational risk, and expected maintenance reduction.

## Report Shape

1. Stack detected: framework, runtime, DB, auth, hosting/deploy, key packages, and unknowns.
2. Opportunity table: current custom area, repo evidence, suggested native/tool alternative, confidence, effort (`S/M/L`), expected code removed or maintenance reduced, and risk.
3. Top recommendations: 1-3 items with the best effort-to-impact ratio.
4. Keep custom: areas that look domain-specific or cheaper to maintain as-is.
5. Research notes and source links for current external facts.
6. Minimal proof-of-concept plan for the first recommendation only.
