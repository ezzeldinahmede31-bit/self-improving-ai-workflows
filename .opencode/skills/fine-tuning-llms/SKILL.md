---
name: fine-tuning-llms
description: "Applies the fine-tuning discipline of Building LLM-Powered Applications and NLP with Transformers: decide when fine-tuning beats prompting, prepare and curate training data, choose LoRA or QLoRA adapters, train and evaluate against a held-out set, and deploy the adapter. Covers the honest rule that fine-tuning is the last lever, after prompt and context engineering. Use when the user says 'fine-tune a model', 'LoRA', 'QLoRA', 'training data for the model', 'domain-specific model', or 'tune instead of prompt'."
---
# fine-tuning-llms

Fine-tuning adapts a pretrained model to a specific domain or output style using your own data. This skill encodes the full loop — deciding when to fine-tune, curating data, training with parameter-efficient methods, evaluating honestly, and deploying the adapter — so the effort pays off and the result is measurable.

## Core principles
- Fine-tuning is the last lever: prompt and context engineering come first, measured against an eval set.
- Data quality dominates: a small curated, labeled, deduplicated set beats a large noisy one.
- Parameter-efficient tuning (LoRA, QLoRA) gives most of the benefit at a fraction of the cost.
- Evaluation is pre- and post-: the same held-out set grades the base model, the fine-tuned model, and any future candidate.
- The trained artifact is versioned and registered like any other model.
- Fine-tuning can regress unrelated skills; eval must cover general behavior, not just the target task.

## Key patterns
- Task and data audit: define the exact input-output contract, then gather and label examples that match it.
- Data pipeline: clean, deduplicate, split train and held-out, and record dataset version and checksum.
- Adapter training: LoRA or QLoRA with a small learning rate, early stopping on the held-out loss.
- A/B eval: run the base model and the fine-tuned model on the same held-out set and compare per case.
- Registry and rollback: register the adapter with metrics and keep the base model deployable.
- Deployment: attach the adapter at inference time through the model provider or a local serving layer.

## Applying this to n8n/Python automation
- Treat fine-tuning as a workflow: export the labeled examples as a dataset, run the training script, and evaluate on the held-out set.
- Register every trained adapter in the model registry table with its held-out metrics.
- Serve the fine-tuned model through the same inference path as the base model so switching is a config change.
- Run a comparison workflow that samples both models on live inputs and records the winner per case.
- Keep prompt engineering, RAG, and fine-tuning as separate levers and measure each one's contribution before layering the next.

## Hard rules
- Never fine-tune before prompting, context, and retrieval are tuned and measured.
- Never train without a held-out eval set shared by every model candidate.
- Never deploy an adapter that is not versioned and registered with its metrics.
- Never claim fine-tuning improved quality without the before-and-after eval evidence.

## Pairs with
nlp-transformers-huggingface, ai-engineering-foundation-models, evaluation, designing-machine-learning-systems, machine-learning-design-patterns, build-gates-pipeline
