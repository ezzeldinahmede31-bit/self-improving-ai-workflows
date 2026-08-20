---
name: linguistic-fundamentals-nlp
description: Applies Emily Bender's Linguistic Fundamentals for Natural Language Processing to build NLP that respects real language structure: the levels of linguistic analysis (phonology, morphology, syntax, semantics, pragmatics), part-of-speech and phrase structure, and the pitfalls of treating text as a flat bag of tokens. Use when the user says 'linguistics for NLP', 'morphology', 'syntax semantics', 'Bender', 'language structure', 'why does my NLP miss grammar', or when an NLP feature needs linguistic awareness beyond statistics. Pairs with: speech-language-processing, foundations-statistical-nlp, natural-language-processing-python, practical-natural-language-processing.
---
# Linguistic Fundamentals for Natural Language Processing

## When to use
Use when an NLP feature needs linguistic awareness, or when the user asks about morphology, syntax, semantics, or why a model misses grammar.

## Core mechanics
- Work through the levels of language: phonology, morphology, syntax, semantics, pragmatics.
- Analyze words into morphemes before relying on token statistics.
- Use phrase structure and dependency information for syntax.
- Respect the distinction, that syntax and semantics are different layers, when designing features.
- Choose representations that preserve the linguistic structure the task needs.
- Document the linguistic assumptions built into a model.

## Verification
- Test the system on linguistic edge cases: morphology, negation, long-distance dependencies.
- Verify that the representation preserves the structure it claims to capture.
- Compare against a flat-token baseline to show the value of linguistic structure.
