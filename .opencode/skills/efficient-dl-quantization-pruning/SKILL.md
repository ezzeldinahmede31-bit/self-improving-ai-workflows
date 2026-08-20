---
name: efficient-dl-quantization-pruning
description: Deep dive into model compression from Sze et al. Efficient Processing of Deep Neural Networks: weight and activation quantization, pruning and sparsity, knowledge distillation, and their combined effect on model size, latency, and accuracy. Use when the user says 'quantize the model', 'prune weights', 'model compression', '8-bit inference', 'sparsity', 'knowledge distillation', 'reduce model size', or when a model must get smaller and faster with controlled accuracy loss. Pairs with: efficient-processing-deep-neural-networks, llm-deployment-optimization, deep-learning-with-python, systems-performance-profiling.
---
# Model Quantization and Pruning

## When to use
Use when a trained model must be compressed: smaller, faster, and lower-energy while keeping accuracy within an agreed tolerance.

## Core mechanics
- Quantization lowers numeric precision: 32-bit to 8-bit or 4-bit weights and activations shrink memory and speed compute.
- Post-training quantization converts a trained model directly; quantization-aware training retrains to recover accuracy.
- Pruning removes low-importance weights or channels; retrain (or fine-tune) after pruning to recover accuracy.
- Sparsity exploits zeros in the pruned weights with specialized kernels.
- Knowledge distillation trains a small student model to imitate a large teacher, often beating direct small training.
- Combine techniques carefully: each layer interacts, so measure the combined effect.

## Verification
- After every step, report accuracy, size, and latency together so the trade-off is explicit.
- Measure inference on the real target device, not a simulation.

