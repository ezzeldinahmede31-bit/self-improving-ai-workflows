# Discovery Sources

Use this when broad candidate discovery is needed, obvious searches are not enough, or adoption/sentiment risk could change the recommendation.

## Source Roles

Treat sources by role, not as equal evidence:

- Primary sources validate recommendations: official docs, pricing pages, API docs, integration docs, changelogs, GitHub repos, package registries, Docker/package registries, marketplace item pages, license/support terms, security advisories, and vendor docs.
- Discovery sources find candidates: Product Hunt, AlternativeTo, SaaSHub, G2, Capterra, directories, curated lists, blog roundups, newsletters, and search result lists.
- Sentiment sources reveal risks: Reddit, Hacker News, GitHub issues/discussions, forum threads, review sites, comments, changelog gaps, and community complaints.

Do not recommend a candidate from discovery or sentiment sources alone. Use them to find names, categories, complaints, migration stories, pricing traps, support issues, lock-in concerns, or missing alternatives; then verify serious candidates from primary sources.

## When To Use Each Source

- Use Product Hunt to discover newer SaaS products, launch categories, adjacent workflows, and product names that exact-match search missed.
- Use Reddit for real-user complaints, alternatives, self-hosting pain, support quality, pricing changes, migration stories, and `why did you leave X` signals.
- Use Hacker News for devtools, infra, OSS, self-hosted tools, architecture tradeoffs, and technical maturity discussions.
- Use AlternativeTo and SaaSHub for quick alternative maps and category vocabulary.
- Use G2 and Capterra for B2B SaaS category discovery, common objections, review patterns, and buyer-language requirements.
- Use stack marketplaces when the project lives inside a platform: WordPress, Shopify, Slack, Salesforce, Chrome Web Store, VS Code Marketplace, AWS/GCP/Azure Marketplace, Atlassian Marketplace, Stripe Apps, Zapier, Make, and n8n community nodes.
- Use package/container registries for library/module discovery: npm, PyPI, Packagist, RubyGems, crates.io, Maven Central, NuGet, Docker Hub, GHCR, Helm charts, Terraform Registry, and Ansible Galaxy.

## Query Patterns

- `<feature> Product Hunt alternatives`
- `<feature> reddit alternatives self hosted`
- `<tool> reddit pricing support export lock-in`
- `<feature> Hacker News open source self hosted`
- `<tool A> vs <tool B> reddit Hacker News`
- `<feature> AlternativeTo SaaSHub`
- `<feature> G2 Capterra API SSO export`
- `<platform> marketplace <feature> API webhook OAuth`
- `<language/package-manager> <feature> library maintained`

## Verification Rules

- Verify API, webhooks, OAuth/OIDC/SAML, embeds, export, pricing, license, hosting, and support from primary sources before recommending.
- Treat Reddit/Hacker News/review-site claims as leads unless multiple recent independent reports point to the same risk.
- Check dates. Downgrade stale sentiment when product, pricing, or APIs changed afterward.
- Prefer recent primary-source changelogs over old community posts.
- Mention sentiment only when it materially affects risk, confidence, or the proof-of-concept plan.
