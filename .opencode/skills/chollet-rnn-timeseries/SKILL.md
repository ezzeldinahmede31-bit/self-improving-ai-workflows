---
name: chollet-rnn-timeseries
description: Deep dive into the recurrent-network and timeseries chapters of Chollet's Deep Learning with Python: RNNs and LSTM/GRU cells for sequences, the limitations of RNNs versus 1D convolutions and attention, timeseries forecasting with sliding windows, and temperature/weather forecasting examples. Use when the user says 'LSTM', 'GRU', 'recurrent network', 'timeseries forecasting with deep learning', 'sequence model', 'temperature forecasting', 'RNN vs attention', or when building a model over ordered data. Pairs with: deep-learning-with-python, deep-learning-illustrated, streaming-systems, time-series-analysis, data-pipelines-pocket-reference.
---
# RNN and Timeseries Deep Learning

## When to use
Use when the data is sequential: timeseries forecasting, sensor streams, or ordered text, and a recurrent or attention model is the candidate architecture.

## Core mechanics
- RNNs carry a hidden state across steps; LSTM and GRU cells manage what to remember and forget.
- Prepare timeseries as sliding windows: past observations predict the next value; split by time, not randomly.
- RNNs struggle with long-range dependence; 1D convolutions over time are fast alternatives, and attention relates distant steps directly.
- Forecast with the right horizon and metric (MAE, RMSE) and compare against a naive baseline (persist last value).
- The evaluation split must respect time order to avoid leakage.
- Choose architecture by sequence length: short sequences favor simple RNNs, long ones favor attention.

## Verification
- Report the forecast metric against a naive baseline on a time-ordered held-out segment.
- Confirm no future information leaks into the training windows.

