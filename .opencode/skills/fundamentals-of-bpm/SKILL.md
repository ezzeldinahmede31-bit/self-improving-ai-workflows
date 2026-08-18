---
name: fundamentals-of-bpm
description: Applies Dumas, La Rosa, Mendling & Reijers' Fundamentals of Business Process Management as the practical handbook for modeling and improving business processes — identifying the process, creating as-is and to-be BPMN models, process discovery and stakeholder interviews, quantitative and qualitative process analysis (flow analysis, queuing, simulation, value-added and waste analysis), redesign (heuristic and more radical), and process automation with monitoring. Use when the user says 'fundamentals of BPM', 'process discovery', 'as-is to-be model', 'BPMN', 'process redesign', 'process analysis', 'waste analysis', 'Dumas BPM', 'process improvement', 'process automation', or when improving an existing business process from discovery through to automation. Pairs with: business-process-management-weske, workflow-management-van-der-aalst, process-mining, n8n-workflow, thinking-systems, the-goal-constraints.
---
# Fundamentals of Business Process Management (Dumas et al.)

Transfers the Dumas / La Rosa / Mendling / Reijers handbook so a process improvement project runs the full loop: discover the real process, model it, analyze it with numbers, redesign it, and automate the improved version.

## When to use
- Running a process improvement or automation project from start to finish.
- Modeling a process in BPMN and analyzing where the waste and delays are.
- Justifying a redesign with quantitative analysis before changing anything.

## The loop
1. Process identification and discovery: define boundaries, interview stakeholders, capture the actual (as-is) process, not the intended one.
2. Modeling: BPMN with clear activities, events, gateways, and resources.
3. Analysis: quantitative (flow analysis, queuing, simulation with cycle times) and qualitative (value-added vs non-value-added steps, waste, rework, waiting).
4. Redesign: apply heuristic redesign (task elimination, reordering, resource pooling, parallelization) and, where warranted, more radical transformation.
5. Implementation and automation: deploy the to-be model, monitor it, and feed results back into the loop.

## Principles
- Measure before redesign; a change without baseline numbers is a guess.
- Attack waiting time and hand-offs first; they dominate most cycle times.
- Keep the model faithful to reality; a pretty diagram of a fictional process automates the fiction.

## Verification discipline
- Validate the as-is model with the people who run the process.
- Simulate the to-be model on the same inputs as the baseline before committing.
- After automation, compare actual cycle time and cost against the analysis prediction.

## Pairs with
business-process-management-weske, workflow-management-van-der-aalst, process-mining, n8n-workflow, thinking-systems, the-goal-constraints.