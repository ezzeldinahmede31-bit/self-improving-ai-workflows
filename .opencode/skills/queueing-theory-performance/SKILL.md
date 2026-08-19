---
name: queueing-theory-performance
description: Applies classic queueing theory to performance modeling and capacity planning: the fundamental queueing model (arrivals, service, discipline), Little's law, the M/M/1 and M/M/c queues and their steady-state behavior, utilization and response time, and the discipline of measuring systems so the model matches reality. Use when the user says 'queueing theory', 'Little law', 'M/M/1', 'response time', 'utilization', 'arrival rate', 'service rate', 'capacity planning', 'queue length', 'performance model', or when predicting how a service behaves under load.
---

# Queueing Theory and Performance Evaluation (various classic texts)

Queueing theory is the math of waiting: how arrival rate, service rate, and variability shape response time. This skill applies it to real services and capacity decisions.

## The queueing model

- A queue has arrivals, a service process, a discipline, and a capacity; define all four before analyzing.
- Utilization is the arrival rate over the service rate; the system is unstable when it exceeds one.
- Steady state means the long-run averages exist; transient behavior needs simulation or different math.

## Little's law

- Little's law: the average number in the system equals the arrival rate times the average time spent.
- It holds under very weak assumptions and gives one relation the data must satisfy.
- Measure any two quantities and the third is implied; use it to sanity-check measurements.

## M/M/1 and M/M/c

- Exponential arrivals and service give closed-form results for average queue length and response time.
- As utilization nears one, response time grows without bound; the curve is steep near the cliff.
- More servers (M/M/c) reduce the queue only when the workload can be split across them.

## Modeling discipline

- Measure the real arrival and service distributions before choosing the model.
- Variability beyond exponential makes queues longer; the coefficient of variation tells how far off the formula is.
- Use the model to size capacity, then verify with load tests; the model guides, the test confirms.

## Pairs with
systems-performance-profiling, rate-limit-and-cost-guard, sre-reliability-engineering, building-data-heavy-applications, thinking-probabilistic
