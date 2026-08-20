---
name: deep-learning-cookbook
description: Applies Douwe Osinga's Deep Learning Cookbook to solve real problems with ready-to-adapt recipes in Keras: working with images, text, sound, and structured data; building recommendation and generative models; and transfer learning, all as concrete copy-paste-and-adapt solutions. Use when the user says 'deep learning recipe', 'Deep Learning Cookbook', 'Osinga', 'adapt a Keras example', 'build a recommendation model', 'generate text with Keras', 'cookbook for deep learning', or when a proven recipe is the fastest route to a working model. Pairs with: deep-learning-with-python, deep-learning-cookbook, machine-learning-pytorch-scikit-learn, collective-intelligence-in-action.
---
# Deep Learning Cookbook

## When to use
Use when the fastest path to a working model is adapting a proven recipe: image, text, audio, and structured-data tasks with Keras, including recommendation and generation.

## Core mechanics
- Treat each chapter as a recipe: ingredients (data), method (architecture and training), and expected result.
- Adapt, never copy blindly: swap the input/output shape, the last layer and loss to match your task.
- For images use convolution stacks; for text use embedding plus recurrent or attention layers; for tabular use dense layers.
- Recommendations are a ranking problem: learn embeddings of users and items and score their match.
- Generation samples from a trained distribution: character or word language models produce new text.
- Transfer learning reuses a pretrained backbone so small datasets still train well.
- Keep the evaluation from the recipe as the baseline for your adapted version.

## Verification
- Run the adapted recipe on a small slice of your data before the full dataset.
- Compare the adapted model's metric to the recipe's reported baseline and report the delta honestly.

