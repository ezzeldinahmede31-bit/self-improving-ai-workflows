---
name: ai-automation-master-blueprint
description: "The master blueprint for architecting AI automation end to end: discovery, psychology-grounded design, pipeline wiring, security and cost gates, delivery verification, and post-deployment monitoring. Orchestrates every specialist automation skill into one coherent build. Use when the user says 'architect my automation', 'AI automation blueprint', 'full pipeline design', 'build the whole system', 'end to end automation', or 'make it production-ready'."
---
# ai-automation-master-blueprint

This skill is the coordinating layer: it assembles the specialist automation skills into one end-to-end blueprint. From discovering what the automation must achieve, through psychology-grounded design, wiring, gates, delivery verification, and monitoring — it keeps the build coherent instead of a pile of nodes.

## Core principles
- Start from purpose and audience; an automation built without a goal is a solution in search of a problem.
- Research before building: adopt the best existing implementation, then apply the required changes.
- Design the flow on paper before placing a node; the wiring contract precedes the JSON.
- Security, cost, and quality are designed in from the first node, not patched after.
- Delivery means proof: an artifact ships only when it ran end to end and met the agreed result.
- After deployment, monitoring closes the loop; a live system is a measured system.

## Key patterns
- Discovery: turn the request into purpose, audience, and a done-when contract.
- Best-practice pass: search templates and existing implementations before designing.
- Incremental build: emit one node, schema-check it, wire it, then the next.
- Gate pipeline: security, quality, integrity, precision, reasoning, and dry-run before deploy.
- Delivery verification: execute the real workflow, compare outputs, audit the original commands.
- Monitoring loop: track runs, errors, costs, and success rate; feed findings back into the design.

## Applying this to n8n/Python automation
- Run the mandatory skill-stack order: clarify, psychology pass, best-practice research, then build.
- Use incremental-generation to place nodes one at a time against the schema cache.
- Run the build gates with the schema cache until the verdict is ready for deployment.
- Activate, execute, and verify the workflow end to end before delivering it.
- Add monitoring nodes for errors, cost, and success rate, and review them on a schedule.

## Hard rules
- Never build before the purpose and done-when contract are fixed.
- Never skip the research pass; from-memory designs are forbidden when a web pass can find better.
- Never deliver an artifact that did not run end to end with the agreed output.
- Never ship a workflow that fails the build gates.

## Pairs with
ai-engineering-foundation-models, n8n-agents-official, multi-agent-patterns, evaluation, build-gates-pipeline, n8n-workflow, context-engineering, ai-skill-authoring-standards
