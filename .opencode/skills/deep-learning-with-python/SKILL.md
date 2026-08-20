---
name: deep-learning-with-python
description: Applies Francois Chollet's Deep Learning with Python (Keras) to build, train, and ship deep learning models: the universal workflow of preparing data, choosing a model, training, evaluating, and tuning; convolutional networks for vision; recurrent and LSTM networks for sequences; and best practices for overfitting, regularization, and model deployment. Use when the user says 'Keras', 'Chollet', 'build a neural network in Python', 'image classification model', 'sequence model', 'transfer learning', 'regularize my network', or when designing a deep learning model end to end. Pairs with: deep-learning-illustrated, dive-into-deep-learning, machine-learning-pytorch-scikit-learn, deep-learning-cookbook, building-ml-powered-applications.
---
# Deep Learning with Python

## When to use
Use when building a neural network in Keras/TensorFlow, classifying images, modeling sequences, applying transfer learning, or following the end-to-end deep learning workflow. Best for practitioners who want proven Keras recipes, not just theory.

## Core mechanics
- Follow the universal workflow: define the problem, pick a metric, prepare data into tensors, choose an architecture and a loss, train with a fit loop, evaluate on held-out data, then iterate on failures.
- Prefer the sequential or functional Keras API; name layers and models meaningfully so the graph is readable.
- Fight overfitting before adding capacity: more data, data augmentation, dropout, L2 regularization, and early stopping.
- Match the architecture family to the data shape: dense for tabular vectors, convolutional for grids, recurrent/attention for sequences.
- Batch data with generators or tf.data; normalize inputs; use the correct final activation (sigmoid for binary, softmax for multi-class, linear for regression).
- Tune with the correct loss per task (binary crossentropy, categorical crossentropy, MSE) and monitor validation metrics, never training loss alone.

## Verification
- Prove each model with a held-out evaluation and a confusion matrix or per-class report before claiming success.
- Save and reload the trained model and verify inference on a never-seen sample.

