---
name: c4-architecture-communication
description: "Communicate architecture so it lands: C4 diagrams, views-and-beyond docs, ADR records. Use when the user says 'ارسم المعمارية', 'document the architecture', 'C4 model', 'architecture diagram', 'ADR', 'views and beyond', 'present the design', or needs diagrams + docs that reviewers actually understand."
---

# C4 Architecture Communication

Distilled from Simon Brown *C4 Model + Software Architecture for Developers
Vol 2*, Clements et al *Documenting Software Architectures: Views and
Beyond*, arc42, Rozanski & Woods viewpoints, *97 Things Every Software
Architect* and *Presentation Patterns*. A design nobody can read is a
design nobody follows.

## Purpose

Produce the minimum documentation that makes a system buildable and
reviewable: one Context, one Container, Component diagrams only for the
risky parts, one Deployment view, ADRs for contested choices.

## The protocol

1. **C4 Context (1 diagram).** System + users + external dependencies.
   No tech inside the box. Audience: everyone. If a stakeholder cannot
   point at their box, redraw.
2. **C4 Container (1 diagram).** Apps, services, datastores, and the
   arrows that carry data. Label every arrow with protocol + payload,
   not just a line. Runtime topology pairs with
   `software-architecture-design`.
3. **C4 Component (only the risky container).** Never diagram all
   containers — depth follows risk (`system-design-production-blueprint`
   phase 5). Components = deployable-unit internals with contracts.
4. **Deployment view.** Where containers run, zones/regions, ingress,
   data residency. Pairs with `kubernetes-operations` /
   `practice-of-cloud-system-administration`.
5. **Views-and-beyond pack.** Module view (what builds on what),
   runtime view (sequence of the critical path), allocation view
   (code-to-team mapping — Conway check with `team-topologies`).
6. **ADRs.** One per contested decision: context, options with numbers,
   decision, consequences, reversible-or-not. Five lines minimum, five
   pages maximum. Pairs with `architecture-decision-framework`.
7. **Present it.** One message per diagram (Presentation Patterns):
   Context = why it exists, Container = how it runs, Component = where
   the risk lives, Deployment = what it costs to run.

## Diagram hygiene (automatic reject)

- Unlabeled arrows, boxes meaning different things at one level,
  framework logos instead of responsibilities, a legend nobody reads,
  detail that belongs one level down. Review with `architecture-review`.

## Verification

Docs ship with: Context + Container + (risky Components) + Deployment,
arrow labels with protocols, ADRs for every contested choice, one-line
message per diagram. No diagram without an audience named on it.

## Pairs with

- `system-design-production-blueprint` (the design being communicated),
  `software-architecture-design` (runtime topology),
  `architecture-decision-framework` (ADRs), `architecture-review`
  (hygiene gate), `tradeoff-and-postmortem-documenter` (record),
  `team-topologies` (allocation view).
