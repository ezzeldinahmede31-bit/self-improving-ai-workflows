---
name: vector-databases-similarity-search
description: "Covers the fundamentals of vector databases and similarity search that any RAG or semantic-search build depends on: embedding representation, vector indexes (HNSW, IVF, PQ), distance metrics (cosine, euclidean, dot product), recall/latency trade-offs, hybrid (keyword + vector) search, and evaluation of retrieval quality. Use when the user says 'vector database', 'ANN index', 'HNSW', 'IVF', 'product quantization', 'cosine similarity', 'recall', 'hybrid search', 'choose a distance metric', 'why is retrieval slow', 'semantic search', or when tuning or evaluating a vector store. Pairs with: qdrant-ops, nvidia-embeddings, n8n-rag-vector-qa, search-patterns, database-internals-engines."
---

# Vector Databases and Similarity Search

The premise: vector search finds things by meaning, not by exact match — text,
images, and audio become points in a high-dimensional space, and retrieval asks
which points are nearest to a query point.

## When to use

- Choosing or configuring a vector store (Qdrant, Milvus, Pinecone, pgvector).
- Tuning recall, speed, or memory for semantic search / RAG.
- Debugging why retrieval returns irrelevant results.
- Picking a distance metric or an index type.

## The pipeline

1. **Embeddings** — map items to fixed-size vectors with a model (see
   `nvidia-embeddings`); the embedding space defines what "similar" means.
2. **Index** — structure vectors for fast approximate nearest-neighbor (ANN)
   search.
3. **Query** — embed the query with the SAME model and search the index.
4. **Serve** — return the nearest vectors plus metadata.

## Index types (the recall vs speed trade)

- **Flat (exact)**: scan everything; perfect recall, slow at scale — the baseline
  to beat.
- **IVF**: cluster the space and search only nearby clusters; fast, approximate,
  good at small-to-medium scale.
- **HNSW**: hierarchical navigable small-world graph; strong recall with tunable
  neighbors; the common default for high recall.
- **PQ (product quantization)**: compress vectors to fractions of their size; big
  memory savings, measurable accuracy loss.
- Rule: measure recall on YOUR data, with YOUR queries — a recall figure quoted
  for a benchmark corpus does not transfer.

## Distance metrics

- **Cosine**: normalized direction similarity — standard for text embeddings.
- **Euclidean**: raw distance — sensitive to magnitude; matches when magnitude
  carries meaning.
- **Dot product**: raw similarity — use when the embedding space is built for it
  (some models store magnitude in the vector).
- The metric must match what the embedding model was trained to use.

## Hybrid search

- Keyword (BM25) and vector search answer different queries; a hybrid that merges
  both beats either alone on heterogeneous corpora.
- Merge scores with weights tuned on real queries; normalize the two score
  families first.

## Evaluation

- Build a labeled set of queries with their expected results; measure recall@k and
  mean reciprocal rank.
- Tune index parameters (neighbors, ef_search) against a latency budget, not for
  maximum recall alone.
- Re-run evaluation whenever the embedding model or the corpus changes.

Pairs with: qdrant-ops (Qdrant operations), nvidia-embeddings (embedding
payloads), n8n-rag-vector-qa (n8n wiring), search-patterns (UX around retrieval),
database-internals-engines (storage internals).