---
name: browser-debug-discipline
description: "Attach-only device-browser discipline: use the user's existing debug Chrome on :9222, never launch new windows, registry-primary profile only, verify login before composing, Kimi auth lives on kimi.ai. Use when the user says 'استخدم جهازي', 'ادخل على chatgpt/claude/kimi', 'use my browser', 'open the site as me', or before any playwright_browser_navigate on this device."
---

# Browser Debug Discipline (attach-only, device)

Proven 2026-10-12 (ChatGPT plan → Claude review → Kimi review, all in the
user's browser): every rule below is a real failure from that run, not advice.

## Purpose

Keep device-browser work inside the user's agreed setup: attach to the
EXISTING debug Chrome, never open new windows, never touch side profiles,
never lose composed text to a login wall.

## When to use

Before ANY `playwright_browser_navigate` on this device, and whenever the
task needs 'my account', 'logged-in state', or any of chatgpt/claude/kimi.

## Steps (in order, no skipping)

1. **Preflight the bridge, do not build one.** Check `ss -tln | grep 9222`.
   - Listening → attach and go (the MCP server aims at 127.0.0.1:9222).
   - NOT listening → STOP and ask the user to start their debug Chrome.
     NEVER launch `google-chrome --remote-debugging-port` yourself: on
     2026-10-12 self-launching opened windows on the user's screen and
     violated the standing no-new-windows rule (memory, 2026-10-11).
2. **Registry-primary profile only.** Account tasks use
   `/home/ezzeldin/.config/google-chrome-debug` (registry `primary`).
   Side profiles (e.g. `memory/.sessions/chatgpt_profile`) are NOT login
   sources — 2026-10-12 opened logged-out ChatGPT there and the user
   corrected it ("wrong tab").
3. **Verify login BEFORE composing.** Snapshot first: no `Log in` buttons =
   logged in. Long prompts typed pre-login are lost on reload (Kimi,
   2026-10-12: ~5k chars retyped). No session → HITL: user logs in on the
   visible window, agent resumes. Never type credentials.
4. **Kimi auth lives on kimi.ai.** `kimi.com` is anonymous (composer accepts
   text but has no send path). After any Kimi login, work on
   `https://www.kimi.ai/` and re-verify step 3 there.
5. **Cloudflare/2FA/CAPTCHA → human.** Wait once for auto-clear (Kimi 403
   cleared in ~15s on 2026-10-12); if it persists, hand the visible window
   to the user per `hitl-captcha-auth-handler`, then resume.
6. **Cleanup by exact PID.** `pkill -f` is blocked in this sandbox; if you
   ever launched a process, record its PID and `kill <pid>`. Verify the
   port is closed afterwards. Leave zero windows behind.
7. **Tool-call hygiene.** Every `question` object carries
   header+question+options+multiple (a missing `question` field caused a
   schema retry on 2026-10-12). Snapshot refs expire across calls —
   re-snapshot before clicking/typing.

## Verification

- `ss -tln | grep 9222` state stated BEFORE first navigate (attached vs asked).
- Snapshot evidence of logged-in state quoted before any long compose.
- End of task: port/window state reported (left attached vs closed-what-I-opened).
- Real-scenario proof: 2026-10-12 dental-plan run (ChatGPT 15 steps →
  Claude 26 fixes → Kimi 14 fixes → merged plan delivered).

## Pairs with

- `claude-code-style-web-login` — the login/session mechanism this disciplines.
- `site-login-session-registry` — profile lookup (primary only).
- `hitl-captcha-auth-handler` — human handoff for walls.
- `desktop-gui-controller` — last-resort real-screen control.
- `multi-model-pipeline` — prefer its device-API path when the user allows
  it (no browser needed at all); this skill governs only browser-mandated runs.
