---
name: ml-model-testing
description: "ML model testing distilled. Use when testing model quality, train-serve skew, data slices, fairness, robustness, monitoring hooks."
---

# ML Model Testing

## Purpose

Test models as systems: offline quality plus slices, train-serve parity, robustness, fairness checks, monitoring from day one.

## When to use

Use when the user says 'model testing', 'ML evaluation', 'train-serve skew', 'slice metrics', 'fairness test', 'robustness test'.

## Steps

1. Evaluate on held-out data with task metrics plus critical slices.
2. Test train-serve parity: same features, same transforms, same outputs.
3. Probe robustness: noisy, shifted, and adversarial-ish inputs.
4. Check fairness slices defined with stakeholders.
5. Ship with monitoring: drift, quality, and feedback loops wired.

## Anti-patterns

- Single aggregate metric hiding failing slices.
- Leakage from test data into training.
- Serve path reimplementing training transforms.
- No monitoring, so decay discovered by users.

## Example

Python:

```python
assert slice_metric(y_true[mature], y_pred[mature]) >= FLOOR
assert serve_vector(row) == train_vector(row)
```

## Verification

Slices reported, parity proven, robustness probed, fairness checked, monitoring live.

## Pairs-with

designing-ml-systems, building-ml-powered-applications, machine-learning-design-patterns, data-drift-concept-drift-detection-v2.
