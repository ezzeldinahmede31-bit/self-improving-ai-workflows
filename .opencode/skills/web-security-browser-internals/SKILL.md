---
name: web-security-browser-internals
description: "Applies Michal Zalewski's The Tangled Web to secure modern web applications: how browsers and HTTP actually behave (parsing, encoding, navigation, the same-origin policy), the real attack surface (XSS, CSRF, clickjacking, DNS rebinding, response splitting, content sniffing, URL parsing edge cases), and layered defense that survives browsers' quirks. Use when the user says 'secure this web app', 'XSS', 'CSRF', 'same-origin policy', 'clickjacking', 'content sniffing', 'URL parsing attack', 'encode output', 'CSP', 'web security', 'browser security model', 'is this endpoint safe', or when reviewing web code or an n8n webhook surface for hidden attacks. Pairs with: security-and-hardening, security-review, build-gates-pipeline, frontier-red-team-auditor."
---

# Web Security — The Tangled Web

Zalewski's thesis: the web's security rests on conventions (encoding, parsing,
navigation) that browsers implement inconsistently, and attackers exploit exactly
that gap. Defend by knowing the primitives and layering independent defenses — never
assume one filter saves you.

## When to use

- Securing or reviewing any web application, endpoint, or webhook.
- Any UI that renders user input, any URL that reflects parameters, any cookie or
  CORS decision.
- Threat-modeling a browser-adjacent surface before deploy.

## The browser primitive model (know these exactly)

- **Same-origin policy**: a document may only read another origin's data; but it can
  *send* requests anywhere (CSRF lives in this asymmetry). State the origin triple —
  scheme, host, port — precisely.
- **Parsing is not what you expect**: browsers are permissive. Encodings (UTF-7,
  overlong UTF-8), nested tags, and broken HTML reparse into attacker-meaningful
  structure. Never filter "bad characters"; encode output for the context
  (HTML-attribute, JS-string, CSS, URL) instead.
- **Navigation and loading**: many tags (img, link, iframe, fetch) initiate requests
  without JS; a reflected payload that becomes a tag attribute fires on page load.
- **DNS rebinding**: the browser resolves the same hostname differently for the
  victim and for the server, bypassing hostname-based checks — validate by IP on the
  server side where it matters.

## The attack checklist
- **XSS**: reflect or store untrusted data unencoded → script runs. Encode per
  context; use a CSP that blocks inline script; sanitize only as a last layer.
- **CSRF**: state-changing request issued without the user's consent because cookies
  travel automatically. Defend with SameSite cookies + a server-validated token +
  origin/referer check on state-changing endpoints (see the n8n webhook auth rules
  in `build-gates-pipeline`).
- **Clickjacking**: transparent frames overlay a target action. Defend with frame
  ancestors / X-Frame-Options.
- **Content sniffing**: browsers guess a type when the declared one is missing.
  Always send correct Content-Type (and X-Content-Type-Options: nosniff).
- **Open redirects / URL parsing edge cases**: canonicalize and validate
  redirect/URL inputs against an allowlist, never a substring check.

## Layered defense (never one layer)
1. Correct context-aware output encoding everywhere.
2. CSP + SameSite cookies + secure/HttpOnly flags.
3. Server-side input validation (type, length, allowlist) — as a boundary, not a
   substitute for encoding.
4. Runtime checks (framework auto-escaping, ORM parameters) with the raw path
   audited separately.

## Verification
- Red-team the surface: inject a payload through every untrusted input and confirm
  it renders inert (see `frontier-red-team-auditor`).
- Confirm every state-changing endpoint enforces auth + token + SameSite (see the
  precision gate D rules in `build-gates-pipeline`).
- Check the response headers on every route (CSP, nosniff, frame-ancestors, HSTS).

## Pairs with
- `security-and-hardening` — the hardening checklist for user input and sessions.
- `security-review` — systematic vulnerability review of code.
- `build-gates-pipeline` — the SECURITY gate on every workflow/agent artifact.
- `frontier-red-team-auditor` — adversarial verification of the defenses.