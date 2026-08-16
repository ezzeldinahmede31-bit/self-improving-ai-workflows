# Memory protocol

- SOURCE OF TRUTH: `memory/conversation-memory.md`.
- Load at session start: `venv/bin/python scripts/memory-encode.py decode`.
- After significant work: APPEND (never rewrite) to
  `memory/conversation-memory.md`, then run
  `venv/bin/python scripts/memory-encode.py encode` (re-compresses to
  `memory/conversation-memory.bin` and re-runs the MonkeyCode sync).
