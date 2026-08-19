---
name: software-engineering-at-google
description: Applies Winters, Manshreck, and Wright's Software Engineering at Google to sustain code at scale: software engineering is programming integrated over time by many people, so readability, testing, code review, and deprecation are core skills. Covers the test pyramid, Hyrum's Law, change management, and keeping large codebases healthy. Use when the user says 'keep this codebase healthy', 'what is good code review', or 'how do we maintain code at scale'.
---
# software-engineering-at-google

The Google SRE-adjacent classic distinguishes programming (getting a program to work now) from software engineering (programming that many people will change for years). Use this skill to design automation and code that survives scale, time, and a rotating team of owners.

## Core principles
- Time, scale, and tradeoffs shape every decision: what is fine for a prototype is wrong for a five-year system.
- Readability is a feature: code is read far more often than it is written.
- Testing is an engineering skill, and a disciplined test pyramid keeps suites fast and trustworthy.
- Change is normal: the system must support safe, frequent, reviewable changes, not resist them.
- Hyrum's Law holds: once a behavior is depended on, it becomes a contract, whether documented or not.
- The process is the product: rules exist to make many people productive together.

## Key patterns
- The test pyramid: many fast unit tests, fewer integration tests, a thin slice of end-to-end tests.
- Code review as a quality and knowledge-sharing event, with small, focused changes.
- Policy as code: runbooks, style guides, and guardrails written down and enforced by tooling.
- Deprecation discipline: an owner, a timeline, and a migration path for anything removed.
- Documentation that lives next to the code and explains the why, not just the what.
- A shared culture of ownership: everyone can fix what they see, and nobody owns a walled-off silo.

## Applying this to n8n/automation/code
- Build the workflow library like a codebase: reviews, versioning, and a shared style enforced by the gates.
- Split large workflows into tested subworkflows and document each contract at the boundary.
- Run the test pyramid on automations: fast unit checks in Code nodes, integration runs against mocks, and rare live end-to-end runs.
- Treat any output that other workflows depend on as a contract; change it only with a migration path.
- Keep a decision log and known-issues file so future owners inherit the reasoning.

## Hard rules
- Never merge unreviewed changes to shared code, workflows, or contracts.
- Never remove a behavior that other systems depend on without a migration and a timeline.
- Never let the end-to-end layer grow unchecked; most coverage belongs in fast tests.
- Always write the test before claiming a change is done.

## Pairs with
continuous-delivery-pipeline, sre-reliability-engineering, devops-handbook-flow, accelerate-dora-metrics, staff-engineer-leadership
