---
name: agent-reach
version: "1.1.0"
description: "Read and search external sources through Agent Reach channels (YouTube, GitHub, Reddit, Twitter, Facebook, Instagram, LinkedIn, RSS, web). Use when the task needs content from a feed, a video, or another platform an installed channel covers."
---

# agent-reach

Give the agent eyes on the whole internet: one CLI (`agent-reach`) routes each platform to its best backend (OpenCLI, twitter-cli, bili-cli, rdt-cli, yt-dlp, mcporter, gh CLI, Jina Reader) with automatic fallback. Installed from the official source: `https://github.com/Panniantong/Agent-Reach` (MIT). Install guide: `https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/install.md`.

## Binary & environment (this machine)

- Binary: `~/.agent-reach-venv/bin/agent-reach` (v1.5.0, dedicated venv — never the project venv)
- Config/cookies: `~/.agent-reach/` (mode 600, local only — never commit, never log)
- yt-dlp: venv build 2026.08.19 with `--js-runtimes node` in `~/.config/yt-dlp/config`
- Put the venv first on PATH when calling: `export PATH="$HOME/.agent-reach-venv/bin:$PATH"`

## Discipline

1. **Doctor first on failure:** run `agent-reach doctor` if any call fails; a channel can be installed but unauthenticated.
2. **Never a wrapper:** v1.5.0 has NO `get` command — Agent Reach installs/selects upstream tools, and the AGENT calls them directly (yt-dlp, gh, curl+Jina, feedparser). Agent Reach is the selector/installer/router.
3. **Keep outputs bounded:** transcripts/feeds can be long — extract, then trim to what the task needs.

```
export PATH="$HOME/.agent-reach-venv/bin:$PATH"
agent-reach doctor                       # health check all channels
agent-reach install --env=auto           # safe read-only check (default)
agent-reach install --env=auto --dry-run # preview what --system would change
agent-reach transcribe <url>             # Whisper via Groq/OpenAI (needs API key)
agent-reach skill --install              # register SKILL.md into agent dirs
```

## Channels

### Live on this machine (verified via doctor)

| Channel | How the agent calls it | Notes |
|---------|------------------------|-------|
| `youtube` | `yt-dlp --skip-download --print "%(title)s" <url>` for info; `--write-auto-sub --sub-langs ar,en --skip-download` for subtitles | Proven live on this machine (title+duration+AR/EN subs extracted) |
| `rss` | any feed URL via feedparser/curl | Clean text, no login |
| `web` | `curl https://r.jina.ai/<URL>` | Jina Reader, no key |
| `v2ex` | public API | Hot posts, threads, replies |
| `bilibili` | search API direct | Full subs need `bili-cli` |

### Unlockable (needs approval or login)

| Channel | Requirement |
|---------|-------------|
| `github` (private/issues/PRs) | `gh` CLI install (needs sudo approval) |
| `exa` semantic search | `mcporter` via `npm install -g` (needs sudo approval) |
| `twitter`, `reddit`, `facebook`, `instagram`, `linkedin`, `xiaohongshu` | Cookie login per channel — ask the agent "ثبّتلي Twitter" etc. |

## Security rules (from upstream docs)

- Cookies stay in `~/.agent-reach/` (600) — never in prompts, logs, or git.
- `install` is check-only by default. `--system` ONLY after explicit user approval. Never `sudo` silently.
- Never clone repos or write files into the agent workspace; tools live in `~/.agent-reach/tools/`, temp in `/tmp/`.
- Login channels carry ban risk (platforms detect non-browser API calls) — **use burner accounts, never the personal account**.

## n8n integration

Call the CLI from an n8n Code node or Execute Command node on a self-hosted instance:

```
Schedule Trigger → Execute Command (agent-reach get youtube.transcript <url> --max-tokens 4000)
  → Code (normalize) → store/notify
```

Keep collection (Agent Reach) separate from interpretation (later LLM node), same pattern as `seven-ai-tools-humam`.

## Pairs with

| Skill | Why |
|-------|-----|
| `media-downloader-extractor` | Download the actual video/audio after Agent Reach finds it (yt-dlp) |
| `audio-whisper-transcriber` | Local transcription when no subtitles exist |
| `seven-ai-tools-humam` | Same collect-then-normalize n8n pattern for AI answers |
| `evidence-over-memory` | Paste real fetched text, never recall |
| `build-gates-pipeline` | Mandatory pre-deploy gates |

## Frontmatter

```json
{
  "name": "agent-reach",
  "version": "1.1.0",
  "description": "Read and search external sources through Agent Reach channels (YouTube, GitHub, Reddit, Twitter, Facebook, Instagram, LinkedIn, RSS, web)",
  "author": "Panniantong (adapted for opencode)",
  "license": "MIT",
  "tags": ["internet-access", "youtube", "reddit", "twitter", "research", "transcript", "rss", "scraping-alternative"],
  "triggers": ["agent reach", "summarize this video", "search twitter", "reddit thread", "youtube transcript", "read this page for me", "what are people saying about"]
}
```

---

*Upgraded from stub v1.0.0 → full v1.1.0 after real install (v1.5.0, doctor 5/16) + official install.md + n8nar Arabic guide*
