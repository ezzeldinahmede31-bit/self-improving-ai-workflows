---
name: intelligent-automation-rpa
description: "Applies Intelligent Automation and RPA design to automate systems with no API: UI automation for legacy screens, OCR and document understanding for paper, model-driven decisioning, and human-in-the-loop exception handling. Covers the taxonomy of when to use API, UI, or document automation. Use when the user says 'RPA', 'UI automation', 'robotic process automation', 'document processing', 'OCR pipeline', 'automate a legacy system', or 'exception handling automation'."
---
# intelligent-automation-rpa

Intelligent automation combines RPA (UI-level automation for systems without APIs) with AI understanding and human oversight. This skill encodes the taxonomy — API automation first, UI automation when no API exists, document understanding when input is paper, and human exception handling where judgment is required — so the right tool is used for the right surface.

## Core principles
- Prefer API and webhook integration before UI automation; UI automation is the last resort, not the first.
- UI automation is brittle: selectors and screens change, so every step is verified and every failure is loud.
- Document understanding pairs OCR with a model pass to turn unstructured paper into structured data.
- AI handles fuzzy judgment; RPA handles deterministic repetition; the split is explicit in the design.
- Exceptions route to humans: a small set of edge cases that confuse the bot go to a queue for manual handling.
- Every automated action is logged with a trace so a misstep can be replayed and fixed.

## Key patterns
- Surface taxonomy: API available, no API but stable UI, paper documents, or human-only judgment.
- Selector discipline: identify UI elements by stable attributes and verify them before scripting the step.
- OCR-plus-model: extract text, then validate and structure it with a schema check rather than trusting raw output.
- Human exception queue: items below a confidence threshold route to a review queue, not to silent acceptance.
- Audit trail: each run records what was read, decided, and done, with screenshots or payloads as evidence.
- Recovery: a failed step retries once, then pauses for human inspection instead of drifting.

## Applying this to n8n/Python automation
- Wire the API path first; only add browser or desktop UI automation nodes when the target system exposes no API.
- Add an OCR and model pass for scanned input, and validate the structured result against a schema.
- Route low-confidence or unparseable items to a human review queue rather than failing the run.
- Log every automated action with its evidence payload for audit and replay.
- Apply the build gates, and treat every UI automation step as a candidate failure point that needs verification.

## Hard rules
- Never automate a legacy screen with UI automation when an API or webhook exists.
- Never trust raw OCR output; always validate and structure it.
- Never silently accept low-confidence results; route them to a human.
- Never deliver an RPA flow that has not run end-to-end on the real system.

## Pairs with
n8n-workflow, ai-engineering-foundation-models, evaluation, nlp-transformers-huggingface, build-gates-pipeline
