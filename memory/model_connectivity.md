# Model Connectivity — Recorded Blocker

Date: 2026-10-25
Status: **BLOCKED** — no free model is reachable through the current environment.

## What was tested

| Provider | Model | Method | Result |
|----------|-------|--------|--------|
| NVIDIA (integrate.api.nvidia.com) | deepseek-ai/deepseek-v4.1-flash | Direct HTTP POST `/v1/chat/completions` | **TimeoutError** — read operation timed out at 90s |
| NVIDIA | /v1/models (GET) | Reachability check | HTTP 200 — API is reachable |
| OpenRouter | — | API key present in env | Insufficient credits (never purchased) |
| opencode.ai | deepseek-v4.1-flash-free | Built-in provider | Free usage limit reached |
| deepseek-api | deepseek-chat | Built-in provider | Insufficient Balance |
| deepseek_official | deepseek-v4-flash | Built-in provider | Authentication Fails (invalid api key) |
| free-llm-gateway | deepseek-v4-flash | Built-in provider | Not Found |

## Analysis

- The NVIDIA API endpoint is **reachable** (HTTP 200 on `/v1/models`), but the
  chat completions endpoint **times out** on the actual inference request.
  This is a network/firewall issue, not a credentials issue.
- The `NVIDIA_API_KEY` environment variable is present and non-empty.
- No paid API calls were made. No credits were purchased. No trial was activated.
- The OpenCode CLI (`opencode` 1.18.10) is installed at
  `/home/ezzeldin/.opencode/bin/opencode` but cannot be used to prove
  connectivity because every configured provider fails.

## Conclusion

**Model connectivity is not proven.** The blocker is documented here rather
than claimed as resolved. All other remediation work (router, classification,
device_state fix, benchmark) was completed without requiring model output.

## Unblocking options (not executed — requires user action)

1. Fix outbound network path to `integrate.api.nvidia.com` POST endpoints.
2. Add a working free provider (e.g. Cerebras llama-3.1-8b, if key valid).
3. Enable OpenCode Go subscription for the free-tier fallback.