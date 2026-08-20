---
name: speech-language-processing
description: Applies Jurafsky & Martin's Speech and Language Processing (SLP) to build NLP systems on textbook foundations: regular expressions and text normalization, n-grams and language models, part-of-speech tagging, parsing, semantic analysis, information extraction, and speech processing (ASR, TTS). Use when the user says 'build an NLP system', 'language model', 'POS tagging', 'syntactic parsing', 'information extraction', 'speech recognition', 'Jurafsky', 'SLP', 'text normalization', or when a natural-language feature must be built with the standard pipeline. Pairs with: foundations-statistical-nlp, neural-network-methods-nlp, nlp-transformers-huggingface, ai-engineering-foundation-models.
---
# Speech and Language Processing

## When to use
Use this skill when building any natural-language or speech feature that should rest on textbook foundations, or when the user asks about the standard NLP pipeline from text normalization through parsing to speech.

## Core mechanics
- Start with text normalization: tokenization, word segmentation, sentence segmentation, and handling of casing, numbers, and punctuation.
- Choose the level of analysis the task needs: words, morphology, syntax, or semantics.
- Use language models for generation and ranking, tagging for structure, parsing for syntax, and information extraction to pull relations from text.
- For speech, follow the acoustic-to-linguistic pipeline from feature extraction through acoustic modeling to decoding.
- Match the method to the evidence: statistical methods for text, neural methods when data is plentiful.

## Verification
- Test every stage on a small labeled sample before scaling.
- Verify that tokens, tags, and parses are correct on adversarial examples, not just common ones.
- Compare the chosen model against a simple baseline and report the gap.
