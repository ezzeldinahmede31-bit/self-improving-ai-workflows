---
name: canva
description: "Bind the agent to Canva via a local MCP server. Use when the user wants to create, list, get, or export Canva designs. Requires CANVA_API_KEY for live API calls."
metadata:
  version: 1.0.0
---

# Canva

Binding to Canva (web design platform) via a local MCP server at `scripts/canva-mcp-server.js`, registered in `opencode.jsonc`.

## Prerequisites

Canva is a web application. Live API calls require a **CANVA_API_KEY** set in your environment:

```bash
export CANVA_API_KEY=your_canva_api_key_here
```

Without the key, the MCP server starts but all Canva API tools return a "key not configured" message instead of making unauthenticated requests.

## Available MCP Tools

| Tool | Purpose |
|------|---------|
| `canva_info` | Check connection status and whether CANVA_API_KEY is configured |
| `canva_designs_list` | List your Canva designs (paginated) |
| `canva_design_get` | Get details of a specific design by ID |
| `canva_design_export` | Export a design to png/jpg/pdf/mp4/gif |
| `canva_exec` | Run an arbitrary Canva API request (GET/POST/PUT/DELETE) |

## Example Usage

```bash
# Check if Canva is bound and key is configured
# MCP tool: canva_info

# List designs
# MCP tool: canva_designs_list { page: 1, per_page: 10 }

# Get a design
# MCP tool: canva_design_get { designId: "DESIGN_ID" }

# Export a design as PNG
# MCP tool: canva_design_export { designId: "DESIGN_ID", format: "png" }
```

## When to Activate

- User says "canva", "Canva design", "export from Canva", "Canva API"
- User wants to create or manage Canva designs programmatically
- User wants to bind the agent to Canva using the system's MCP infrastructure

## Related Skills

- `remotion` — programmatic video (Remotion)
- `video` — general video production
- `video-editing` — FFmpeg + Remotion pipeline

## Notes

- Canva API is REST-based at `https://api.canva.com/rest/v1`
- All requests use `Authorization: Bearer <CANVA_API_KEY>`
- Export endpoints may return async job IDs that need polling
- If you don't have a Canva API key, you can get one from the Canva Developer Portal
