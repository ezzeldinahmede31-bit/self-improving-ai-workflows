---
name: efficient-processing-deep-neural-networks
description: Applies Sze, Chen, Yang & Emer's Efficient Processing of Deep Neural Networks to make deep models fast, small, and energy-efficient: the computation patterns of DNNs (data reuse, tiling), pruning, quantization, low-rank factorization, and hardware-aware design (dataflow, memory hierarchy, accelerators). Use when the user says 'quantize a model', 'prune a network', 'model compression', 'inference latency', 'efficient inference on edge', 'TinyML', 'hardware-aware deep learning', or when a model must run under compute or energy constraints. Pairs with: deep-learning-with-python, systems-performance-profiling, designing-machine-learning-systems, llm-deployment-optimization, embedded-systems-architecture.
---
# Efficient Processing of Deep Neural Networks

## When to use
Use when a trained deep model must run faster, smaller, or on constrained hardware (edge devices, phones, low-energy processors) and the trade-offs of each efficiency technique must be chosen deliberately.

## Core mechanics
- Understand the DNN computation pattern first: convolutions and matmuls dominate, with high data reuse that tiling and memory hierarchies exploit.
- Prune: remove unimportant weights or channels, then fine-tune to recover accuracy.
- Quantize: lower the numeric precision (8-bit, 4-bit, mixed) to shrink memory and speed up multiply-accumulate; calibrate after conversion.
- Factorize: replace large dense weight matrices with low-rank approximations where the error is tolerable.
- Design for the hardware: match the dataflow (stationary weights, stationary activations, or row-stationary) to the target memory system.
- Measure every technique: report accuracy, size, latency, and energy so the trade-off is explicit and honest.

## Verification
- After each compression step, re-evaluate on the held-out test set and record the accuracy delta.
- Benchmark latency and memory on the actual target device, not a simulated one.

