---
name: site-login-session-registry
description: "Logs into websites ONCE, persists the authenticated browser session as a named profile in a registry, and reuses it on later runs so the user is not asked for credentials again. Orchestrates first-login (vault creds + real human 2FA confirmation) and session renewal (cookie expiry, re-auth). Use whenever the task needs 'my account', 'logged-in state', 'reach my dashboard', 'my sessions', 'renew my login'. Trigger phrases: 'login to', 'my session', 'still logged in', 're-login', 'my profile on <site>', 'access my account'."
---

# SITE LOGIN SESSION REGISTRY

## DIRECTIVE
Stop asking for passwords every run. A logged-in browser session is an asset:
keep it, name it, reuse it. One real login per site (completed by the human
for 2FA), then every future automation borrows that session. Track all of them
in a registry so sessions survive between runs and never get lost.

## REGISTRY FILE
- Path: `memory/.sessions/registry.json` (gitignored; chmod 600).
- Shape per site:
  ```json
  {
    "site": "github.com",
    "profile": "memory/.sessions/github_profile",
    "status": "valid" | "expired",
    "last_verified": "2026-08-13T06:00:00Z",
    "expires_hint": "cookies: 30d",
    "auth_method": "real-human-2fa" | "vault-creds"
  }
  ```

## REGISTRATION PROTOCOL (first time)
1. **Ask the human to log in ONCE** in the real Chrome (profile folder
   pre-created under `memory/.sessions/<site>_profile` via a normal browser
   window) — OR drive first login with vault creds through
   `desktop-gui-controller` / `persistent-browser-automation` when the user
   explicitly authorizes auto-typing.
2. **Complete 2FA/CAPTCHA on the visible screen** (`hitl-captcha-auth-handler`), never loop
   passwords on block.
3. **Verify** the intended authenticated page actually renders (screenshot).
4. **Persist**: copy cookies/LocalStorage in that profile, write registry entry
   with status `valid` and timestamp.

## REUSE PROTOCOL (every later time)
1. Load the registry entry for the site.
2. If `valid`: launch Chrome with that user_data_dir → assert logged-in state
   via screenshot/URL → proceed.
3. If `expired` or login failed: offer to re-login through the visible browser
   (2FA by the human), then update the registry timestamp.

## RULES
- One profile per site; NEVER reuse a profile concurrently (Chrome profile
  lock) — if `chrome.exited.cleanly` or lock file appears, copy the profile to a
  temp dir for that run.
- Session data stays on-device under `memory/.sessions/` (gitignored), never
  in prompts, logs, or git.
- Expiry is a HINT: verify by loading the real page, not by guessing.
- Evidence over memory: show the screenshot/URL proving logged-in state.

## Local adaptation
This project's venv HAS playwright 1.62.0 + chromium (headless shell) installed,
plus xdotool/pyautogui for desktop control. For human-approved 2FA use the REAL
desktop Chrome (channel="chrome", DISPLAY=:0) where it is trivial for the user
to confirm. Startup command with real desktop Chrome:
`google-chrome --user-data-dir="$PWD/memory/.sessions/<site>_profile"`.
All secrets flow through `.env`/vault — never the prompt. Paired with
`desktop-gui-controller` for visible-screen interactions and with
`hitl-captcha-auth-handler` for blocking challenges.