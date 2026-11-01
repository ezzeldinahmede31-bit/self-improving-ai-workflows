---
name: remotion
description: "Programmatic video with Remotion — render compositions, start studio, scaffold scenes/components, run arbitrary remotion CLI commands. Use when the user wants to build or edit a Remotion motion-graphics video (e.g. the AI automation project at video-production/ai-automation-motion)."
metadata:
  version: 1.0.0
---

# Remotion

Programmatic motion graphics using Remotion (React-based video library). This skill binds the agent to the Remotion project at `video-production/ai-automation-motion/` via a local MCP server (`scripts/remotion-mcp-server.js`) registered in `opencode.jsonc`.

## Project at a Glance

| Property | Value |
|----------|-------|
| Directory | `video-production/ai-automation-motion/` |
| Composition ID | `AIAutomationMotion` |
| Resolution | 1080 × 1920 (9:16 vertical) |
| FPS | 30 |
| Duration | 36 seconds |
| Scenes | Scene1..Scene6 (hook, problem, turning, process, comparison, closing) |
| Output | `out/video.mp4` |

## Available MCP Tools

| Tool | Purpose |
|------|---------|
| `remotion_info` | Project info: scenes, scripts, package, tsconfig |
| `remotion_render` | Render a composition to MP4 |
| `remotion_studio` | Start Remotion Studio (background) |
| `remotion_scaffold` | Scaffold a new scene or component |
| `remotion_exec` | Run arbitrary `npx remotion <command>` |

## Render Command (npm)

```bash
cd video-production/ai-automation-motion
npx remotion render AIAutomationMotion out/video.mp4 --codec h264
```

## Studio Command

```bash
cd video-production/ai-automation-motion
npx remotion studio
```

## Scene Structure

Each scene is a React component in `src/scenes/SceneN.tsx` that uses:
- `useCurrentFrame`, `useVideoConfig`, `interpolate` from Remotion
- `COLORS` from `src/constants.ts`
- Shared components: `Typography`, `Particles`, `DataLines`
- Timing is driven by `localFrame = frame - (startSecond * fps)`

## Conventions

- Arabic text uses `direction: rtl`, `textAlign: right`, font stack `"Cairo", "Tajawal", "Noto Sans Arabic", Tahoma, Arial, sans-serif`
- Colors: `navy #0A1128`, `black #050505`, `gold #D4AF37`, `cyan #00CFE8`, `white #FFFFFF`, `muted #9BA8C3`, `darkSurface #111D38`
- No fake numbers in metrics bars — use interpolated visual bars only
- Hedged claims only in closing (no absolute financial/medical promises)

## When to Activate

- User says "remotion", "render the video", "remotion studio", "add a scene", "motion graphics"
- User wants to modify the `video-production/ai-automation-motion` project
- User wants a programmatic video built with React/Remotion

## Related Skills

- `video` — general video production approach
- `video-editing` — FFmpeg + Remotion pipeline layer
- `n8n-mcp-workflow-builder` — if wiring Remotion renders into n8n automation
