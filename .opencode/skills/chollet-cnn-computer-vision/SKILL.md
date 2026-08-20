---
name: chollet-cnn-computer-vision
description: Deep dive into the convolutional-network and computer-vision chapters of Chollet's Deep Learning with Python: convolution filters, pooling, data augmentation, the VGG/inception/resnet evolution, transfer learning with pretrained backbones, and fine-tuning for new domains. Use when the user says 'CNN architecture', 'convolution explained', 'data augmentation for images', 'transfer learning for vision', 'fine-tune a pretrained model', 'image feature extraction', or when designing a convolutional model for an image task. Pairs with: deep-learning-with-python, deep-learning-vision-systems, computer-vision-algorithms-applications, efficient-processing-deep-neural-networks.
---
# CNN and Computer Vision with Chollet

## When to use
Use when designing or improving a convolutional network for images: choosing the architecture, using augmentation, and applying transfer learning.

## Core mechanics
- Convolutions detect local patterns with shared weights; stacking layers composes edges into parts into objects.
- Pooling downsamples and adds translation invariance; strides do the same with learnable parameters.
- Data augmentation (rotation, flip, zoom, color jitter) is the cheapest regularization for vision.
- Modern families (VGG deeper, Inception wider, ResNet skip connections) trade depth, width, and gradients.
- Transfer learning is the default: pretrained backbone extracts features; replace the top and fine-tune.
- Freeze early layers, fine-tune later ones; use a small learning rate for the fine-tuning pass.

## Verification
- Visualize sample predictions and misclassifications to find where the model fails.
- Compare transfer learning versus training from scratch on the same data and report the delta.

