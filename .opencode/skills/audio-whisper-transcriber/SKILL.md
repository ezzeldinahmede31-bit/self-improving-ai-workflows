---
name: audio-whisper-transcriber
description: "Transcribes extracted audio files (mp3/wav) into text using local OpenAI Whisper / faster-whisper — no per-use API cost, no network upload, runs fully on-device. Use after media-downloader-extractor to turn a reel/video's speech into processable text. Trigger phrases: 'transcribe the audio', 'give me the transcript', 'what does it say', 'turn the reel into text'."
---

# AUDIO WHISPER TRANSCRIBER

## DIRECTIVE
Video content becomes text -> the LLM can read, summarize, and reason over it.
The transcription must be LOCAL (no API bill, no upload, no rate limits on your
content) and must surface word-level timing so the summary can be checked
against the actual media seconds.

## EXECUTION STEPS
1. **Backend:** use `faster-whisper` (ONNX + CPU/GPU) from the venv. It ships
   `ffmpeg` discovery via `imageio-ffmpeg`, so no system ffmpeg needed.
2. **Minimal reliable invocation:**
   ```python
   from faster_whisper import WhisperModel
   model = WhisperModel("base", device="cpu", compute_type="int8")
   segments, info = model.transcribe("/tmp/reel_xxx.mp3", beam_size=5,
                                     without_timestamps=False, language="ar")
   for s in segments: print(s.start, s.end, s.text)
   ```
   `base` (~75M) is enough for short reels; `large-v3` adds accuracy if the
   model can be downloaded. `device="cpu"` works; switch to `cuda`/`auto` if
   available.
3. **Language detection:** if unsure (mixed Arabic/English), omit `language=` and
   let the model auto-detect, then report it.
4. **Timestamp discipline:** emit `start–end : text` lines so the downstream
   summary can be cross-checked against media time (evidence over memory).
5. **Handoff:** inject the full transcript (with timestamps) into the
   conversation as "Video Content Context", then summarize.

## Rules
- Never invent words to fill gaps; if a segment is quiet/garbled, mark it
  `[inaudible x.y–x.z]`.
- If the model returns empty (too noisy), escalate rather than fabricate.
- Free model download (HuggingFace) may hit HF rate limits at first use — retry
  with `faster-whisper`'s retry env if needed.

## Local adaptation
Installed: `faster-whisper` + `ctranslate2` + `imageio-ffmpeg` in the venv
(`import imageio_ffmpeg; imageio_ffmpeg.get_ffmpeg_exe()`). `av` is also
present as a fallback muxer. Output transcript goes to `/tmp/transcript_xxx.txt`
and is read back with the `Read` tool so the user sees exactly what changed.
Pairs with `media-downloader-extractor` (download step) and
`text-content-summarizer` downstream if a summary is also wanted.