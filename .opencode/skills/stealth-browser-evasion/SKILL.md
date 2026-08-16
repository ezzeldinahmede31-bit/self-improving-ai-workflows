---
name: stealth-browser-evasion
description: "Runs browser automation in stealth mode so WAF anti-bot systems (Cloudflare, Akamai, DataDome) do not flag the session: hardened Chromium launch flags, fingerprint masking, and human behavioral simulation. Use together with persistent-browser-automation whenever the target site shows bot-protection or rate-limit walls. Trigger phrases: 'blocked by cloudflare', 'bot protection', 'stealth', 'anti-bot', 'avoid detection', 'waf bypass', 'datadome', 'akamai'."
---

# STEALTH BROWSER EVASION SKILL

## DIRECTIVE
Never launch standard, unpatched Playwright or Puppeteer instances. Always
apply anti-detection flags, override automation signatures, and emulate human
interactions.

> Responsible-use note: apply this only to sites/accounts you own or have
> permission to automate. Evading authentication or access controls on sites
> you do not control violates their ToS and may be illegal.

## ANTI-DETECTION ARCHITECTURE

### 1. Browser Launch Arguments (Chromium Hardening)
When initializing Playwright/Patchright, supply these stealth arguments:
- `--disable-blink-features=AutomationControlled`
- `--disable-dev-shm-usage`
- `--no-sandbox`
- `--disable-infobars`

### 2. Fingerprint Masking
Force-override DOM properties that reveal automated drivers:
- **`navigator.webdriver`:** set strictly to `undefined` or `false`.
- **`navigator.plugins`:** mock a standard Chrome plugins array (length > 0).
- **`chrome.runtime`:** mock a realistic `window.chrome` object.
- **User-Agent & Viewport:** match the User-Agent precisely to the Client
  Hints and screen resolution (e.g., `1920x1080` on Linux/Windows).

### 3. Human Behavioral Emulation (Anti-Heuristic)
- **Typing Jitter:** never use instant `.fill()`. Type character-by-character
  with randomized delays (40ms–120ms per keypress).
- **Mouse Dynamics:** move the mouse along Bézier curves, not linear
  teleportation, before clicking elements.
- **Micro-Delays:** add randomized natural pauses (500ms–1800ms) before
  clicking or submitting forms.
- **Session Warmup:** with a fresh profile, visit a benign site (e.g., Google
  or Wikipedia) before navigating to the target domain to build initial cookie
  trust.

## VERIFICATION CONTRACT
- After each run, confirm the session was NOT flagged: expected status codes,
  no challenge page, no rate-limit wall. Paste the real observed evidence
  (status/URL/screenshot) — this project's rule is evidence over memory.
- If a challenge still appears, hand off to `hitl-captcha-auth-handler`
  instead of escalating stealth measures: the HITL pause is the fallback path.

## Local adaptation
Composes with `persistent-browser-automation` (shared profile under
`memory/.sessions/`) and `hitl-captcha-auth-handler` (the failover when a
challenge is detected anyway). Chromium hardening works with the system
Google Chrome at `/usr/bin/google-chrome` via `channel="chrome"` or with
playwright's bundled chromium after `pip install playwright` +
`playwright install chromium --with-deps`.