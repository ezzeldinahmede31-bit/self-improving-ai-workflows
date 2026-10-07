---
name: claude-device-use
description: "Use this Linux device exactly like Claude Code + Cowork: native file/terminal/git tools first, then Playwright persistent-browser for logged-in sites, then real X11 screen control (screenshot, focus, click, type) as last resort. Ask-first permissions (Allow read, Ask write/exec/screen, Deny secrets). Triggers: 'use my device', 'like Claude Code', 'computer use', 'control my screen', 'run on my machine', 'open the app', 'type for me', 'استخدم جهازي', 'زي كلود', 'شغل على جهازي'."
---

# Claude Device Use (Linux, Ask-First)

Single orchestrator that makes this workspace drive the machine the way
Claude Code (terminal/coding) + Cowork (computer use) does — no new
mechanism invented, only routing + permission policy over installed skills.

## 1. How the originals do it (replicated behavior)

**Claude Code:** local agent loop with built-in tools
(Read/Write/Edit/Glob/Grep/Bash/Monitor/LSP/Agent/AskUserQuestion/
TodoWrite/Cron/PlanMode/Worktree/WebFetch/WebSearch/MCP). Every call passes
a permission gate `Deny > Ask > Allow` with patterns like `Bash(npm *)`,
`Read(./path)`, `WebFetch(domain:host)`. Bash has a read-only set that never
prompts, a sandbox (filesystem allowWrite/denyRead, OS-enforced on child
processes), 30s–10min timeouts with auto-backgrounding, and plan/worktree
isolation. Login state = local persistent browser profile; the user types
credentials + 2FA once on the visible screen.

**Cowork computer-use:** precision order per task —
(1) Connectors/API first (fastest, most reliable),
(2) built-in/own browser second,
(3) direct screen interaction last (screenshot → pixel-count the click →
virtual keyboard, slowest and most error-prone). Per-app permission prompt,
sensitive-app blocklist, screenshots see everything visible (treat as
sensitive), macOS 15+ can work in background windows without stealing the
pointer — **on Linux X11 there is no background mode: we TAKE OVER the
pointer/keyboard, so warn + restore focus after every action.**

## 2. Routing order (every device task)

1. **Native tools first** (fastest, auditable): `read`/`glob`/`grep` for
   inspection; `write`/`edit` only after a read (Read-before-Edit);
   `bash` for commands/git/tests via `terminal-bash-executor-governor`;
   git flow via `autonomous-git-coworker`; isolated work via
   `using-git-worktrees`; multi-part jobs via `subagent-task-delegator` +
   `surgical-diff-patch-editor`.
2. **Web via browser second:** anonymous fetch via `firecrawl_scrape` /
   `webfetch`; logged-in work via `claude-code-style-web-login` (Playwright
   MCP headed + `memory/.sessions/playwright_persistent`, registry in
   `site-login-session-registry`, 2FA/CAPTCHA pause in
   `hitl-captcha-auth-handler`, `stealth-browser-evasion` only when the site
   policy allows it).
3. **Real screen last:** `desktop-gui-controller` loop only —
   screenshot → `Read` the pixels → `wmctrl -a` focus → ONE small
   `xdotool` action → fresh screenshot → report what is SEEN.
   Never act blind; never claim success without after-evidence.

## 3. Permission policy (Ask-first, user-confirmed)

- **Allow (no prompt):** `Read`, `Glob`, `Grep`, `bash` read-only
  (`ls`, `git status/diff/log`, `pwd`, `wmctrl -l`, screenshots).
- **Ask (explicit user yes first):** `Write`/`Edit`, any `bash` that
  creates/modifies/deletes/runs code/installs, any screen
  click/type, any browser form submit/post, any credential use.
- **Deny (never, even if asked):** `~/.ssh/`, `~/.env*` outside project,
  `memory/.sessions/` contents, `*.db*`, `.operator/`, passwords/API keys
  in prompts/logs/git, `rm -rf /`-class destroyers, banking/health/
  government apps for screen control, workarounds for 2FA.
- Destructive commands (`rm -rf`, `git push --force`, `sudo`,
  DB drops, deploys) always pause via the governor — no silent override.

## 4. Safety gates (never bypass)

- Credentials live in vault/env, never in prompts, files, or git.
- `memory/.sessions/` stays 0700 + gitignored; registry holds NO secrets.
- Before screen actions: screenshot proves the target is focused.
- After screen actions: restore the user's original window focus.
- If `DISPLAY` is unset or `wmctrl -l` fails → STOP, report headless.
- Sensitive visible data: close/minimize before screenshots when possible;
  treat every pixel as sensitive.

## 5. Verification contract (every delivery)

Report: what tool path was used (native/browser/screen), the exact
commands with exit codes, before/after screenshot paths for screen work,
and session-reuse note for logins. A device claim without this evidence
is not done.

## 6. Built companions (scripts/, all self-tested green)

- `device_permissions.py check --tool Bash --input "<cmd>"` → pre-flight
  gate (exit 0=ALLOW, 10=ASK, 20=DENY). Policy: `scripts/device_policy.json`
  (Deny > Ask > Allow; unmatched Bash/Edit/Write = ASK = Ask-first).
  Native enforcement lives in `opencode.jsonc` → `permission` block.
- `device_sandbox.py [--no-net] [--ro] -- <cmd>` → bwrap jail (proven
  bind set + `--unshare-net` kills egress; exit = command's exit).
- `device_monitor.py start/poll/stop/list` → background watch with
  per-line JSONL feed + 5min default / 30min max deadline + one end notice.
- `device_cron.py add/list/due/ack/del` → one-shot (`--in S`) and
  recurring (`--every S`) tasks, session-scoped JSON.
- `device_symbols.py defs/info/refs` → LSP-lite over Python `ast`
  (definitions+docstrings+name references; no import resolution claimed).
