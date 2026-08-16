---
name: visual-context-verifier
description: "Closes the 'blind spot' gap for a model that cannot see its own work: before anything visual is claimed, capture real pixels/HTML/DOM as evidence (screenshots read back as images, page snapshots, element bounding boxes), compare expected vs actual, and only then report. Use whenever the task is visual or browser-based: clicking, styling, layout, screenshots, rendered output, GUI state, or 'it should look like X'. Trigger phrases: 'screenshot', 'does it look right', 'visual', 'rendered output', 'click the button', 'check the page'."
---

# VISUAL CONTEXT VERIFIER

## DIRECTIVE
A blind agent "assumes"; a verified agent "looks". Any claim about pixels,
layout, rendered state, or a clicked element is UNTENABLE without fresh visual
evidence. See it, verify it, report it — in that order.

## VERIFICATION LOOP
1. **CAPTURE:** produce ground truth pixels before acting:
   - Full screen: `gnome-screenshot -f /tmp/evidence.png` (then Read the image
     with the `Read` tool).
   - Browser page: JSON view via Playwright
     (`page.screenshot(path=...)`, or save page HTML + `page.locator(...)
     .bounding_box()`).
   - Element: crop with playwright locator screenshot or
     `xdotool`/`wmctrl` geometry + `gnome-screenshot -a`.
2. **READ & COMPARE:** actually LOOK at the captured image (use the Read tool on
   the PNG) and compare against the expected state. State the expected vs the
   seen in one line.
3. **REPORT EVIDENCE:** paste the file path + what the pixels prove. Never say
   "should have worked" — say "confirmed: <seen>".

## VERIFICATION CHECKLIST (per action)
- Click: target element visible? bounding box within viewport? previous state?
- Typed text: is the value echoed in a visible field/URL/toast?
- Styled/layout: font/color/size/spacing vs the spec — check the image, not the
  CSS alone.
- Rendered output (tables, charts, PDFs): screenshot the finished render.
- Multi-step flows: capture BEFORE and AFTER each stage; compare deltas.

## RULES
- One screenshot per significant stage; annotate which stage it proves.
- If a capture fails (black screen, wrong window), STOP and fix the capture —
  running blind invalidates the conclusion.
- Evidence is the deliverable; the narrative is a wrapper, not the proof.
- Clean up /tmp/evidence files at the end unless the user wants them kept.

## Local adaptation
This machine has a live X11 desktop (DISPLAY=:0): `gnome-screenshot`,
`wmctrl`, `xdotool` and a real Chrome on `:0`, plus playwright with chromium in
the venv. Prefer the REAL desktop Chrome + `gnome-screenshot` when a human must
approve 2FA; headless playwright when unattended. Pair with
`desktop-gui-controller` for GUI interaction and with `site-login-session-registry`
for authenticated pages — the rendered logged-in state must be visual-proofed the
same way.