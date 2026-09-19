# Foreign skills verdicts — concurrent session (Sep 19, 20:21+)

A sibling session is installing skills into `.opencode/skills/` concurrently.
Rule applied: ADOPT only genuinely new, high-quality skills (gates +
register; router_register is idempotent so double-registration is safe).
Everything else stays on disk UNREGISTERED and untouched — never move or
delete a live session's files. Revisit after coordinating with the user.

## Adopted by this session (16, all gates green + router + library)

python-backend-architecture-review, bach-session-exploratory,
adzic-specification-by-example, api-testing-contract-patterns,
chaos-resilience-practice, playwright-modern-automation,
performance-testing-k6-jmeter, selenium-enterprise-patterns,
ai-powered-testing-patterns, security-testing-owasp-fuzz,
osherove-unit-testing, graham-istqb-foundations,
compatibility-cross-testing, usability-testing-patterns,
accessibility-wcag-testing, localization-i18n-testing.

## Left in place, NOT adopted (14, reasons)

- system-design, scalability-distributed-systems, system-type-distributed:
  duplicate alex-xu-system-design / akf-scalability-cube /
  distributed-systems-concepts-design.
- system-type-event-driven: duplicate designing-event-driven-systems.
- architecture-decision-framework, tradeoff-analysis: duplicate
  architecture-tradeoff-analysis / agent-arch-system-design.
- architecture-review: covered by clements-views-beyond + code-review.
- c4-architecture-communication: duplicate clements + agent-arch-system-design.
- production-capacity-planning: covered by alex-xu + sre-workbook.
- web-scalability-startup-playbook: duplicate akf-scalability-cube.
- system-design-production-blueprint: duplicate alex-xu-system-design.
- systems-design-methodology, systems-design-review-methodology:
  harness-coupled (needs foreign agents/recipes system) — rewrite required,
  out of scope for silent adoption.
- architecture-primitives: covered by enterprise-integration-patterns.

Secrets scan on all: clean. If the sibling session registers any of the
left-alone list, that is its decision to reconcile with the user.
