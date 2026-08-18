---
name: business-process-management-weske
description: Applies Mathias Weske's Business Process Management to design, model, analyze, and orchestrate business processes — process modeling with BPMN, process enactment engines (orchestration, choreography, collaboration), process analysis (performance and conformance), and process lifecycle management with process automation. Bridges business analysis and IT implementation so a process is described once and enacted faithfully. Use when the user says 'BPM', 'business process management', 'BPMN model', 'process orchestration', 'process engine', 'process lifecycle', 'Weske BPM', 'process analysis', 'workflow automation design', or when designing and automating a structured business process that must be modeled, executed, and measured. Pairs with: fundamentals-of-bpm, workflow-management-van-der-aalst, process-mining, n8n-workflow, automation-known-issues-compass, long-horizon-executor.
---
# Business Process Management (Weske)

Transfers Mathias Weske's BPM discipline so business processes are modeled explicitly (BPMN), enacted by an engine, and analyzed — bridging the business and IT views instead of automating blindly.

## When to use
- Designing or redesigning a structured business process that will be automated.
- Modeling a process in BPMN for shared understanding before implementation.
- Analyzing a running process for performance and conformance gaps.

## The discipline
1. Model the process first in BPMN: activities, events, gateways, lanes, and the data flow; the model is the contract both sides agree on.
2. Distinguish orchestration (one engine runs the internal steps), choreography (partners exchange messages), and collaboration (both together).
3. Enact the model with a process engine so execution matches the diagram; keep the model and the runtime in sync.
4. Analyze continuously: cycle time and resource utilization for performance, conformance checking to find where reality diverges from the model.

## Lifecycle
- Discover the real process, model it, implement it, run it, analyze it, then improve and remodel — a closed loop, not a one-shot automation.

## Verification discipline
- Validate the BPMN model before build: reachable end states, no deadlocks, every path has an event.
- Test the enacted process with the same scenarios the model promised.
- Run conformance analysis on production executions and close gaps between the model and reality.

## Pairs with
fundamentals-of-bpm, workflow-management-van-der-aalst, process-mining, n8n-workflow, automation-known-issues-compass, long-horizon-executor.