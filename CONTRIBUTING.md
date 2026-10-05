# Contributing to Self-Improving AI Workflows

> **Contribution is voluntary** (MIT license — no strings attached). Sharing is
> **on by default** because the network grows stronger when everyone shares, and
> you can turn it off at any time: add `[skip-sync]` to a commit message, or
> simply don't run `report_update.py`/`sync_upstream.py`. Nobody watches, nobody forces.

---

## The golden rule (for those who choose to share)

**What evolves on your machine → returns to the origin → everyone benefits.**

For contributors (after `make setup` + consent): `sync_upstream.py` runs automatically
after each commit via the hook and sends changes as a Pull Request — and
`report_update.py` **asks your explicit approval** of what will be sent
(metadata only by default) before anything leaves your machine. Changed your
mind? Re-run `make setup` and decline.

---

## How it works (automatic, no manual steps)

```
1. You finish your daily work
2. The system runs its cycle in the background (25-35 minutes):
   - skillopt-sleep: updates CLAUDE.md + SKILL.md from today's sessions
   - autonomous-model-self-evolver: generates new rules.json from HITL rejections
   - discover_skills.py: fetches internet skills + adapts + security-scans them
3. sync_upstream.py collects the new changes
4. Opens a PR on a `community-contributions/*` branch
5. GitHub Actions runs the checks (experiments + security gate)
6. A human maintainer reviews → merge → everyone benefits in the next cycle
   (never any auto-merge — automated checks cannot detect prompt injection)
```

---

## What gets sent (you approve it first)

| Change type | Example |
|-------------|---------|
| New skill (`.opencode/skills/*/SKILL.md`) | you added skill `new-skill` |
| Modified skill | you improved `n8n-rag-vector-qa` |
| New `rules.json` from self-evolver | a new safety rule from a HITL rejection |
| `CLAUDE.md` update | new preferences, recurring patterns |
| `memory/conversation-memory.md` update | distilled lessons |
| Internet-discovered skill (`discover_skills.py`) | fetched from skills.sh + programmatically adapted + clean security scan |

**Never sent**: `.env`, API keys, personal sessions, `venv/`, `.operator/`, `memory/.sessions/` — all in `.gitignore`.

---

## Recommendations (fully optional)

1. **Leave the machine on 25-35 minutes** after you're done, so you benefit first from the self-improvement.
2. **To share**: keep the hook installed (`make install-hook`) — and approve reports when shown to you.
3. **To opt out**: `[skip-sync]` in any commit, or remove the hook — no questions, no guilt.
4. **If a PR fails checks** — the system tells you; fix it once manually, the rest is automatic.

## Your privacy first (reporting guarantees)

1. **Metadata only by default**: skill names + numbers — no diffs, no content, no memory.
2. **Mandatory explicit approval**: `report_update.py` shows the full text of what will be sent and asks `[y/n]` — never any silent sending.
3. **Even with `--send-content`**: only *new* skill files are attached after a security scan + secret redaction — `memory/`, `CLAUDE.md`, and `.env` **never leave the machine**.
4. **No upstream = no sending**: without central-repo setup, reports stay in a local outbox only.

## Your rights as a user (updates coming from central)

1. **Right to know**: `make check-updates` shows every new release with its changelog — zero changes to your machine.
2. **Right to accept or reject**: `make apply-update` asks per release.
   - **Accept** = local security scan (`security_scan.py`) + backup (`backup/pre-update-*`) + apply + router registration.
   - **Reject** = the decision is recorded and that release is never offered again.
3. **No automatic applying**: applying any update to your machine without your explicit consent is strictly forbidden.
4. **Right to roll back**: every applied update has a backup branch — `git checkout backup/pre-update-<ts> -- <paths>` takes you back.

## Client update lifecycle (client → central → clients)

1. **Report**: `report_update.py` opens a `client-update` Issue (anonymous client fingerprint + files + skills — no secrets).
2. **Verify**: `verify_update.yml` scans every added/modified file:
   - exposed secrets → auto-redacted (`[REDACTED:*]`) and committed back to the PR.
   - dangerous code → **blocking**: stops the merge + `needs-fix` label + comment with reasons (needs a human).
   - clean → `security-verified` label + summary comment.
3. **Publish**: maintainer merges (human review, always) and publishes a Release with a changelog.
4. **Distribute**: every user decides (accept/reject) via `check_updates.py`.

---

## Sharing manually (optional)

```bash
# Run the sync manually if you want
venv/bin/python scripts/sync_upstream.py

# Or inspect changes before sending
git status
git diff
```

---

## Code review

- **Maintainers**: review PRs weekly.
- **No auto-merge, ever**: even green checks require a human review (prompt injection is invisible to automation).
- **Breaking changes**: need approval from at least one maintainer.

---

## Reporting issues

- **Skill bug**: open an Issue with the `skill:` prefix.
- **Suggested improvement**: open a Discussion.
- **Security**: contact `security@` directly.

---

## Thank you!

By using this system for free, you are part of a **collective learning network** — every session on your machine strengthens the system for everyone, and every session elsewhere strengthens yours.

> **"Real improvement doesn't happen in code... it happens in sharing."**
