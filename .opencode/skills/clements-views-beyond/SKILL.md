---
name: clements-views-beyond
description: "Documents and evaluates architectures: views, beyond-views info, and ATAM tradeoffs. Use when the user says 'architecture documentation', 'Views and Beyond', '4+1 views', 'ATAM', 'architecture evaluation', 'quality attribute scenarios', 'Clements', or when an architecture must be understood, reviewed, or defended."
---

# Clements Views & Beyond

Distilled from Clements et al. *Documenting Software Architectures: Views
and Beyond* (with ATAM evaluation): document the architecture people need to
reason about quality attributes — no more (waste), no less (folklore).

## Purpose

Produce architecture documentation that lets strangers evaluate fitness for
purpose — and run the evaluation that proves or kills it.

## Document: views + beyond (the 3-step recipe)

1. **Choose views for the stakeholders.** Module views (what builds on
   what: decomposition, uses, layers) for developers; component-and-
   connector views (runtime: processes, data flow, deployment) for
   performance/reliability reasoning; allocation views (who builds/deploys
   where) for managers. Three view families cover nearly every question —
   pick per stakeholder, never "all views for completeness".
2. **Document each view completely.** Primary presentation (the diagram),
   element catalog (every box explained), context (external interfaces),
   variability (what can change and how), rationale (WHY this shape —
   the part everyone skips and every reviewer asks for), plus what the view
   deliberately omits.
3. **Add beyond-views info once.** System overview, mapping across views
   (same element, different views — reconciled), directory (find anything
   fast), glossary, and the decision log (ADR per significant choice with
   alternatives rejected and why).

## Evaluate: ATAM in one pass

- **Quality-attribute scenarios:** stimulus + environment + measurable
  response ("1000 concurrent checkouts, p99 under 2s"). No scenario, no
  evaluation — attributes without numbers are adjectives.
- **Utility tree:** prioritize scenarios (importance × difficulty); walk the
  architecture against the top ones.
- **Findings that matter:** sensitivity points (one decision affecting one
  attribute), tradeoff points (one decision pulling two attributes opposite
  ways — THE output of the method), risks (unresolved unknowns),
  non-risks (settled with evidence).

## Verification

Architecture package review: stakeholder-to-view coverage (every reader has
their view), rationale present per major decision, ATAM findings with
tradeoffs named and risks owned. Documentation nobody reads is inventory,
not architecture — validate by watching a newcomer answer questions from it.

## Pairs with

- `agent-arch-system-design` (design method), `tradeoff-and-postmortem-documenter`
  (decision records), `architecture-tradeoff-analysis` (tradeoff math),
  `n8n-autodoc-mermaid` (diagram generation).
