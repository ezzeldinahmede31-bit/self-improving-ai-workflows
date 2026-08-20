---
name: deep-learning-illustrated
description: Applies Jon Krohn, Grant Beyleveld & Aglaé Bassens' Deep Learning Illustrated to build a clear mental model of deep learning: the intuition behind neurons, layers, cost functions, backpropagation, CNNs, RNNs, and transformers, richly illustrated and code-supported with TensorFlow/Keras. Use when the user says 'explain deep learning visually', 'deep learning illustrated', 'Krohn', 'intuition for neural networks', 'what does a CNN actually do', 'transformers explained simply', or when deep learning concepts must be communicated or understood with strong intuition. Pairs with: deep-learning-with-python, dive-into-deep-learning, grokking-deep-learning, artificial-intelligence-modern-approach.
---
# Deep Learning Illustrated

## When to use
Use when the goal is deep intuition and clear communication: explaining what a network does, why layers compose, and how the modern architectures (CNN, RNN, transformer) actually work, with code support.

## Core mechanics
- Build the mental model from the bottom up: a neuron computes a weighted sum and applies a nonlinearity; a layer is many neurons; a network is layers composed.
- A cost function gives a single scalar quality score; training is gradient descent on that score through backpropagation.
- Visualize what each layer learns: early layers capture low-level edges and textures, later layers capture parts and objects.
- CNNs exploit spatial locality and shared weights for grids; RNNs carry state across sequence steps; transformers replace recurrence with attention over all positions.
- Choose an architecture by the structure of the data, not by fashion: convolutional for images, recurrent/attention for sequences, dense for tabular.
- Communicate with analogies and pictures, then back every intuition with a working Keras example.

## Verification
- For every concept taught, produce a running code example that demonstrates it.
- Check the intuition against measured behavior (layer activations, loss curves) before stating it as fact.

