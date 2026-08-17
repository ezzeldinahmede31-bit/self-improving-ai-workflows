---
name: machine-learning-design-patterns
description: "Applies Lakshmanan, Robinson & Munn's Machine Learning Design Patterns to solve recurring ML engineering problems with proven templates: data representation patterns (hashed, embedding, feature cross, multimodal), problem representation (reframing regression to classification, multiclass to multilabel), model patterns (design patterns for overfitting, ensembles, cascade), resilient ML (checkpointing, stateless serving, batch serving, reproducible splitting, and the right patterns for the full ML pipeline). Use when the user says 'ML design pattern', 'reframe this ML problem', 'feature cross', 'embedding', 'resampling imbalanced data', 'overfitting', 'ensembles', 'cascade classifier', 'checkpoint', 'stateless serving', 'batch serving', 'reproducible data split', 'leakage', 'multilabel', 'model versioning', or when a recurring ML engineering problem needs a proven, named solution instead of an ad-hoc hack. Pairs with: designing-machine-learning-systems, data-analysis, experiment-code, algorithm-design-manual-war-stories, evaluation."
---

# Machine Learning Design Patterns

The ML Design Patterns book catalogs ~30 named solutions for problems every ML
engineer hits repeatedly — data, problem, model, and resilience. Its value: a
shared vocabulary and a proven template, so you solve the named problem with the
known-good pattern instead of improvising.

## When to use

- A training or serving problem that feels "common" — check the catalog.
- Reframing a poorly-posed ML problem.
- Hardening a pipeline against data problems, leakage, or serving failure.

## The pattern families

### 1. Data representation patterns
- **Hashed feature**: replace an unbounded categorical with a bounded hash
  bucket — handles new values, at the cost of collisions.
- **Embedding**: map categorical/high-cardinality data into dense vectors that
  capture similarity — powerful for text, users, items.
- **Feature cross**: multiply/create combinations of features so a linear model
  can express interactions (the trick behind much CTR prediction).
- **Multimodal input**: combine distinct data types (text + image + numeric) via
  separate encoders joined at the model.

### 2. Problem representation patterns
- **Reframing**: turn regression into classification (or vice versa) when the
  metric and business need fit better; turn multiclass into multilabel when
  examples carry multiple true labels.
- **Imbalanced data**: resample (oversample minority / undersample majority),
  use class weights, or change the metric — pick by the cost of each error type.
- **Neutral class / distinct labels**: add an explicit neutral or "other" class
  to absorb noise instead of forcing every example into a wrong bucket.

### 3. Model patterns
- **Overfitting countermeasures**: regularization, early stopping, dropout, more
  data, and honest validation — the pattern is "validate on data the model never
  saw, repeatedly".
- **Ensembles**: bagging, boosting, stacking — combine weak models to reduce
  variance and bias. Use when single models plateau.
- **Cascade**: a cheap model filters, an expensive model refines — use when the
  expensive model only needs to see the hard cases.
- **Two-slot / rebalancing**: retrain the model on a data sample whose label
  distribution is adjusted to the production prevalence.

### 4. Resilient ML patterns
- **Checkpointing**: persist training state so a crash resumes instead of
  restarting — saves hours on long training runs.
- **Stateless serving**: keep the serving container stateless (model + config only)
  so it scales and fails over cleanly; never store mutable state in the serving
  process.
- **Batch serving**: precompute predictions in bulk (scheduled) when latency is
  not interactive — cheaper and easier to audit than online inference.
- **Reproducible splitting**: split by a stable, hash-based key on the unit of
  data (e.g., user id, not rows) to prevent **data leakage** — the single most
  common silent ML bug is information leaking from test into training via
  duplicated or grouped rows.

## How to use the catalog
- When a problem arises, name it against the catalog first; the pattern gives the
  shape of the fix. Then adapt with real data (see `data-analysis`) and verify
  with held-out evaluation (see `evaluation`).
- Patterns compose: e.g., hashed features + feature cross + stateless serving is
  a standard high-volume pipeline.

Pairs with: designing-machine-learning-systems (lifecycle context), data-analysis
(statistical checks), experiment-code (implementation), evaluation (verification).