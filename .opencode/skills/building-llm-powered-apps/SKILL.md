---
name: building-llm-powered-apps
description: "Applies the product-engineering method of Building LLM-Powered Applications (Valentina Alto) to design LLM features from user goals: choose the right LLM for the task, design prompts and structured outputs, plan evaluation, and handle cost, latency, and failure modes. Covers the full build loop from idea to production. Use when the user says 'build an LLM feature', 'LLM-powered app', 'which model should I use', 'design the prompt', or 'structured output from an LLM'."
---
# building-llm-powered-apps

Building an LLM feature is a product exercise, not a prompt-writing exercise. This skill takes a user goal and walks it through the engineering loop: task framing, model selection, prompt and structured-output design, evaluation, and the cost-latency trade-offs that decide whether the feature ships at all.

## Core principles
- Start from the user goal and the decision it enables; the LLM is a component, not the product.
- Prefer the simplest model that passes the eval; capability beyond need is wasted latency and spend.
- Structured output is a contract: define the JSON schema before the prompt, and validate the response mechanically.
- Evaluation is the unit of trust: build a labeled eval set from real examples before tuning anything.
- Fail visibly: detect wrong-shaped output, empty answers, and hallucinated keys instead of propagating them.
- Iterate on the smallest change: prompt first, then context, then model, then fine-tune.

## Key patterns
- Task framing checklist: input, output, constraints, examples, cost ceiling, and the fallback when the model fails.
- Prompt-and-schema pair: one template plus one JSON schema, versioned together, tested together.
- Two-stage extraction: first call extracts raw facts, second call maps facts onto the schema, reducing hallucination.
- Confidence and abstention: ask the model for a confidence field and route low-confidence outputs to the human or a fallback.
- Evals in the loop: run a fixed eval set on every change and refuse to merge a change that lowers the score.

## Applying this to n8n/Python automation
- Define the output schema in a Set or Code node and validate every model response against it before downstream nodes run.
- Build the eval set as a data table and run a scoring workflow after each prompt edit.
- Use the JSON output parser node with autoFix enabled for resilient structured outputs.
- Wire a fallback path in n8n: if validation fails, send the item to a human review branch instead of failing the run.
- Wrap model calls with the cost meter from the usage field and record it per run.

## Hard rules
- Never build the prompt before the schema is written and the eval set exists.
- Never ship an LLM feature with an unhandled failure path for malformed output.
- Never tune the prompt on a single example; tune on the eval set.
- Never escalate to a bigger model before cheaper interventions are measured.

## Pairs with
ai-engineering-foundation-models, prompt-engineering-llm-apps, evaluation, designing-machine-learning-systems, n8n-agents-official, build-gates-pipeline
