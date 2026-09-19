---
name: voice-assistant-testing
description: "Voice assistant testing distilled. Use when testing utterances, intents, slots, fallbacks, multi-turn dialogs, ASR and TTS quality."
---

# Voice Assistant Testing

## Purpose

Test voice experiences: utterance coverage per intent, slot filling, fallback grace, multi-turn memory, recognition plus synthesis quality.

## When to use

Use when the user says 'voice test', 'Alexa skill', 'utterance test', 'intent test', 'slot filling', 'dialog test', 'TTS test'.

## Steps

1. Cover each intent with varied phrasings plus accents and noise profiles.
2. Test slot filling: missing, ambiguous, and corrected values.
3. Verify fallbacks guide users forward instead of dead-ending.
4. Test multi-turn memory across interruptions.
5. Score recognition accuracy plus synthesis naturalness per release.

## Anti-patterns

- One canonical phrase per intent.
- Fallbacks that apologize and hang up the dialog.
- Slot errors looping without escape.
- Noisy-environment behavior never sampled.

## Example

Probe matrix: intent by phrasing by noise level, each cell asserting routed intent plus filled slots.

## Verification

Phrasing varied, slots resilient, fallbacks guiding, memory proven, quality scored.

## Pairs-with

fundamentals-speech-recognition, audio-whisper-transcriber, usability-testing-patterns, llm-eval-harness.
