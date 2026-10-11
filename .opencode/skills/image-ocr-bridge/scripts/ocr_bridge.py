#!/usr/bin/env python3
"""ocr_bridge.py — image -> Gemini OCR text -> optional stronger model.

Usage:
  ocr_bridge.py <image.png|jpg> [--forward openai/gpt-4o-mini] [--task "..."]
                                [--ocr-model google/gemini-3.5-flash-lite]
                                [--max-tokens N]

Key: opencode auth.json openrouter.key (never printed, never logged).
Step 1 (Gemini) extracts text; step 2 forwards text-only (no image resend).
Prints extracted text, then forwarded answer; usage totals go to stderr.
"""
import base64
import json
import sys
import urllib.request
from pathlib import Path

AUTH = Path("/home/ezzeldin/.local/share/opencode/auth.json")


def call(key, model, messages, max_tokens):
    body = json.dumps({"model": model, "messages": messages,
                       "max_tokens": max_tokens}).encode()
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions", data=body,
        headers={"Authorization": "Bearer " + key,
                 "Content-Type": "application/json"})
    d = json.load(urllib.request.urlopen(req, timeout=180))
    return d["choices"][0]["message"]["content"], d.get("usage", {})


def main() -> int:
    a = sys.argv[1:]
    if not a or a[0].startswith("--"):
        print("usage: ocr_bridge.py <image> [--forward MODEL] [--task TEXT] "
              "[--ocr-model ID] [--max-tokens N]")
        return 1
    img, forward, task, ocr_model, cap = a[0], None, "", \
        "google/gemini-3.5-flash-lite", 400
    i = 1
    while i < len(a):
        if a[i] == "--forward":
            forward = a[i + 1]; i += 2
        elif a[i] == "--task":
            task = a[i + 1]; i += 2
        elif a[i] == "--ocr-model":
            ocr_model = a[i + 1]; i += 2
        elif a[i] == "--max-tokens":
            cap = int(a[i + 1]); i += 2
        else:
            i += 1
    ext = Path(img).suffix.lower()
    if ext not in (".png", ".jpg", ".jpeg", ".webp"):
        print(f"ERROR: unsupported image type '{ext}'")
        return 1
    mime = "image/jpeg" if ext in (".jpg", ".jpeg") else \
        f"image/{ext.lstrip('.')}"
    b64 = base64.b64encode(Path(img).read_bytes()).decode()
    key = json.loads(AUTH.read_text())["openrouter"]["key"]
    text, u1 = call(key, ocr_model, [{
        "role": "user", "content": [
            {"type": "text", "text": "Extract ALL text visible in this "
                                    "image, line by line. Nothing else."},
            {"type": "image_url", "image_url": {
                "url": f"data:{mime};base64," + b64}}]}], cap)
    print(text)
    t1 = u1.get("total_tokens", 0)
    if forward:
        prompt = (task + "\n" if task else
                  "Process the following extracted image text:\n") + text
        ans, u2 = call(key, forward, [{"role": "user",
                                       "content": prompt}], cap)
        print("---forwarded---")
        print(ans)
        t2 = u2.get("total_tokens", 0)
    else:
        t2 = 0
    print(f"[usage: ocr={t1} forward={t2} total={t1 + t2} tokens]",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
