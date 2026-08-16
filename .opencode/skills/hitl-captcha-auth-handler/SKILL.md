---
name: hitl-captcha-auth-handler
description: "Detects CAPTCHAs, Cloudflare Turnstile, and 2FA SMS/Email verification prompts during browser automation, triggers a Human-in-the-Loop (HITL) pause, then resumes and persists the new session once the human clears them. Use with any persistent-browser-automation run that may hit interactive verification. Trigger phrases: 'captcha', '2FA', 'OTP', 'turnstile', 'recaptcha', 'verification code', 'solve the captcha', 'login blocked'."
---

# HITL CAPTCHA & 2FA AUTH HANDLER SKILL

## DIRECTIVE
Automate everything EXCEPT interactive human verifications. When a CAPTCHA or
2FA field is detected, PAUSE script execution, alert the human operator, wait
for manual clearance, and persist the new session state.

## DETECTION PROTOCOL
Constantly scan the page DOM for known challenge indicators:
- **CAPTCHA Selectors:** `iframe[src*="recaptcha"]`, `iframe[src*="hcaptcha"]`,
  `#turnstile-wrapper`, `.cf-turnstile`
- **2FA Selectors:** `input[autocomplete="one-time-code"]`,
  `input[name*="otp"]`, `input[name*="2fa"]`
- **Cloudflare Gate:** Page title contains "Just a moment..." or status code
  `403/503` with a Cloudflare challenge body.

## HITL EXECUTION FLOW

1. **Trigger Alert & Pause:**
   - Print terminal alert:
     `[HITL REQUIRED] CAPTCHA / 2FA detected on page. Manual intervention needed.`
   - Ring the terminal bell (`\a`) or show a prompt and wait for `[ENTER]`.
   - If the browser runs headless, either force a display switch or tell the
     operator to attach via the remote debugging port
     (`--remote-debugging-port=9222`).

2. **Verification Polling Gate:**
   - Do NOT proceed on arbitrary timers. Wait for an actual success condition:
     - Disappearance of the CAPTCHA iframe.
     - URL redirect to the dashboard/authenticated page.
     - Creation of an auth cookie (e.g., `session_id`, `cf_clearance`).

3. **Session Persistence:**
   - Immediately dump updated cookies, LocalStorage, and SessionStorage to
     `user_data_dir`.
   - Log: `[HITL SUCCESS] Verification completed. Session persisted. Resuming automation.`

## FAIL-CLOSED RULES
- If the success condition never appears, do NOT retry passwords in a loop.
  Report the stuck state and exit.
- Never paste a solved token or OTP back into the shareable memory files.
- Time out after a bounded wait (default 120s live; configurable) and surface
  the pause to the operator.

## Local adaptation
Integrates with `persistent-browser-automation`. HITL fits this project's
existing pattern (`hitl_gate.py`): same philosophy — automation pauses, human
approves, flow resumes. Session dumps land under `memory/.sessions/`
(gitignored), the same profile the browser skill reuses. Playwright must be
installed first (`pip install playwright` + `playwright install chromium`).