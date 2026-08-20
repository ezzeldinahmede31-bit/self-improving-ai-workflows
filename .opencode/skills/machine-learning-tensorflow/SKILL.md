---
name: machine-learning-tensorflow
description: Applies Tom Hope, Yehezkel Resheff & Itay Lieder's Machine Learning with TensorFlow to build machine learning models with TensorFlow: the TensorFlow programming model, linear regression and classification, neural networks, CNNs, RNNs, embeddings, and best practices for training and evaluating models at scale. Use when the user says 'machine learning with TensorFlow', 'Hope Resheff Lieder', 'build a model in TensorFlow', 'TensorFlow classification', 'embedding with TensorFlow', or when implementing machine learning directly on the TensorFlow stack. Pairs with: deep-learning-with-python, machine-learning-pytorch-scikit-learn, dive-into-deep-learning, experiment-code.
---
# Machine Learning with TensorFlow

## When to use
Use when building machine learning models directly on TensorFlow and wanting a guided path from linear models through neural networks, CNNs, RNNs, and embeddings.

## Core mechanics
- Understand the TensorFlow model: graphs (or eager execution) plus variables that training updates.
- Start with linear regression and logistic classification as the base models; they establish the loss and training loop.
- Compose neural networks from layers; add regularization and monitor validation to keep generalization.
- Use convolution for image tasks and recurrent/embedding structures for sequences and text.
- Embeddings map categorical tokens into dense spaces that capture similarity.
- Manage the data pipeline so batches feed the model without blocking the GPU.
- Evaluate on held-out data with the task-appropriate metric and record it.

## Verification
- Confirm the training loop is deterministic on a fixed seed.
- Run the final model on a held-out test set and compare to a simple baseline before claiming success.

