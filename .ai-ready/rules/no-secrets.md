# Never commit secrets

`.env`, `*.db*`, `*.db-shm`, `*.db-wal`, `.operator/`,
`**/rotation_override.secret`, `memory/.sessions/`, `memory/.skillopt-sleep/`,
`venv/`, `__pycache__/` are gitignored. Never write API keys, tokens, or
passwords into node parameters, scripts, docs, or commits.
