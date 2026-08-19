---
name: ai-safety-governance
description: "Applies AI safety and governance discipline to every model-backed feature: prompt-injection defense, output filtering, access control, audit logging, policy enforcement, and red-teaming. Covers the controls that keep an AI system safe, controlled, and traceable. Use when the user says 'AI safety', 'AI governance', 'prompt injection', 'guardrails', 'output filtering', 'red-team the model', or 'controlled AI'."
---
# ai-safety-governance

AI safety and governance turn a capable model into a controlled one: inputs are constrained, outputs are filtered, actions are gated, and everything is auditable. This skill encodes the control layers — injection defense, output filtering, access control, audit, policy, and adversarial testing — that make a model-backed system controlled and traceable.

## Core principles
- Treat model inputs and outputs as untrusted until proven otherwise; the model is a component with a security boundary.
- Prompt injection is a real vector: external content must be marked as data, never as instructions.
- Output filtering is mandatory: schemas, blocklists, and detectors run on every model response before it acts.
- Access control applies to tools: the model can only reach what its role permits, never more.
- Everything is auditable: prompts, responses, actions, and decisions are logged with trace ids.
- Red-teaming is continuous: adversarial testing finds weaknesses before attackers or accidents do.

## Key patterns
- Wrapper delimiters: external content is wrapped in explicit data markers so the model treats it as untrusted data.
- Output contract validation: parse and validate the response schema; reject or quarantine malformed output.
- Tool scope lock: an explicit allowed-tools list bounds what the model may act on.
- Approval gates: state-changing and destructive actions require human confirmation.
- Audit trail: every model call and tool action is recorded with a trace id linking input to output to action.
- Red-team passes: a standing set of injection, jailbreak, and data-exfiltration probes runs on every change.

## Applying this to n8n/Python automation
- Wrap any scraped or web-sourced content in a data-marker node before it reaches a model node.
- Validate model output against a JSON schema in a Code node before any downstream action node.
- Give agent nodes an explicit allowed-tools list and a bounded iteration ceiling.
- Add a human approval branch before destructive or external-facing actions.
- Run the security stage of the build gates: injection, tool scope, secrets, and uncontrolled-destination checks are mandatory before deploy.

## Hard rules
- Never let untrusted external content reach a model without being marked as data.
- Never act on model output that fails schema validation.
- Never grant a model tool access beyond its declared scope.
- Never deploy a model-backed feature without an audit trail and a red-team pass.

## Pairs with
ai-engineering-foundation-models, prompt-engineering-llm-apps, build-gates-pipeline, n8n-agents-official, evaluation, ai-skill-authoring-standards
