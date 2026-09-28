---
name: rag-eval-deepeval-ragas-adapter
description: "RAG evaluation adapter (faithfulness/answer-relevancy/context precision-recall, pytest CI gates, tune-vs-gate split). Use when a RAG pipeline (Qdrant + embeddings + chat) needs grounding measurement, retrieval-vs-generation diagnosis, or a CI quality gate. Trigger phrases: 'evaluate RAG', 'faithfulness', 'ragas', 'deepeval', 'قياس جودة الاسترجاع'."
---

# RAG Eval Adapter (Diagnose with RAGAS, Gate with DeepEval)

Adapter over **RAGAS** (reference RAG metrics: faithfulness, answer
relevancy, context precision/recall; component-level diagnosis) and
**DeepEval** (pytest-style framework, 16K stars: broad metrics incl.
G-Eval judges, agent/chat metrics, synthetic data, CI-native). Proven
production pairing: RAGAS to TUNE, DeepEval to GATE. Maps directly onto
our stack (`rag_engine.py`, Qdrant collections, NVIDIA embeddings,
`n8n-rag-vector-qa` wiring).

## When to use

- "Why is the pipeline wrong — retrieval or generation?" → RAGAS
  component metrics while tuning chunking, hybrid search, reranking.
- "Did this change make the feature worse?" → DeepEval pytest gate in
  CI/PR with thresholds.
- Any RAG delivery: faithfulness + precision/recall numbers archived
  with the delivery evidence.

## Steps

1. Build the eval dataset (real Q/A + retrieved contexts; synthetic
   generation for volume, human labels for calibration).
2. Tune loop (RAGAS): faithfulness (claims supported by context?),
   answer relevancy, context precision/recall → locate the failure
   (retrieval miss vs generation drift) → adjust chunking/embeddings/
   rerank → re-measure. Fix the judge model across comparisons.
3. Gate loop (DeepEval): pytest cases with metric thresholds; fail CI
   on regression; track cost per eval run.
4. Calibrate: scores are RELATIVE signals (did faithfulness drop after
   this change?), not absolute truth — spot-check against human labels
   before trusting a threshold; pin chunk/embedding/rerank versions
   with each reported number.
5. Wire into the RAG delivery checklist: eval numbers beside retrieval
   latency/recall in the evidence table.

## Verification

- Faithfulness + precision/recall reported per delivery with dataset
  version + judge model pinned.
- CI gate green; threshold changes reviewed (never silently lowered).
- Human spot-check log exists for the current thresholds.

## Pairs with

`n8n-rag-vector-qa` (pipeline), `qdrant-ops`, `rag-eval-faithfulness`,
`promptfoo-eval-redteam-adapter` (security side),
`build-gates-pipeline` (QUALITY).
