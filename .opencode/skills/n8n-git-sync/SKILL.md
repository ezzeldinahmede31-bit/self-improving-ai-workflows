---
name: n8n-git-sync
description: "Sync every n8n workflow JSON to a local/cloud Git repository automatically after create/update success. Use ONLY when delivering, updating, or deleting n8n workflows, so every change is versioned, recoverable, and shareable."
---

# n8n Git Version Control Sync

Version-control every workflow so nothing is ever lost and any change is reversible.

## Setup (once)
1. Create a backup repo, e.g.:
   `~/n8n-backups` (git init) — OR push to GitHub:
   `git remote add origin https://github.com/<you>/n8n-backups.git`
2. Define the folder layout per workflow:
   `{repo}/workflows/<WorkflowName>/workflow.json`
   plus optional `README.md` (per n8n-autodoc-mermaid).

## Sync procedure (run AFTER create/update success)
1. Export the updated workflow JSON via n8n MCP: `n8n_get_workflow` `mode: full`
   (this captures the live state) — or use the JSON we built.
2. Write it atomically:
   - folder `workflows/<WorkflowName>/`
   - file `workflow.json`
3. Commit with a descriptive message:
   `feat(workflow): <Name> — <summary of change> (nodes=N, active=bool)`
4. Push if a remote exists (`git push origin main`). Log failures but don't block
   the user-facing deliverable on them.

## Rules
- Commit AFTER a successful E2E test (n8n-e2e-test-runner) — don't version broken canvas.
- Never commit credentials in JSON — run a scan for secret literals first
  (per n8n-credential-security-guard); if found, fix then commit.
- On DELETE of a workflow: create one final commit that moves the JSON to
  `workflows/_archive/<Name>/<date>_workflow.json` before deleting the live one.
- Keep temp/mock files (pinnedData payloads) in a separate `examples/` folder,
  never under `workflows/<Name>/` — or mark them clearly.

## Verification
- `git status` clean after commit.
- `git log --oneline -3` shows the latest workflow change.
- If remote: confirm `git push` reported success.

## Failure handling
- Network/remote fails → still commit locally, note "local-only" to the user.
- Output:
  ```
  Git sync: ✅ {sha} workflows/<Name>/workflow.json
             (local) / remote pushed / local-only (remote error: ...)
  ```