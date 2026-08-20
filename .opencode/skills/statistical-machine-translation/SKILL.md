---
name: statistical-machine-translation
description: Applies Philipp Koehn's Statistical Machine Translation to build translation systems from data: word-based and phrase-based models, the alignment problem, language models, decoding, and evaluation with BLEU. Use when the user says 'statistical machine translation', 'phrase based MT', 'word alignment', 'Koehn', 'BLEU score', 'translation model', or when building a translation system from parallel corpora. Pairs with: speech-language-processing, foundations-statistical-nlp, nlp-transformers-huggingface, data-analysis.
---
# Statistical Machine Translation

## When to use
Use when building a translation system from parallel corpora, or when the user asks about word alignment, phrase-based translation, or BLEU evaluation.

## Core mechanics
- Prepare parallel corpora and align sentences.
- Estimate word and phrase translation models.
- Train a language model for the target side.
- Decode with a beam search over the search space.
- Evaluate with BLEU and related metrics.
- Handle out-of-vocabulary terms explicitly.

## Verification
- Verify alignment on a small parallel set.
- Report BLEU against a reference translation.
- Test the decoder on short sentences.
