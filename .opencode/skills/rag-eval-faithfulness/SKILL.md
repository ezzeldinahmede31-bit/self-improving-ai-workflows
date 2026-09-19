---
name: rag-eval-faithfulness
description: "RAG faithfulness evaluation distilled. Use when measuring groundedness, citation accuracy, retrieval recall, chunking effects, hallucination rate."
---

# RAG Faithfulness Evaluation

## Purpose

Prove RAG answers stay grounded: faithfulness to retrieved context, citation accuracy, retrieval recall, chunking impact, hallucination tracking.

## When to use

Use when the user says 'RAG eval', 'faithfulness', 'groundedness', 'citation accuracy', 'retrieval recall', 'hallucination rate'.

## Steps

1. Score faithfulness: every claim traceable to cited chunks.
2. Verify citations point to supporting spans, not nearby text.
3. Measure retrieval recall on known-answer probes.
4. A/B chunking and ranking changes against the same eval set.
5. Track hallucination rate per release with failure review.

## Anti-patterns

- Fluency mistaken for correctness.
- Citations decorating ungrounded claims.
- Retrieval tuned without eval-set proof.
- Chunking changed globally on anecdotal wins.

## Example

Eval row: question, gold chunks, answer, per-claim citation verdict, faithfulness score.

## Verification

Faithfulness scored, citations verified, recall measured, changes A/B proven.

## Pairs-with

evaluating-rag-faithfulness-metrics, n8n-rag-vector-qa, llm-eval-harness, vector-databases-similarity-search.
