---
name: foundations-statistical-nlp
description: Applies Manning & Schutze's Foundations of Statistical Natural Language Processing to build NLP with statistical rigor: linguistic essentials, text tokenization, probability models and smoothing, collocations, n-gram models, HMM tagging, parsing with PCFGs, and statistical methods for retrieval. Use when the user says 'statistical NLP', 'Manning Schutze', 'smoothing', 'n-gram', 'HMM tagging', 'PCFG parsing', 'collocation', 'statistical language model', or when an NLP system must rest on statistically sound foundations. Pairs with: speech-language-processing, linguistic-fundamentals-nlp, probabilistic-graphical-models, all-of-statistics.
---
# Foundations of Statistical Natural Language Processing

## When to use
Use when an NLP system must be built on statistically sound foundations, or when the user asks about smoothing, n-grams, HMM tagging, or PCFG parsing.

## Core mechanics
- Represent text with tokenization and the vocabulary decisions that make the model tractable.
- Estimate probabilities with maximum likelihood and correct for sparse data with smoothing.
- Build n-gram models for sequence prediction and evaluate them with perplexity.
- Tag sequences with hidden Markov models and their extensions.
- Parse with probabilistic context-free grammars and the algorithms that search them.
- Apply collocation and statistical association measures for lexical analysis.

## Verification
- Hold out data and report perplexity or accuracy on unseen text.
- Test that smoothing improves the model on a small corpus where sparsity is visible.
- Verify parsing output on sentences with known structure.
