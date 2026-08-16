---
name: persistent-browser-automation
description: "Drives a real Chromium browser (playwright or browser-use) so the agent can click, type, scroll, upload files, and extract pages exactly like a human — while reusing a persistent authenticated session instead of re-logging-in, and pulling credentials from a secret vault instead of the prompt. Use whenever the task involves 'browse', 'login to', 'scrape', 'fill the form', 'download from', CAPTCHA/2FA flows, or any site interaction. Trigger phrases: 'open the browser', 'login to', 'scrape the site', 'automate the website', 'playwright', 'download reports', 'fill the form'."
---

# PERSISTENT BROWSER AUTOMATION

## DIRECTIVE
Treat every browser interaction as a real human session, not a stateless bot.
Three pillars must hold BEFORE executing: an execution engine, a persistent
authenticated session, and a secret vault. Skipping any pillar causes bans,
CAPTCHAs, or credentials leaking into the prompt — which is worse than not
running at all.

## 3 PILLARS

### 1. Execution engine (browser-use or Playwright)
- `browser-use` (open source) or raw `playwright` with Python.
- Opens a REAL Chromium (headed or headless).
- Reads page elements (buttons, inputs, forms) → maps to
  `click()`, `type()`, `scroll()`, `upload_file()`.

### 2. Persistent sessions (user_data_dir)
- WRONG: giving the model email+password to type every time (causes bans,
  CAPTCHA, 2FA challenges).
- CORRECT: the operator logs in ONCE by hand and confirms 2FA; the session
  (Cookies + LocalStorage) is saved in a local profile folder
  (`/user_data/chrome_profile`).
- The agent opens the browser borrowing that ready session — it enters the
  site as the operator, without re-typing passwords each run.
- NEVER reuse a profile path in concurrent agents (profile lock). If locked,
  copy the profile to a temp dir for that run.

### 3. Secret vault (Environment Vault)
- If the agent must log in for the FIRST time, credentials go in a secure
  `.env` (gitignored) or via Bitwarden CLI / 1Password CLI.
- The skill PULLS them programmatically (e.g. `sops`/`bw`/`op` get) and injects
  them into the browser — never writes them literally in the prompt or in
  code comments.

## EXECUTION FLOW
1. **Check session:** does the profile exist with valid cookies? If yes, launch
   with `user_data_dir` and skip login.
2. **Check vault:** if the profile is absent or expired, read creds from env
   vault, drive the login form, approve 2FA, then persist the profile.
3. **Act:** locate elements by stable attributes (`data-testid`, aria-labels)
   before CSS/XPath; verify each step's visible state before proceeding.
4. **Verify:** assert the outcome (URL changed, toast shown, file downloaded)
   with the same rigor as a test — never claim success without observation.
5. **Cleanup:** close the browser; do NOT delete the profile.

## SECURITY RULES
- Credentials never appear in prompts, files, or git.
- Add {profile, .env, session dirs} to `.gitignore` in this repo.
- Fail closed: if 2FA challenges appear unexpectedly, stop and report —
  do not loop through passwords.
- Remember this project's standard: evidence over memory. Paste the real
  screenshot/URL/log, not "should have worked".

## Local adaptation
This project's venv does NOT yet have playwright. Enable once, before the
first run:
```
venv/bin/pip install playwright
venv/bin/python -m playwright install chromium --with-deps
```
System Google Chrome exists at `/usr/bin/google-chrome`; playwright can launch
it via `channel="chrome"` as an alternative to its bundled chromium. Session
profiles go under `memory/.sessions/` (gitignored) — never inside `venv/`.