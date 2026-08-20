---
name: slp-pos-tagging-parsing
description: Applies the sequence-labeling and parsing chapters of Jurafsky & Martin's Speech and Language Processing to tag and parse text: part-of-speech tagging with HMMs and discriminative models, the CYK parsing algorithm, probabilistic context-free grammars, and dependency parsing. Use when the user says 'POS tagging', 'CYK parsing', 'probabilistic context free grammar', 'dependency parse', 'sequence labeling', 'SLP tagging', or when text must be tagged and parsed into structure. Pairs with: speech-language-processing, linguistic-fundamentals-nlp, pgm-inference-variable-elimination, algorithmic-math-reasoner.
---
# Part-of-Speech Tagging and Parsing

## When to use
Use when text must be tagged and parsed into structure, or when the user asks about POS tagging, CYK parsing, or dependency parsing.

## Core mechanics
- Tag parts of speech with sequence models.
- Parse with the CYK algorithm for probabilistic context-free grammars.
- Build dependency parses for typed relations.
- Handle ambiguity with the most probable analysis.
- Use the parse for downstream tasks.
- Evaluate tagging and parsing with accuracy metrics.

## Verification
- Verify tagging accuracy on a labeled sample.
- Test the parser on sentences with known structure.
- Check that parses align with the grammar.
