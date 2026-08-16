# Project Memory (MonkeyCode mirror)

> Distilled automatically by `scripts/monkeycode_sync.py`. The SOURCE OF TRUTH is the full file at `memory/conversation-memory.md` (and its compact `.bin`). Read the full file for complete history.

## Project

- Root: `/home/ezzeldin/Documents/Default Project`
- Purpose: Python agent system that guards, self-improves, and generates n8n
  workflow assets (verifying, security gating, HITL approval, key rotation).
- Test suite: `venv/bin/python -m pytest` → **295 passed, 1 deselected** (269 + 26 gate tests)
  (pytest.ini: `-m "not e2e" -q`).- Modules: `feedback_loop.py` (rotation gate + operator secret),
  `auto_self_evolver.py` (evolver + lockdown read path),
  `master_system_orchestrator.py` (orchestrator + Telegram + incidents),
  `security_gate.py` (SSRF/secret/ast probes), `hitl_gate.py` (HITL tokens),
  `verifier_engine.py`, `quality_gate.py`, plus support modules.

## What this workspace is

- Python agent system that guards, self-improves, and generates n8n
  workflow assets (verifying, security gating, HITL approval, key rotation).
- Test suite: `venv/bin/python -m pytest` (green, e2e deselected).
- Skill library under `.opencode/skills/` (fast index: `memory/skills-library.md`;
  full docs: `memory/skills-docs/`).

## Standing user rules (verbatim, load-bearing)

1. شغّل البوابات اللي في البرمجة قبل أي build (الأمان/الجودة/التكامل/الرياضيات/التفكير) — exit 0 = READY_FOR_DEPLOYMENT فقط.
2. قبل ما تسلمني أي workflow لازم تجربه ويشتغل فعلاً، وراجع أوامري واحد واحد إنها اتنفذت (n8n-delivery-verification-gate).
3. لما أطلب تصميم workflow أو agent دور على الإنترنت على أفضل طريقة موجودة الأول — مش نعيد اختراع العجلة (best-practice-first-designer).
4. بعد ما أقولك تبدأ: دور الأول، وبعدين ارجع اسألني التفاصيل، وبعدين نفذ بالظبط (clarify-before-execute).
5. القفل: شغّل كل المهارات مع بعض حتى لو شايفهم مالهمش علاقة — psychology مطلوبة مع أي طلب (omni-request-orchestrator).
6. find-skills تشتغل أوتوماتيك في الخلفية مع أي طلب، وأي مهارة جديدة تُسجَّل في الراوتر والمكتبة (router_register.py).
7. أي حاجة نبنيها تعدي على نفس البوابات بنفس الجودة زي نظام Python.

## Where things live

- **Full conversation memory:** `memory/conversation-memory.md (.bin for compact)`
- **Skill library index:** `memory/skills-library.md`
- **Skill full docs:** `memory/skills-docs/`
- **Build gates pipeline:** `scripts/build_gates_pipeline.py`
- **Router (meta-skill):** `.opencode/skills/compensatory-router/SKILL.md`
- **Skill registration:** `scripts/router_register.py <skill-name>`
- **Memory encode/decode:** `scripts/memory-encode.py encode | decode`
- **MonkeyCode sync:** `scripts/monkeycode_sync.py`

## Keep alive

- After significant work: append to `memory/conversation-memory.md`, then run
  `venv/bin/python scripts/memory-encode.py encode` (which re-runs this sync).
- After installing a skill: run `venv/bin/python scripts/router_register.py <name>`
  (adds router row + library entry + re-runs this sync).
