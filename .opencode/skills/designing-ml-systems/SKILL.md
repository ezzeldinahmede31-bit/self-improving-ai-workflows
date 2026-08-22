---
name: designing-ml-systems
description: Applies Chip Huyen's Designing Machine Learning Systems to take ML models from notebooks to production: the ML system lifecycle (data collection, feature engineering, training, evaluation, deployment, monitoring, retraining), data quality and drift (data distribution shift, concept drift), feature stores and online/offline consistency, model deployment patterns (batch, online, streaming), monitoring and observability for models, feedback loops, and the practical reality that ML systems fail on data and operations far more than on modeling. Use when the user says 'put my model in production', 'ML system design', 'data drift', 'concept drift', 'feature store', 'train-serve skew', 'model monitoring', 'retraining', 'online vs batch inference', 'ML observability', 'design an ML pipeline', 'reproducibility', 'MLOps', or when taking any model to production reliably. Pairs with: data-analysis, experiment-code, machine-learning-design-patterns, state-machine-persistence, n8n-rag-vector-qa, evaluation.
---

# Designing Machine Learning Systems (Chip Huyen) Skill

## Core Philosophy: Systems Over Models

> ML systems are complex because they consist of many components and involve many stakeholders. Unique because they're data-dependent. This book takes a **systems approach** — consider all components holistically, not just algorithms.

**Key distinction**: ML in research ≠ ML in production
- Research: model-centric, static datasets, offline metrics
- Production: data-centric, evolving data, business metrics, operational concerns

---

## Chapter 1: When to Use ML

**Use ML when**:
- No clear rules exist (complex patterns)
- Problem involves large-scale data
- System must adapt to new data

**Don't use ML when**:
- Simple deterministic rules work
- Data is insufficient/noisy
- Interpretability is legally required

---

## Chapter 2: ML System Design Requirements

| Requirement | Definition | Techniques |
|-------------|------------|------------|
| **Reliability** | Performs consistently under various conditions | Retries, fallbacks, circuit breakers |
| **Scalability** | Handles increasing data/workload | Distributed training, batch/streaming inference |
| **Maintainability** | Easy to update/improve | Modular pipelines, versioning, testing |
| **Adaptability** | Adjusts to changing conditions | Monitoring, retraining, continual learning |

**Design cycle**: Iterative — feedback from deployment → monitoring → improvement.

---

## Chapter 3: Data Engineering Fundamentals

| Aspect | Key Points |
|--------|------------|
| **Formats** | Parquet (columnar, analytics), Avro/Protobuf (schema, streaming), JSON (interop) |
| **Storage** | Data lake (raw), warehouse (curated), feature store (ML-ready) |
| **Processing** | Batch (Spark/Flink), streaming (Kafka/Flink), hybrid (Iceberg/Delta Lake) |
| **Quality** | Schema validation, anomaly detection, data contracts |

**Rule**: Data quality > model sophistication.

---

## Chapter 4: Training Data

| Concern | Practice |
|---------|----------|
| **Collection** | Event-driven, not batch dumps; capture context |
| **Labeling** | Active learning, weak supervision, human-in-the-loop |
| **Splits** | Temporal (not random) — prevent leakage; train/val/test by time |
| **Distribution shifts** | Covariate shift (P(X) changes), label shift (P(Y) changes), concept drift (P(Y\|X) changes) |

---

## Chapter 5: Feature Engineering

| Type | Description | Example |
|------|-------------|---------|
| **Engineered** | Domain knowledge, manual | User age, transaction count |
| **Learned** | Embeddings from models | BERT embeddings, graph embeddings |
| **Crossed** | Feature interactions | user_id × item_id |

**Critical**: 
- Feature store = single source of truth for features (online/offline consistency)
- Prevent leakage: features must not use future data
- Generalization: features should work on unseen data

---

## Chapter 6: Model Development & Offline Evaluation

| Phase | Focus |
|-------|-------|
| **Objective function** | Business metric → ML metric (e.g., revenue → CTR → log-loss) |
| **Architecture** | Start simple (linear, tree-based); add complexity only when justified |
| **Evaluation** | Hold-out test set + backtesting on temporal slices |
| **Baselines** | Always compare against simple heuristics (popularity, last value) |

---

## Chapter 7: Model Deployment Patterns

| Pattern | Latency | Throughput | Use Case |
|---------|---------|------------|----------|
| **Batch prediction** | High (hours) | Very high | Recommendations, nightly scoring |
| **Online prediction** | Low (ms) | Moderate | Fraud detection, real-time ranking |
| **Streaming prediction** | Low (ms) | High | Real-time personalization, anomaly detection |
| **Edge/device** | Lowest | Low | Mobile, IoT, privacy-sensitive |

**Continual learning stages**:
1. Manual retraining from scratch
2. Automated retraining (scheduled)
3. Stateful continual learning (fine-tuning on new data)
4. Automated + stateful with validation gates

---

## Chapter 8: Data Distribution Shifts & Monitoring

**Monitoring layers**:

| Layer | Metrics | Tools |
|-------|---------|-------|
| **Operational** | Latency, throughput, CPU, memory, error rate | Prometheus, Datadog |
| **Data** | Feature distributions, schema violations, missing values | WhyLabs, Evidently |
| **Model** | Prediction drift, accuracy (when labels available), confidence calibration | Custom, Arize |
| **Business** | Conversion, revenue, user satisfaction | BI tools |

**Shift detection**: Statistical tests (KS, PSI, chi-square) on feature/prediction distributions.

---

## Chapter 9: Continual Learning & Test in Production

| Strategy | Description | Risk |
|----------|-------------|------|
| **Shadow mode** | New model runs parallel, no traffic | Safe, no real feedback |
| **Canary** | Small % traffic to new model | Limited blast radius |
| **A/B test** | Randomized controlled experiment | Statistical rigor needed |
| **Bandit** | Dynamic allocation based on reward | Complex, exploration cost |

**Validation gates before promotion**:
- Offline metrics on recent data
- Shadow mode performance
- Canary with automated rollback
- Business metric guardrails

---

## Chapter 10: Infrastructure & MLOps Tooling

| Layer | Components | Examples |
|-------|------------|----------|
| **Storage/Compute** | Object storage, GPUs, TPUs | S3, GCS, AWS/GCP/Azure |
| **Orchestration** | Workflow schedulers | Airflow, Prefect, Dagster, Argo, Metaflow |
| **ML Platform** | Feature store, model registry, deployment | Feast, MLflow, Vertex AI, SageMaker |
| **Monitoring** | Drift detection, alerting | WhyLabs, Evidently, Prometheus |

**Cloud repatriation**: Large companies moving from cloud to private DC for cost.

---

## Chapter 11: Human Aspects

| Aspect | Practice |
|--------|----------|
| **Team structure** | ML platform team (shared infra) + applied ML teams (use cases) |
| **Communication** | Translate between business, data, engineering |
| **Ethics** | Fairness, bias, privacy, transparency by design |

---

## Decision Checklist for Production ML

Before deploying, verify:
1. **Business metric defined** and tracked?
2. **Data pipeline** tested for schema evolution, backfill, reprocessing?
3. **Feature store** provides online/offline consistency?
4. **Model registry** versions model + data + code + config together?
5. **Deployment pattern** matches latency/throughput needs?
6. **Monitoring** covers operational + data + model + business layers?
7. **Retraining pipeline** automated with validation gates?
8. **Rollback** tested and < 5 minutes?
9. **Shadow/canary** infrastructure ready?
10. **Cost per prediction** known and budgeted?

---

## Anti-Patterns to Avoid

- ❌ "Model is done when accuracy hits 95%" (ignores drift, ops)
- ❌ Training on random splits (temporal leakage)
- ❌ No feature store → train/serve skew
- ❌ Manual retraining as only strategy
- ❌ Monitoring only accuracy (misses data drift)
- ❌ Deploying without shadow/canary
- ❌ Treating ML platform as afterthought

---

## Trigger Phrases

`put my model in production`, `ML system design`, `data drift`, `concept drift`, `feature store`, `train-serve skew`, `model monitoring`, `retraining`, `online vs batch inference`, `ML observability`, `design an ML pipeline`, `reproducibility`, `MLOps`

---

## Pairings

- `data-analysis` — statistical validation
- `experiment-code` — iterative model development
- `machine-learning-design-patterns` — recurring ML engineering patterns
- `state-machine-persistence` — stateful pipelines
- `n8n-rag-vector-qa` — RAG as ML system
- `evaluation` — systematic evaluation