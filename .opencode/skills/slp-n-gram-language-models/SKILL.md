---
name: slp-n-gram-language-models
description: Applies the language-model chapters of Jurafsky & Martin's Speech and Language Processing to build and evaluate n-gram language models: n-gram probability estimation, smoothing (Laplace, interpolation, backoff), perplexity, and the practical choices that make a language model useful. Use when the user says 'n-gram model', 'language model smoothing', 'Laplace smoothing', 'interpolation backoff', 'perplexity', 'SLP language models', or when a probabilistic language model must be built and evaluated. Pairs with: speech-language-processing, foundations-statistical-nlp, ai-engineering-foundation-models, natural-language-processing-python.
---
# n-Gram Language Models

## When to use
Use when a probabilistic language model must be built and evaluated, or when the user asks about n-gram estimation, smoothing, or perplexity.

## Core mechanics
- Estimate n-gram probabilities from counts with maximum likelihood.
- Apply smoothing to handle sparse data.
- Use interpolation and backoff to combine orders.
- Evaluate the model with perplexity.
- Choose the order and vocabulary to fit the data.
- Recognize the limits of n-gram models.

## Verification
- Compute perplexity on a held-out set.
- Verify smoothing lowers perplexity on a sparse corpus.
- Reproduce a textbook example.
