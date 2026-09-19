---
name: swebok-guide
description: "Maps any software engineering question to its SWEBOK knowledge area and the right specialist skill. Use when the user says 'SWEBOK', 'knowledge areas', 'which discipline covers', 'requirements vs design', 'software quality', 'engineering economics', 'professional practice', or when routing a software-engineering task to its home discipline."
---

# SWEBOK Guide Router

Distilled from the IEEE *SWEBOK Guide* (15 knowledge areas): software
engineering is not one discipline but fifteen, each with its own methods and
failure modes. This skill routes; the specialist skills execute.

## Purpose

Place any SE task in its knowledge area instantly, so the right methods (not
random habits) apply.

## The 15 areas → where they live here

1. **Requirements** → `wiegers-software-requirements`, `patton-story-mapping`
2. **Design** → `agent-arch-system-design`, `software-architecture-hard-parts`,
   `object-oriented-design`, `clements-views-beyond`
3. **Construction** → `clean-code`, `spinellis-code-reading`,
   `beck-implementation-patterns`, `pro-git`
4. **Testing** → `tdd-sandbox-proof-engine`, `xunit-test-patterns`,
   `goos-outside-in-tdd`, `test-smells-catalog`
5. **Maintenance** → `legacy-code-characterization`, `refactoring-improving-design`
6. **Configuration management** → `pro-git`, `continuous-delivery-pipeline`
7. **Engineering management** → `engineering-management-path`,
   `berkun-making-things-happen`, `mcconnell-software-estimation`
8. **Process** → `enterprise-agile-transformation`, `clean-agile`,
   `shape-up-basecamp`
9. **Models & methods** → `domain-driven-design-strategic`,
   `jackson-alloy-abstractions`, `fowler-analysis-patterns`
10. **Quality** → `enterprise-quality-audit-loop`, `verification-before-completion`
11. **Security** → `aumasson-serious-crypto`, `secure-software-lifecycle`
12. **Economics** → `thinking-opportunity-cost`, `demarco-bears-risk`
13. **Professional practice** → `tech-ethics-ip-privacy`, `clean-coder`,
    `weinberg-egoless-systems`
14. **Computing foundations** → the CS-degree skills (algorithms, OS,
    networks, theory)
15. **Mathematical foundations** → `strang-linear-algebra`, `think-stats`,
    `forallx-formal-logic`

## Routing rule

- Name the KA first, then load its skill(s). A task spanning areas gets one
  primary + named supports (never an unscoped "best practices" soup).
- If no listed skill fits, that is a library gap: record it via
  `gate_complaints.py` (SKILL_GAP) instead of improvising methods.

## Verification

Every routed task states its KA and the loaded skills up front. Unrouted
work is unowned work — stop and route before executing.

## Pairs with

- `compensatory-router` (the execution router), `clarify-before-execute`
  (task shaping), `tradeoff-and-postmortem-documenter` (decision records).
