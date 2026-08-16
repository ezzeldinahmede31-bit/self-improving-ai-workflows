# Automatic skill discovery (user rule #6)

find-skills runs automatically in the background on every request: scan the
local library first (`memory/skills-library.md`), then skills.sh; install
good hits silently (>=1K installs or trusted owner); register every new skill
in the router and library:

    venv/bin/python scripts/router_register.py <name>

If no online skill fits, build it in-house through the gates
(`scripts/build_gates_pipeline.py` on the new SKILL.md until
READY_FOR_DEPLOYMENT), then register it. Never pause the task to ask about a
background install; report in one line at the end.
