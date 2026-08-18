---
name: prompt-engineering-llm-apps
description: Applies industry prompt-engineering guidance (OpenAI/Anthropic cookbooks, DSPy-style prompt programming) to build reliable LLM features — role and instruction clarity, structured output contracts, few-shot examples, chain-of-thought for reasoning tasks, context stuffing and ordering, prompt versioning, and evals as the only honest way to compare prompts. Covers when to prompt vs fine-tune and how to debug a failing prompt methodically. Use when the user says 'write a better prompt', 'prompt engineering', 'few-shot', 'chain of thought', 'structured output JSON', 'system prompt', 'prompt template', 'why does my LLM output drift', 'prompt evals', 'prompt versioning', 'persona prompt', or when building any LLM feature whose quality depends on the prompt. Pairs with: ai-engineering-foundation-models, n8n-agents, evaluation, clarify-before-execute, prompt-engineer, fable-5-playbook.
---
# Prompt Engineering for LLM Applications

Transfers proven prompt-engineering practice so LLM features are built, versioned, and evaluated like software instead of being typed ad hoc.

## When to use
- Writing or debugging the instruction surface of any LLM feature.
- Comparing prompt variants and needing an honest verdict.
- Choosing between prompting and fine-tuning for a task.

## The method
1. Define the output contract first: exact format, constraints, and failure behavior; request structured output when downstream code parses it.
2. Write the instruction: role + goal + rules; be specific and exhaustive, then let evals trim it.
3. Add few-shot examples chosen to be representative of hard, not easy, inputs.
4. Use chain-of-thought for multi-step reasoning; reserve tokens for the reasoning budget.
5. Control context: put the most load-bearing instructions and data where the model attends best; avoid stuffing irrelevant context.

## Prompt programming
- Treat prompts as code: version them, keep them in the repo, review changes.
- Build a small eval set of real inputs with expected outputs; every prompt edit runs the suite.
- When prompts plateau, consider retrieval, a smaller focused model, or fine-tuning on labeled failures.

## Verification discipline
- Never compare prompts by vibe; run the eval set and report deltas.
- Test adversarial or malformed inputs, not just the happy path.
- Watch for silent drift across model versions and context-length changes.
- A prompt that fails once is not a bug; one that fails on a stable eval case is.

## Pairs with
ai-engineering-foundation-models, n8n-agents, evaluation, clarify-before-execute, prompt-engineer, fable-5-playbook.