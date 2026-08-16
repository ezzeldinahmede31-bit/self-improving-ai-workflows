---
name: desktop-gui-controller
description: "Controls the user's real X11 desktop session (DISPLAY=:0) like a human coworker: list/focus/resize windows with wmctrl, send keyboard and mouse events, capture screenshots as evidence, manage clipboard, and launch apps. Use whenever the task needs the actual machine, not a headless VM: 'open my browser', 'type into this window', 'look at my screen', 'click there', 'what window is open', 'use my device'. Trigger phrases: 'on my desktop', 'my real screen', 'window', 'click', 'keyboard', 'screenshot my screen', 'launch the app'."
---

# DESKTOP GUI CONTROLLER

## DIRECTIVE
This machine HAS a live desktop (X11, DISPLAY=:0). Treat it as if sitting at
the keyboard: verify what is on screen (screenshot) → focus the right window →
act with the smallest reliable command → re-verify (screenshot) → report with
real evidence. Never act blind and never claim success without a screenshot.

## AVAILABLE TOOLBOX (already installed)
- `wmctrl` — list windows (`wmctrl -l`), activate (`-a`), close (`-c`),
  resize/move (`-e <X,Y,W,H>`), maximize.
- `xdotool` — mouse/keyboard events (xdotool 3.20160805.1, installed).
- `xclip` — clipboard: `xclip -selection clipboard` read/write.
- `gnome-screenshot` — full/area screenshots (take to a file, then Read it).
- `xwd` — raw X capture (needs `convert` to make PNG; prefer gnome-screenshot).
- `xdg-open` — open files/apps by mime/desktop entry.
- `pdftotext` — OCR-free text extraction from PDFs.

## SETUP (DONE on this machine)
- `xdotool` 3.20160805.1 — installed (`/usr/bin/xdotool`).
- `playwright` 1.62.0 + `pyautogui` 0.9.54 — installed in venv.
- Chromium for playwright — installed (headless shell under
  `~/.cache/ms-playwright/`).
- `pyautogui` needs `python3-tk` only for the optional MouseInfo tool; core
  screen/mouse/click works via X11 directly. Prefer xdotool for events.

## OPERATING PROTOCOL
1. **SEE FIRST:** capture `gnome-screenshot -f /tmp/shot.png` (or area select)
   and Read it. Never invent what is on screen.
2. **FOCUS:** `wmctrl -a "<window title substring>"` to bring the right window
   forward before typing/clicking.
3. **ACT SMALL:** one operation per command; if a window has multiple identical
   buttons, use coordinates from the screenshot + `xdotool mousemove X Y click 1`
   rather than blind `sendkey` spam.
4. **EVIDENCE:** after the action, take a fresh screenshot so the before/after
   is verifiable (project rule: evidence over memory).
5. **CLEANUP:** close auxiliary windows, restore the user's screen the state it
   was found in.

## SAFETY GATES (never bypass)
- Do NOT type into a field unless the screen confirms the field is focused.
- Do NOT send keystrokes that could run destructive commands (no `rm -rf`),
  or hover over destructive UI without the targeted coordinate.
- Do NOT leave the user's screen hijacked: return focus to their original app.
- Credentials are never typed from the prompt or logs — pull from the vault
  (see `site-login-session-registry`).
- Void executions (no display): if `DISPLAY` is unset or `wmctrl -l` fails,
  STOP — this skill only drives a real desktop session.

## Local adaptation
This exact machine: DISPLAY=:0, XDG_SESSION_TYPE=x11, window list ALREADY
verified live (Chrome, Docker Desktop, terminal, OpenCode). Chrome/firefox
present under /usr/bin. The `bash` tool inherits the desktop display, so
commands that need the GUI run from `~/.bashrc`-loaded env; if DISPLAY is not
inherited, prefix `DISPLAY=:0`. Screenshots are read back with the `Read` tool
as image evidence. Always combine with `site-login-session-registry` when the
goal is logging into a website.