---
name: xss-csrf-testing
description: "XSS and CSRF testing distilled. Use when testing reflected stored DOM XSS, output encoding, CSP, anti-CSRF tokens, SameSite."
---

# XSS CSRF Testing

## Purpose

Prove browser-side trust boundaries: stored, reflected, and DOM XSS neutralized; state-changing requests carry unforgeable intent.

## When to use

Use when the user says 'XSS test', 'CSRF test', 'stored XSS', 'DOM XSS', 'CSP', 'SameSite', 'anti-forgery token'.

## Steps

1. Inject markup into every reflected and stored field; assert encoded output.
2. Test DOM sinks with dangerous sources (location, postMessage).
3. Verify state changes require anti-CSRF tokens validated server-side.
4. Check cookies carry SameSite plus Secure plus HttpOnly where apt.
5. Enforce CSP and verify violations report without breaking flows.

## Anti-patterns

- `innerHTML` with interpolated user data.
- GET endpoints performing state changes.
- Tokens validated in script but not on the server.
- CSP in report-only mode claimed as enforcement.

## Example

JS DOM check:

```js
renderComment('<img src=x onerror=alert(1)>');
expect(screen.getByTestId('comment').innerHTML).not.toContain('<img');
```

## Verification

Payloads neutralized, tokens server-validated, cookie flags set, CSP enforced with reporting.

## Pairs-with

web-security-browser-internals, auth-session-testing, security-testing-owasp-fuzz, frontend-perf-testing.
