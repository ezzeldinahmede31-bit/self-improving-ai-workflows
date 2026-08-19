---
name: rag-systems
description: "Applies Retrieval-Augmented Generation (RAG) Systems engineering to build grounded question-answering: document ingestion, chunking, embedding, vector indexing, hybrid retrieval, and generation with citations. Covers the retrieval eval loop and failure modes that make RAG answer badly. Use when the user says 'RAG system', 'grounded answers', 'chat with my documents', 'retrieval pipeline', 'hybrid search', or 'citation-grounded generation'."
---
# rag-systems

RAG grounds LLM answers in your own documents by retrieving evidence first and generating from it second. This skill encodes the full pipeline — ingestion, chunking, embedding, indexing, retrieval, and synthesis — plus the eval discipline that separates a working RAG system from one that confidently invents answers.

## Core principles
- Garbage chunks produce garbage retrieval: chunk boundaries, sizes, and metadata determine recall.
- Retrieval is the bottleneck; generation only reformats what was found, so fix retrieval before prompting.
- Metadata filtering beats brute-force vector search on real corpora; store source, page, and section fields.
- Grounded output means every claim is traceable to a retrieved chunk; enforce citations mechanically.
- Retrieval quality is measurable: build a labeled query-to-relevant-chunk eval set.
- Hybrid search (keyword plus vector) fixes the exact-term misses that vector-only search suffers.

## Key patterns
- Ingestion pipeline: load documents, split with overlap, embed, upsert with metadata payloads.
- Chunking strategy: section-aware splits that keep tables, code, and entities whole; adjust chunk size to the embedding model.
- Index design: collection per corpus or per document, with payload fields for filtering and the embedding dimension fixed at creation.
- Retrieval stage: top-k vector hits, keyword hits, optional rerank, then a synthesis prompt with the chunks and the question.
- Citation contract: the answer template must emit source references that exist in the retrieved set.
- Eval loop: query set, relevance labels, retrieval recall and precision gates, plus an answer-groundedness check.

## Applying this to n8n/Python automation
- Use the n8n RAG wiring: loader node, text splitter node, embeddings node, Qdrant vector store node with ai_embedding and ai_textSplitter connections.
- Reuse scripts/rag_ingest.py and rag_query.py for scripted ingestion and search; keep chunking and embedding consistent with the n8n nodes.
- Store metadata payloads (source, page, section) so the retrieval node can filter before scoring.
- Run the eval set as an n8n workflow that scores retrieval and generation after every index change.
- Pass the RAG stage of the gates (R1-R6) before a RAG workflow is deployed.

## Hard rules
- Never change chunking or embedding without re-running the retrieval eval.
- Never answer from a chunk the retrieval did not return; enforce the citation contract.
- Never upsert into a collection whose dimension differs from the embedding output.
- Never deploy a RAG workflow that fails the structural RAG gate.

## Pairs with
n8n-rag-vector-qa, vector-databases-similarity-search, qdrant-ops, nvidia-embeddings, evaluation, build-gates-pipeline
