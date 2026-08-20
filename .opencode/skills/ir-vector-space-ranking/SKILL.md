---
name: ir-vector-space-ranking
description: Applies the information-retrieval chapters of Jurafsky & Martin's Speech and Language Processing to rank documents for a query: the vector space model, TF-IDF weighting, cosine similarity, relevance feedback, and evaluation with precision and recall. Use when the user says 'vector space model', 'TF-IDF', 'cosine similarity', 'information retrieval ranking', 'relevance feedback', 'precision recall', or when a search or retrieval system must rank documents well. Pairs with: speech-language-processing, search-patterns, vector-databases-similarity-search, n8n-rag-vector-qa.
---
# Vector-Space Information Retrieval and Ranking

## When to use
Use when a search or retrieval system must rank documents well, or when the user asks about the vector space model, TF-IDF, or cosine similarity.

## Core mechanics
- Represent documents and queries as vectors.
- Weight terms with TF-IDF.
- Rank by cosine similarity.
- Apply relevance feedback to refine results.
- Evaluate with precision and recall.
- Combine with modern dense retrieval when appropriate.

## Verification
- Verify ranking on a small corpus with known relevance.
- Report precision and recall at cutoff levels.
- Test that TF-IDF weights match reference values.
