---
name: prompt-engineering-for-developers
description: "Applies Prompt Engineering for Developers to the engineering craft of writing reliable prompts: role and task framing, structured output contracts, few-shot examples, chain-of-thought for reasoning, context ordering, and iterative debugging of prompt failures. Covers prompt versioning and the eval loop. Use when the user says 'write a better prompt', 'prompt engineering', 'few-shot', 'chain of thought', 'structured output JSON', or 'why does my prompt drift'."
---
# prompt-engineering-for-developers

Prompts are code that runs on a language model, and they deserve the same discipline as code: clear contracts, versioning, tests, and debugging. This skill turns prompt-writing into an engineering activity with repeatable techniques and measurable outcomes.

## Core principles
- State the task, the audience, the format, and the constraints explicitly; do not rely on the model guessing.
- Make the output contract concrete: exact structure, field names, allowed values, and failure behavior.
- Few-shot examples teach more than adjectives; include the hard cases, not just the happy path.
- Order matters: put instructions before long context, and put the decisive instruction last.
- For reasoning tasks, ask for the reasoning before the answer so the model cannot shortcut to a guess.
- Treat a prompt like a codebase: version it, diff it, and run evals when it changes.

## Key patterns
- Role plus task plus format plus constraints plus example: the five-part prompt skeleton.
- Delimiters for untrusted content: wrap external data in markers so it is treated as data, never as instructions.
- Chain-of-thought prompting for math and logic, with the derivation separated from the final answer.
- Structured output via JSON schema in the prompt, validated by a parser after the call.
- Negative instructions: list what the output must never do (do not fabricate, do not omit required keys).
- Prompt A/B in shadow mode: run two prompt variants on the same traffic and compare verdicts.

## Applying this to n8n/Python automation
- Store prompt templates in a dedicated node or table so each workflow step references a versioned template.
- Add a Code node after the model that validates the JSON contract and fails the branch loudly on violation.
- Use the n8n prompt tool or agent system prompt slots for the role and constraints sections.
- Wrap scraped or webhook content in the untrusted-data delimiters before it reaches any prompt.
- Keep a prompt changelog in the repo and trigger the eval workflow on every prompt edit.

## Hard rules
- Never put user or scraped content into a prompt without delimiting it as data.
- Never change a production prompt without an eval run on the frozen eval set.
- Never claim a prompt is better without a side-by-side measurement.
- Never ask for the final answer first on a reasoning task that needs a derivation.

## Pairs with
prompt-engineering-llm-apps, evaluation, ai-engineering-foundation-models, n8n-agents-official, litellm-tier-router, build-gates-pipeline
