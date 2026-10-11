---
name: image-ocr-bridge
description: "Reads text out of images with cheap Gemini vision, then forwards the text-only result to a stronger model (ChatGPT/Claude/Kimi) without resending the image. Use when the user says 'اقرا اللي في الصورة', 'حول الصورة لنص', 'ocr this image', 'extract text from screenshot', 'ابعت الكلام اللي في الصورة لشات جيبيتي', or pastes an image needing text extraction plus reasoning."
---

# Image OCR Bridge

Two-hop pipeline that keeps vision cost tiny and reasoning strong:
cheap Gemini reads pixels → text-only forward to the strong model.

## Steps

1. Run: `venv/bin/python .opencode/skills/image-ocr-bridge/scripts/ocr_bridge.py <image> [--forward <model>] [--task "<instruction>"]`
   - OCR default: `google/gemini-3.5-flash-lite` (~$0.0004/image).
   - Forward defaults: `openai/gpt-4o-mini` (plan/reason),
     `anthropic/claude-haiku-4.5` (critique), `moonshotai/kimi-k2-0905`
     (long review). Text-only forward — the image is never re-uploaded.
2. Quote the extracted text, then the forwarded answer, then the usage line
   (stderr) as the spend record.
3. Supported inputs: png/jpg/jpeg/webp. Anything else → refuse, don't convert.

## Verification

- `ocr_bridge.py <test.png>` prints the visible lines verbatim (proven
  2026-10-11: 3/3 lines, 1122 tokens).
- `--forward` answer references ONLY extracted text (no invented content).
- Usage line present with ocr/forward/total tokens.

## Pairs with

- `multi-model-pipeline` — the forward leg reuses its roles, caps, and spend table.
- `text-optimizer` — compress OCR text before expensive forwards.
- `media-downloader-extractor` — frames/video input source.
