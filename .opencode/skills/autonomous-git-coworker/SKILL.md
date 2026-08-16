---
name: autonomous-git-coworker
description: "Manages Git workflows natively: checks status, creates feature branches, crafts atomic commits with descriptive logs, and prepares PRs. Use on version-controlled work, changes staged for commit, or PR preparation. Trigger phrases: 'commit', 'share your changes', 'make a branch', 'pull request', 'stage these', 'git history'."
---

# AUTONOMOUS GIT COWORKER SKILL

## DIRECTIVE
Act as a proactive software engineer who maintains clean git history. Never
leave uncommitted messy work or push directly to production branches.

## WORKFLOW PROTOCOL
1. **Pre-Work Branching:** Before starting a feature or refactor, check
   `git status` and create a dedicated branch (`feat/` or `fix/`).
2. **Atomic Commits:** Group related file changes into separate, logical
   commits instead of one massive commit.
3. **Conventional Commit Format:** Write commit messages strictly structured as:
   - `feat(scope): short description`
   - `fix(scope): concise fix summary`
4. **PR Readiness:** Before declaring a job complete, run `git diff` to ensure
   no temp files or unintended debugging print statements remain.

## Local adaptation
This workspace is **not currently a git repo** — before any commit work, run
`git init`, add a proper `.gitignore` (this project already has one protecting
`.env`, `*.db*`, `.operator/`, `venv/`), and confirm `git status` is clean of
secrets before the first commit. Only commit when the user explicitly asks;
never commit credential files. If no PR host is configured
(no `gh`, no remote), stop at committing locally and offer to push at the
user's request instead of fabricating a PR.