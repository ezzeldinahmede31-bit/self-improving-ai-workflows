---
name: machine-learning-engineering-burkov
description: Applies Andriy Burkov's Machine Learning Engineering to take a model from notebook to production: the ML engineering lifecycle, data collection and labeling, feature storage, model deployment (batch, online, edge), serving and monitoring, model versioning and retraining, and the CI/CD practices that keep ML systems reliable. The practical engineering book for a team that must run models as a service. Use when the user says 'machine learning engineering', 'Burkov', 'deploy a model', 'serve a model', 'monitor ML', 'model versioning', 'retraining', 'ML CI/CD', 'MLOps', or when a trained model must become a reliable production service. Pairs with: designing-machine-learning-systems, continuous-delivery-pipeline, n8n-self-hosting, sre-reliability-engineering, devops-handbook-flow.
---
# Machine Learning Engineering

Transfers Burkov's production discipline: a model in a notebook is an experiment; a model in a service is an engineering system with its own lifecycle.

## When to use
- Moving a trained model into production serving.
- Setting up monitoring, versioning, and retraining for ML.
- Choosing between batch, online, and edge deployment.

## Core practice
1. Design the data pipeline first: collection, labeling, validation, and feature storage that stays consistent with training.
2. Deploy the model at the right tier (batch scoring, online API, edge) matching latency, cost, and update frequency.
3. Monitor input distributions, output quality, and latency; detect drift and trigger retraining.
4. Version models and data together so any served prediction is reproducible.

## Engineering rules
- The training pipeline and the serving pipeline must use identical preprocessing.
- Model retraining is a deploy, not a magic fix: gate it with evaluation on recent data.
- Logging and monitoring are part of the model, not an afterthought.

## Verification discipline
- Test the serving path with the same features the training pipeline produces.
- Watch for silent distribution shift before accuracy complaints appear.
- Reproduce any served prediction from the logged data and model version.

## Pairs with
designing-machine-learning-systems, continuous-delivery-pipeline, n8n-self-hosting, sre-reliability-engineering, devops-handbook-flow.
