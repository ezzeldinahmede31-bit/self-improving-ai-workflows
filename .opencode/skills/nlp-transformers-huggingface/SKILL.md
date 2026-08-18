---
name: nlp-transformers-huggingface
description: Applies Tunstall, von Werra & Wolf's Natural Language Processing with Transformers to build production NLP pipelines with the Hugging Face ecosystem — tokenization, pretrained model selection, transfer learning and fine-tuning, token classification, text classification, question answering, translation, summarization, and large-scale training (TPU/GPU, mixed precision, dataset streaming). Covers the fine-tuning workflow that turns a general base model into a task specialist. Use when the user says 'fine-tune a transformer', 'Hugging Face', 'tokenizer', 'BERT', 'RoBERTa', 'T5', 'BART', 'sequence classification', 'question answering model', 'summarization model', 'translation model', 'Trainer API', 'dataset streaming', 'transfer learning NLP', or when building an NLP pipeline that must go beyond a canned API. Pairs with: ai-engineering-foundation-models, building-ml-powered-applications, designing-machine-learning-systems, experiment-code, data-analysis.
---

# NLP with Transformers

Transfers the Hugging Face fine-tuning playbook from Tunstall, von Werra & Wolf onto real NLP pipelines: tokenize correctly, choose the right pretrained base, fine-tune with the Trainer, and scale the training run without losing accuracy.

## When to use
- Fine-tuning a pretrained transformer for a downstream NLP task.
- Choosing tokenizers and model families for a text workload.
- Running training at scale (GPU/TPU, mixed precision, streaming datasets).

## The fine-tuning workflow
1. Tokenize with the model's own tokenizer; alignment between tokens and labels matters for token classification.
2. Pick the base model family by task: encoder-only (BERT/RoBERTa) for classification and tagging, encoder-decoder (T5/BART) for generation, decoder-only for open-ended generation.
3. Fine-tune with the Trainer API or native framework; use per-GPU learning-rate scaling and warmup.
4. Stream large datasets from disk instead of loading them into memory.

## Production concerns
- Freeze and unfreeze layers in stages for small data to avoid catastrophic forgetting.
- Use mixed precision and gradient accumulation to fit bigger batches on limited VRAM.
- Export to an optimized runtime (ONNX / quantized) before serving.

## Verification discipline
- Track loss and a task metric on a validation split through every epoch; stop on the best checkpoint, not the final one.
- Compare against the zero-shot base model to prove the fine-tune added value.
- Test on out-of-domain samples to expose distribution shift.

## Pairs with
ai-engineering-foundation-models, building-ml-powered-applications, designing-machine-learning-systems, experiment-code, data-analysis.