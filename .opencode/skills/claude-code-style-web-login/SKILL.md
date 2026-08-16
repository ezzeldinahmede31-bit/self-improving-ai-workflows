---
name: claude-code-style-web-login
description: "Brows the web and logs into websites with the USER'S OWN accounts on THEIR device, replicating exactly how Claude Code does it — a visible local browser (Playwright MCP) with a PERSISTENT profile so one real login (user types credentials/2FA on screen) carries cookies across sessions, plus optional escalation to the user's real Chrome (CDP) and a registry of reused sessions. Use whenever the task needs 'my account', 'logged in state', 'login to <site>', 'reach my dashboard', 'check my orders/messages/dashboard', or any site that blocks anonymous scraping. Trigger phrases: 'سجل دخول بحسابي', 'login as me', 'enter my account', 'use my account', 'my emails', 'my profile on <site>', 'logged-in session'. Pairs with playwright MCP (mcp 'playwright': browser_navigate / browser_snapshot / browser_click / browser_type / browser_press_key / browser_wait / browser_screenshot / browser_close) + site-login-session-registry + hitl-captcha-auth-handler + desktop-gui-controller."
---

# Claude-Code-Style Web Login (deviceside)

Goal: give the agent the same web-and-login capability Claude Code has —
a local, visible browser that can work *as the user*, with logins that
survive sessions, on **this machine only** (credentials never leave the box).

## How Claude Code does it (replicated 1:1)

1. **Playwright MCP server runs locally** (`npx @playwright/mcp@latest`),
   browser in **headed mode** (visible window on the user's device).
2. **Persistent profile by default**: cookies/login state are stored in a
   profile dir, so the login survives across sessions (we pin
   `--user-data-dir <project>/memory/.sessions/playwright_persistent`).
3. **Login flow = human-assisted**: agent navigates to the login page in the
   visible browser; the USER types credentials and completes 2FA on screen
   (or authorizes the agent to fill them from the vault); agent then
   continues the task. No password is ever logged or stored in memory.
4. **Session reuse**: until cookies expire, later runs just navigate and the
   site already knows the user.
5. **Escalation when Playwright is blocked** (WAF/anti-bot/2FA walls):
   drive the USER'S REAL Chrome over CDP (`--remote-debugging-port` +
   `--user-data-dir` profile, connect via `--cdp-endpoint`), or the Agent360
   Browser MCP extension (`browser-mcp` config, `browser_ask_user` for
   2FA approval). Fallback order: playwright MCP → real Chrome/CDP →
   browser-mcp extension (+ stealth-browser-evasion flags when Cloudflare).

## Required setup (one time)

- `playwright` MCP server registered in `opencode.jsonc` (done in this
  workspace): local command
  `npx -y @playwright/mcp@latest --user-data-dir <project>/memory/.sessions/playwright_persistent --browser=chromium`.
  Profile dir is gitignored (memory/.sessions) and chmod 700.
- `browser-mcp` (Agent360) config exists but is **disabled** until the user
  loads its Chrome extension once (unpacked folder or Chrome Web Store).
- Optional vault: `memory/.sessions/` secrets via env vault, NEVER in prompts.

## Workflow (every logged-in task)

1. **Route/restore**: if a registry entry exists for the site
   (`memory/.sessions/registry.json`, profile under
   `memory/.sessions/<site>_profile`), reuse it; else use the playwright MCP
   persistent profile.
2. **Navigate + detect state**: `browser_navigate` to the site, take a
   `browser_snapshot`. If already authenticated (dashboard/homepage shown) →
   go straight to the task, note "session reused".
3. **Login (first time only)**: navigate to login page; if CAPTCHA/2FA →
   `hitl-captcha-auth-handler` pause: tell the USER to clear it on the
   visible screen, wait for confirmation, then resume (session persists).
   - If the user authorizes vault credentials: `browser_type` the fields and
     `browser_click` submit, then *pause for 2FA on screen*.
   - NEVER type credentials without explicit user approval; NEVER store them.
4. **Verify**: after login, confirm the authenticated page (URL no longer
   `/login`, snapshot shows account elements). Save evidence screenshot.
5. **Persist**: write/update the registry entry (site, profile path, date,
   method) so future runs skip login.
6. **Do the task** with playwright MCP tools; take screenshots as evidence
   at key steps (visual-context-verifier discipline: report what the
   screenshot shows, never assume).

## Safety gates

- Visible browser only (headed). Never run stealth/hidden for account work
  unless the site's own automation policy allows it and the user agrees.
- Credentials live in the vault or the user's own Chrome profile — never in
  memory files, prompts, or git.
- `memory/.sessions/` is 0700 + gitignored; registry contains NO secrets.
- When the user cannot be reached (no screen attention), prefer read-only
  tasks and ask before posting/clicking destructive actions.
- Sites with cluster/device checks (Google, banking): prefer the real-Chrome
  CDP path so the fingerprint matches the user's normal browsing.

## Known limits (honest)

- Persistent profile still expires cookies (usually weeks); re-login is a
  30-second user action, reused afterwards.
- Some sites require the REAL Chrome (device fingerprint); the CDP path
  covers those. Browser-mcp extension covers 2FA/CAPTCHA-hard sites.
- Never work around 2FA to bypass security — the user, not the agent, always
  performs it.