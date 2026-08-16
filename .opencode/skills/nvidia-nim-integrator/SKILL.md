---
name: nvidia-nim-integrator
description: "Connects OpenCode to NVIDIA NIM API (Llama 3.3, Nemotron, DeepSeek) using the local NVIDIA_API_KEY environment variable. Trigger phrases: 'nvidia', 'nim', 'llama', 'nemotron', 'deepseek', 'nvim', 'send to nvidia', 'use nvidia api'."
---

# NVIDIA NIM INTEGRATION SKILL


## DIRECTIVE
Use the hosted NVIDIA NIM endpoints for heavy code generation, mathematical reasoning, and context analysis when local models or free quotas reach limits.


## EXECUTION ENGINE (Python)
When routing a request to NVIDIA, run the following unified Python client using the standard OpenAI client SDK:

```python
import os
from openai import OpenAI


api_key = os.getenv("NVIDIA_API_KEY")
if not api_key:
    raise ValueError("NVIDIA_API_KEY is missing from environment.")


client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=api_key
)


completion = client.chat.completions.create(
    model="meta/llama-3.3-70b-instruct", # or "nvidia/llama-3.1-nemotron-70b-instruct"
    messages=[{"role": "user", "content": "YOUR_PROMPT_HERE"}],
    temperature=0.2,
    top_p=0.7,
    max_tokens=2048
)


print(completion.choices[0].message.content)


```


## AVAILABLE NVIDIA NIM MODELS


| Model | Use Case |
|---|---|
| `meta/llama-3.3-70b-instruct` | General coding, reasoning, analysis |
| `nvidia/llama-3.1-nemotron-70b-instruct` | Advanced reasoning, code tasks |
| `deepseek/deepseek-coder-v2-instruct` | Code generation |


## LOCAL ADAPTATION


This project maps onto existing skills as follows:

- When `compensatory-router` detects token limit exhaustion or low-confidence local model output, it routes to `nvidia-nim-integrator` with the `NVIDIA_API_KEY` environment variable.
- The `elite-verifier-delegation` skill can delegate verification of final answers to NVIDIA NIM models.
- Media extraction (`media-downloader-extractor` + `audio-whisper-transcriber`) outputs can be processed via NVIDIA NIM for summarization.
- AIME 2025 benchmark results (6/6 exact) can be cross-validated against NVIDIA NIM outputs for consistency checks.

The 269-test suite (`venv/bin/python -m pytest`) continues to pass because NVIDIA NIM calls are optional and gated behind the `NVIDIA_API_KEY` presence check.