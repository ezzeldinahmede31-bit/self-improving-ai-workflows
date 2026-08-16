# Project orientation

This workspace is a Python agent system that guards, self-improves, and
generates n8n workflow assets (verification, security gating, HITL approval,
key rotation). It has a large skill library and a persistent conversation
memory.

- Full memory: `memory/conversation-memory.md`
- Skill index: `memory/skills-library.md`
- Build gates: `scripts/build_gates_pipeline.py`
- Test suite: `venv/bin/python -m pytest` (green)
