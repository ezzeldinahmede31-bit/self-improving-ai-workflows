# Research Report — demo URL shortener

## Project Goal
demo URL shortener

## Open Source Candidates
- shlink: https://github.com/shlinkio/shlink (license MIT, tests: True)
- YOURLS: https://github.com/YOURLS/YOURLS (license MIT, tests: True)
- kutt: https://github.com/thedevs-network/kutt (license MIT, tests: True)
- dub-oss: https://github.com/dubinc/dub (license AGPL-3.0, tests: True)

## Closed Source Candidates
- bitly: custom domains; team features and integrations

## Architecture Comparison
(see candidate arch fields + decisions below)

## Feature Comparison
(see candidate payloads in store)

## Community Feedback
- [repeated-pattern] Shlink has the most detailed analytics (https://selfhostwise.com/posts/self-hosted-link-shorteners-in-2026-shlink-vs-yourls-vs-kutt-complete-guide/)
- [repeated-pattern] Shlink has the most detailed analytics (https://homelabcompass.com/alternatives/self-hosted-url-shortener)
- [individual-opinion] Shlink has the most detailed analytics (https://lenkli.com/blog/url-shorteners/open-source-url-shorteners-compared)
- [documented-issue] YOURLS admin UI is dated (https://selfhosting.sh/best/url-shorteners/)
- [individual-opinion] YOURLS admin UI is dated (https://lenkli.com/blog/url-shorteners/open-source-url-shorteners-compared)
- [individual-opinion] Kutt development pace slowed in 2024-2025 (https://lenkli.com/blog/url-shorteners/open-source-url-shorteners-compared)
- [fact] Bitly free tier limited to 10 links/month (https://homelabcompass.com/alternatives/self-hosted-url-shortener)

## Repeated Complaints
- Shlink has the most detailed analytics (2 sources)

## Strengths Worth Adopting
- Adopt API-first design with visit analytics: converging independent reviews + repeated community praise
- Reuse shlink short-code approach: MIT + maintained + tests

## Weaknesses To Avoid
- admin-UI-only features: converging independent reviews + repeated community praise

## Reusable Components
- shlink: reusable (permissive license MIT)

## License Analysis
- shlink: ('ALLOW', 'permissive license MIT')
- YOURLS: ('ALLOW', 'permissive license MIT')
- kutt: ('ALLOW', 'permissive license MIT')
- dub-oss: ('REVIEW', 'copyleft/conditional license AGPL-3.0 needs human review')

## Security Considerations
Closed-source: behavior only. Reuse: permissive licenses only.

## Performance Considerations
Repeated complaints: 1 patterns.

## Recommended Architecture Changes
- Adopt API-first design with visit analytics (status: approved)
- Reuse shlink short-code approach (status: approved)

## Final Design Decisions
- [approved] Adopt API-first design with visit analytics: converging independent reviews + repeated community praise evidence=3
- [approved] Reuse shlink short-code approach: MIT + maintained + tests evidence=1

## Sources
- https://selfhosting.sh/best/url-shorteners/
- https://selfhostwise.com/posts/self-hosted-link-shorteners-in-2026-shlink-vs-yourls-vs-kutt-complete-guide/
- https://lenkli.com/blog/url-shorteners/open-source-url-shorteners-compared
- https://homelabcompass.com/alternatives/self-hosted-url-shortener
