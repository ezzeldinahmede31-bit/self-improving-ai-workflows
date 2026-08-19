---
name: mlops-production
description: "Applies MLOps Production discipline to ship and operate ML models reliably: reproducible training runs, data and model versioning, automated pipelines, a model registry, deployment choices (batch, online, streaming), monitoring, drift detection, and retraining loops. Ties model lifecycles to the same build gates as the rest of the system. Use when the user says 'MLOps', 'model in production', 'training pipeline', 'model registry', 'deploy a model', 'monitor model drift', or 'retraining loop'."
---
# mlops-production

MLOps production is the discipline of treating a model as a continuously operated service, not a one-off artifact. This skill encodes the lifecycle — reproducible training, versioned data and models, automated pipelines, registry, deployment, monitoring, and retraining — so a model survives contact with real traffic.

## Core principles
- Reproducibility is non-negotiable: the same data, code, and config must reproduce the same training run.
- Data and model are versioned artifacts; a deployed model is always traceable to its exact inputs.
- Training is a pipeline: ingest, validate, feature, train, evaluate, register — automated and idempotent.
- Deployment is a choice among batch, online, and streaming inference, driven by the latency and freshness the feature needs.
- Monitoring is continuous: prediction distributions, performance metrics, and data drift all feed a retraining decision.
- A model that degrades silently is worse than no model; alerting and fallback are part of the deployment.

## Key patterns
- Pipeline: every training run goes through validate data, build features, train, evaluate against a held-out set, register.
- Model registry: each artifact carries a version, metrics, and lineage; promotion to production requires an eval gate.
- Shadow deployment: run the new model beside the old one and compare outputs before switching traffic.
- Online serving: wrap the model behind an API with input validation, batching, caching, and a fallback response.
- Drift monitor: track input feature distributions and prediction-confidence shifts; trigger retraining on change.
- Rollback path: keep the previous registry version deployable so a bad model is reverted in minutes.

## Applying this to n8n/Python automation
- Model every retraining run as an n8n workflow or Python script that records data, code, and config hashes in the run log.
- Register every promoted model in the model registry table with its eval metrics before it can be referenced.
- Wrap online inference in a node that validates inputs, measures latency, and logs predictions for drift analysis.
- Run the drift monitor on a schedule and have it open an approval task before retraining replaces the live model.
- Apply the same build gates to pipeline definitions that the rest of the system uses; a pipeline that fails validation never runs.

## Hard rules
- Never promote a model that has not passed its eval gate with recorded metrics.
- Never deploy a model without a rollback path to the previous registered version.
- Never train from data that has no recorded version and checksum.
- Never let a live model run without prediction logging and drift monitoring.

## Pairs with
designing-machine-learning-systems, machine-learning-design-patterns, evaluation, ai-engineering-foundation-models, build-gates-pipeline, n8n-workflow
