---
name: langchain-llamaindex-handbooks
description: "Applies the applied patterns of the LangChain and LlamaIndex Handbooks to build agent and RAG systems with the two dominant frameworks: chains, tools, retrievers, index structures, query engines, and the abstractions that transfer across both. Covers when each framework fits and how to migrate patterns to n8n. Use when the user says 'build with LangChain', 'build with LlamaIndex', 'RAG index', 'agent framework', 'chains and tools', or 'port this to n8n'."
---
# langchain-llamaindex-handbooks

LangChain and LlamaIndex are the two reference frameworks for applied LLM systems: LangChain for chains, tools, and agents, LlamaIndex for data indexing and retrieval. This skill encodes the shared engineering patterns so you can reason about either framework and translate them onto the n8n node graph.

## Core principles
- Abstractions transfer: model, memory, retriever, tool, chain — each framework names them differently but composes the same way.
- LlamaIndex leads with the index (documents, chunks, embeddings, retrieval); LangChain leads with the chain (call, tool, memory).
- Retrieval quality dominates generation quality: invest in chunking, embedding choice, and index structure first.
- Tools are typed contracts: name, description, input schema, and an execution path the model can rely on.
- Every abstraction has a cost: deep framework coupling makes the port to n8n nodes harder, so keep core logic framework-free.

## Key patterns
- Chain composition: prompt template, model, output parser wired as a single callable.
- Tool wrapper: function plus name, description, and JSON input schema exposed to the agent.
- Retriever abstraction: vector search, keyword search, or hybrid behind one interface.
- Index structures: document store, chunk index, metadata filters, and a query engine that composes retrieval and synthesis.
- Agent loop: model chooses a tool, executes, observes, and repeats until a stop condition.

## Applying this to n8n/Python automation
- Model LangChain chains as n8n node chains: prompt node, chat model node, output parser node.
- Model LangChain tools as n8n tool nodes attached to an AI Agent via the ai_tool output.
- Model LlamaIndex index as the Qdrant vector store node wired with embeddings and a retriever.
- Keep the Python-side chunking and embedding calls in scripts/rag_common.py so n8n and scripts share one implementation.
- Use the AI Agent node instead of hand-rolling the framework loop when the orchestration lives in n8n.

## Hard rules
- Never build a RAG system before fixing the index and retrieval quality.
- Never expose a tool to a model without a name, description, and input schema.
- Never let framework-specific objects leak across the n8n boundary; pass plain JSON.
- Never port a chain to n8n before drawing its node equivalent on paper.

## Pairs with
ai-engineering-foundation-models, n8n-rag-vector-qa, n8n-agents-official, vector-databases-similarity-search, qdrant-ops, multi-agent-patterns
