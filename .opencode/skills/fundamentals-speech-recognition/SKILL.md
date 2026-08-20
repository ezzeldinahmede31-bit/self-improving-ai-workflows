---
name: fundamentals-speech-recognition
description: Applies Rabiner & Juang's Fundamentals of Speech Recognition to build speech systems on the classic foundations: the speech signal and its representation, the hidden Markov model framework, acoustic modeling, language modeling, and the decoding of speech into text. Use when the user says 'speech recognition', 'Rabiner Juang', 'HMM for speech', 'acoustic model', 'feature extraction speech', 'decoding', or when building an ASR system from fundamentals. Pairs with: speech-language-processing, foundations-statistical-nlp, audio-whisper-transcriber, all-of-statistics.
---
# Fundamentals of Speech Recognition

## When to use
Use when building a speech system on the classic foundations, or when the user asks about HMMs for speech, acoustic modeling, or decoding speech into text.

## Core mechanics
- Represent the speech signal with features.
- Model speech units with hidden Markov models.
- Build acoustic models from labeled audio.
- Combine with a language model.
- Decode the most likely word sequence.
- Evaluate with word error rate.

## Verification
- Test the recognizer on a small labeled set and report word error rate.
- Verify feature extraction reproduces reference values.
- Check that the language model improves decoding.
