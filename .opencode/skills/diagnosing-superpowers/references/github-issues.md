# Known-symptom search (local workflow — opencode adaptation)

This workspace has no upstream issue tracker. Search local records instead:

1. `memory/conversation-memory.md` — past incidents and lessons.
2. `memory/gate_complaints/` — recorded skill/gate complaints by gate.
3. `memory/n8n_error_patterns.json` — known automation failure signatures.

```bash
grep -rni "<symptom terms>" memory/conversation-memory.md memory/gate_complaints/ | head -10
```

Show matches to your partner with paths. If none match, fill
`templates/issue.md`, write it to the workspace, show the exact text, and —
only after partner approval — record it via
`venv/bin/python scripts/gate_complaints.py` so find-skills can resolve it.
There is no external filing step on this harness.
