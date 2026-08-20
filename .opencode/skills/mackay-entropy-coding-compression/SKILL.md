---
name: mackay-entropy-coding-compression
description: Applies the coding and compression chapters of David MacKay's Information Theory, Inference, and Learning Algorithms to compress data exactly: Shannon's source-coding theorem, Huffman coding, arithmetic coding, and the Lempel-Ziv family, with the entropy as the unbeatable bound. Use when the user says 'entropy coding', 'Huffman coding', 'arithmetic coding', 'Lempel Ziv', 'source coding theorem', 'data compression theory', 'MacKay coding', or when data must be compressed efficiently and provably. Pairs with: information-theory-inference-learning, elements-information-theory, algorithmic-math-reasoner, clrs-string-matching.
---
# Entropy Coding and Compression

## When to use
Use when data must be compressed efficiently and provably, or when the user asks about Huffman coding, arithmetic coding, or the source-coding theorem.

## Core mechanics
- Use entropy as the lower bound on code length.
- Apply Huffman coding for symbol codes.
- Use arithmetic coding for near-optimal block codes.
- Consider the Lempel-Ziv family for universal compression.
- Model the source to improve compression.
- Verify that a code is prefix-free.

## Verification
- Verify a Huffman code is optimal for the given probabilities.
- Check an arithmetic code decodes back to the original.
- Compare code length against the entropy bound.
