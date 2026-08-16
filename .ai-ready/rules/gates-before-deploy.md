# Gates before deploy (user rule #1)

Before creating or deploying ANY n8n workflow, AI agent, or automation
artifact, run the user's own gate pipeline:

    venv/bin/python scripts/build_gates_pipeline.py <artifact>

Exit code 0 means `READY_FOR_DEPLOYMENT` only. The pipeline runs SECURITY,
QUALITY, INTEGRITY, PRECISION, MATH, REASONING, HITL, and AUDIT stages.
