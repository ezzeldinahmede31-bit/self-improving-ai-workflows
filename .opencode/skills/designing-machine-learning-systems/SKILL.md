---
name: designing-machine-learning-systems
description: "Applies Chip Huyen's Designing Machine Learning Systems to take ML models from notebooks to production: the ML system lifecycle (data collection, feature engineering, training, evaluation, deployment, monitoring, retraining), data quality and drift (data distribution shift, concept drift), feature stores and online/offline consistency, model deployment patterns (batch, online, streaming), monitoring and observability for models, feedback loops, and the practical reality that ML systems fail on data and operations far more than on modeling. Use when the user says 'put my model in production', 'ML system design', 'data drift', 'concept drift', 'feature store', 'train-serve skew', 'model monitoring', 'retraining', 'online vs batch inference', 'ML observability', 'design an ML pipeline', 'reproducibility', 'MLOps', or when taking any model to production reliably. Pairs with: data-analysis, experiment-code, machine-learning-design-patterns, state-machine-persistence, n8n-rag-vector-qa, evaluation."
---

# Designing Machine Learning Systems

Huyen's thesis: an ML system is a software system with ML at its core — the model
is a small part of the whole. Production ML fails on data quality, drift, serving
infrastructure, and operations, not on the choice of algorithm.

## When to use

- Moving a model/experiment into a production service.
- Designing a new ML product end to end.
- Diagnosing a production model that degrades over time.

## The lifecycle (all phases matter)

1. **Business goal → ML problem**. Define what the model optimizes and the
   business metric it serves. A model that wins on AUC but does not move the
   business metric is waste.
2. **Data**: the foundation. Understand data sources, freshness, and biases.
   Data quality (missing, inconsistent, duplicated, skewed labels) dominates
   model quality. Establish labeling quality control.
3. **Feature engineering + feature stores**: define features once, serve the same
   features online and offline (**train-serve consistency**) — the classic silent
   failure is training on computed features that are different in production.
   A feature store keeps a single source of truth and timestamped feature values.
4. **Training**: reproducibility (fixed data versions, seeds, environment), and
   a clean split that does not leak future/duplicate data into training.
5. **Evaluation**: offline metrics plus online evaluation; calibrate thresholds to
   business cost of false positives vs false negatives.
6. **Deployment**: batch, online (single request), or streaming inference —
   choose by latency and volume needs.
7. **Monitoring**: track both system metrics (latency, throughput, errors) and
   **data/model metrics** (input distribution, prediction distribution,
   accuracy proxies). A model is not done when deployed — it is done when it can
   be watched and refreshed.
8. **Retraining**: decide when and how to refresh (scheduled, drift-triggered);
   always validate a new version before it replaces the old one.

## The failure modes (learn these)

- **Distribution shift**: training and production data come from different
  distributions (covariate shift, label shift, concept drift). Detect via input
  distribution monitoring and ground-truth feedback when available.
- **Train-serve skew**: the pipeline that computes features at training differs
  from the one at serving. Fix by using one pipeline for both.
- **Feedback loops**: model outputs influence future data (a recommendation model
  shapes what users see and therefore what gets logged). Account for the loop;
  collect explicit and diverse feedback.
- **Feedback delay**: labels arrive late or never — plan a labeling cadence that
  keeps monitoring meaningful.
- **Silent degradation**: a model can keep serving wrong answers without errors.
  Only monitoring catches this — which is why drift detection and prediction
  tracking are non-negotiable.

## Practical rules
- Start simple and baseline: a heuristic or linear model beats a broken deep model
  in production. Iterate with data, not just architecture.
- Version everything (data, features, model, code) so any result is reproducible.
- Make serving idempotent and safe: bounded latency, fallback to a default when
  the model is unavailable, and clear degradation semantics.
- Document the decision boundary and its business cost; that is what non-ML
  stakeholders can review.

Pairs with: machine-learning-design-patterns (reusable patterns), data-analysis
(statistical rigor), evaluation (measurement), n8n-rag-vector-qa (RAG serving),
state-machine-persistence (stateful ML services).