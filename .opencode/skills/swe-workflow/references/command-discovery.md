# Command Discovery

Use this before choosing validation commands.

## Contract

1. Do not invent validation commands.
2. Discover commands from the current repo.
3. Prefer project-documented commands over generic commands.
4. Record discovered commands in the plan.
5. If no command exists, say so and choose the closest targeted validation.

## Where to Look

Inspect, when present:

- `AGENTS.md`
- `README.md`
- `package.json`
- `Makefile`
- `justfile`
- `Taskfile.yml`
- `pyproject.toml`
- `tox.ini`
- `setup.cfg`
- `Cargo.toml`
- `go.mod`
- `.github/workflows/*`
- `docs/*`

## Command Priority

Use this order:

1. Repo-specific instructions from `AGENTS.md`
2. README or docs
3. Package scripts / Makefile / task runner
4. CI workflow commands
5. Language default commands only as fallback

## Required Plan Entry

Record commands as:

| Purpose | Command | Source | Required? |
|---|---|---|---|
| Typecheck |  |  |  |
| Lint |  |  |  |
| Test |  |  |  |
| Build |  |  |  |

## Command Evidence

For noisy commands, keep raw output out of model context:

1. Write raw output to `/tmp` in its native format (`.log`, `.json`, `.txt`, `.diff`).
2. Print only the useful summary, failure lines, or bounded `head`/`tail` slice.
3. Record the compact evidence schema:
   - `Command`: exact command run
   - `Exit`: exit code
   - `Output`: `/tmp/...` file path, or `inline` for small output
   - `Summary`: one-line result
   - `Freshness`: current workspace/session, stale after relevant changes unless rerun

## Skipped Commands

For every skipped command, record:

- command
- reason skipped
- risk
- substitute validation, if any
