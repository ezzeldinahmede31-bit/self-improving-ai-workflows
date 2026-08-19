---
name: machine-learning-yearning
description: Applies Andrew Ng's Machine Learning Yearning to make the high-leverage decisions that determine whether an ML project succeeds: setting a single-number evaluation metric and an optimistic baseline for calibration, analyzing errors by category to prioritize the next move, structuring train/dev/test sets to avoid data skew, handling the bias-variance spectrum, and deciding when more data, more features, or a different architecture is the right investment. Use when the user says 'Machine Learning Yearning', 'Andrew Ng', 'error analysis', 'dev set', 'human-level performance', 'avoidable bias', 'data skew', 'prioritize ML work', 'should I collect more data', or when an ML project is stalled and the next high-value action is unclear. Pairs with: designing-machine-learning-systems, building-ml-powered-applications, evidence-over-memory, test-time-compute-scaling.
---
# Machine Learning Yearning

Transfers Ng's decision framework for ML projects: pick one number, set a baseline, and let error analysis tell you the next move instead of guessing.

## When to use
- An ML project is stuck and the next action is unclear.
- Deciding whether to collect more data, add features, or change architecture.
- Setting up train/dev/test and metrics so decisions are evidence-driven.

## Core method
1. Choose a single-number evaluation metric (plus a satisficing metric if needed) and a baseline such as human-level performance.
2. Analyze dev-set errors by category and tally the causes — work on the largest bucket first.
3. Place train/dev/test from the same distribution; when real-world data differs, add the realistic subset to dev/test to measure the skew.

## Decisions
- Avoidable bias (gap to baseline) vs variance (gap between train and dev) tells you whether to improve the model or add data/regularization.
- More data helps when variance is the problem; a bigger model or better features help when bias is.
- Move fast by testing hypotheses on the dev set with error analysis, not by blind retraining.

## Verification discipline
- The dev set is the honest scoreboard; the test set is used rarely, for final confirmation.
- Error analysis categories must be measured, not guessed.
- Every improvement is accepted only if the dev metric improves.

## Pairs with
designing-machine-learning-systems, building-ml-powered-applications, evidence-over-memory, test-time-compute-scaling.
