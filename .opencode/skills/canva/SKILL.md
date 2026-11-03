---
name: canva
description: "Bind the agent to Canva via the official Canva Dev MCP server (@canva/cli@latest mcp). Use when the user wants to create, list, get, or export Canva designs, or access Canva developer documentation."
metadata:
  version: 1.1.0
---

# Canva

Binding to Canva (web design platform) via the **official Canva Dev MCP server** (`npx -y @canva/cli@latest mcp`), registered in `opencode.jsonc`.

## Prerequisites

Canva is a web application. The official Canva Dev MCP server requires:

* **Node.js v24+** and npm (to run `npx -y @canva/cli@latest mcp`)
* A Canva developer account / API access for live design operations
* The MCP server fetches Canva documentation from `canva.dev` and provides development assistance for Canva apps

## Configuration (already added to opencode.jsonc)

```json
"canva": {
  "type": "local",
  "command": ["npx", "-y", "@canva/cli@latest", "mcp"],
  "enabled": true
}
```

## Available Capabilities (via official Canva Dev MCP server)

The official server provides AI-powered development assistance for Canva apps, including:

* Access to Canva documentation and App UI Kit reference
* Canva Developers SDK guidance
* Design-related tool invocations (LLM-controlled — include keywords like "App UI Kit", "Canva Developers SDK" in requests)

## When to Activate

- User says "canva", "Canva design", "Canva API", "Canva Dev MCP"
- User wants to access Canva developer documentation
- User wants to bind the agent to Canva using the system's MCP infrastructure

## Verification

After saving `opencode.jsonc`, restart the MCP client / session, then ask:

> "How many components are in the App UI Kit?"

If the connection is successful, the client should display a tool invocation prompt.

## Related Skills

- `remotion` — programmatic video (Remotion)
- `video` — general video production
- `video-editing` — FFmpeg + Remotion pipeline

## Documentation Index

Full Canva docs index: https://www.canva.dev/docs/apps/llms.txt
