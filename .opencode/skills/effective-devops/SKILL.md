---
name: effective-devops
description: Applies Davis and Daniels' Effective DevOps to build a humane, high-trust delivery culture: the four pillars (collaboration, affinity, tools, scaling) and the four ideals (measure, localize, standardize, automate). Treats DevOps as a cultural and organizational practice that runs on empathy and psychological safety, not just pipelines. Use when the user says 'adopt devops', 'fix our dev culture', or 'why is delivery so painful'.
---
# effective-devops

Davis and Daniels make the case that DevOps is a cultural movement whose outcome is shared ownership of software delivery. Tools matter, but trust, empathy, and visible work are what make a team actually ship. Use this skill to change how the team works, not just which tools it runs.

## Core principles
- DevOps is a sociotechnical practice: the people and the pipeline must improve together.
- Collaboration replaces handoffs; teams share responsibility for the whole lifecycle, not just their slice.
- Affinity means people trust each other enough to admit failure and learn in public.
- Tools should reduce friction and reveal work, never become the goal themselves.
- Scaling is achieved through standard ways of working that every team can adopt.
- Empathy is a professional skill: understand what the people downstream and upstream actually need.

## Key patterns
- The four ideals, applied in order: measure first, then localize (find where work slows), then standardize, then automate.
- Visible work: boards and dashboards that show flow, blockers, and progress so decisions use facts.
- Blameless learning: post-incident reviews that find causes and countermeasures, not culprits.
- Pairing and mentoring to spread knowledge and build affinity across specialties.
- Regular retrospectives that produce one concrete improvement each cycle.
- Cross-functional teams owning a product end to end, so no one throws work over a wall.

## Applying this to n8n/automation/code
- Treat the workflow library as the team's shared codebase: review changes, version them, and keep a shared style.
- Make every workflow visible: an inventory with owner, trigger, and dependencies so anyone can trace a job.
- Standardize the build steps (schema checks, gates, pinned data, tests) so every new workflow ships the same way.
- Use execution history as the measure: surface failures, retries, and silent drops in a shared dashboard.
- Run blameless reviews of failed executions and turn each root cause into a documented pattern.

## Hard rules
- Never let tooling run ahead of the people using it; adoption beats mandates.
- Never skip the measure step; automation built on unmeasured assumptions multiplies the problem.
- Always pair a change with a learning event (review, retro, or shared note) so the team grows.
- Never let a post-incident turn into blame; keep the focus on system causes.

## Pairs with
devops-handbook-flow, value-stream-mapping, high-output-management, staff-engineer-leadership, continuous-delivery-pipeline
