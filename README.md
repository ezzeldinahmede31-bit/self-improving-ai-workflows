# Self-Improving AI Workflows

> **Build production workflows & AI agents that get better every night.**
> An open-source (MIT) platform for building workflows and AI agents — it learns from your daily work, improves itself automatically, and shares improvements across the network.

## Why this system

| Feature | The verified reality |
|---------|---------------------|
| **Huge ready-made library** | 1240+ installed skills, including 35 specialized n8n skills (agents, RAG, error handling, deployment) |
| **Mandatory build gates** | Every workflow or agent passes 7 inspection stages (security → quality → integrity → logic → HITL → audit) before delivery — nothing unproven gets shipped |
| **Verified delivery** | No workflow is delivered unless it actually ran end-to-end with evidence — a written policy, not a slogan |
| **Nightly self-improvement** | After you finish work: memory + skill updates, new rules from the day's mistakes, internet skill discovery and adaptation — 25-35 minutes with the machine on |
| **Consent-based sharing** | Voluntary contribution with install-time consent, metadata-only reports with explicit approval, security scanning + mandatory human review, and every user's right to accept/reject any update |

## Featured skills (from 1240+ in `.opencode/skills/`)

**AI Automation — the system's backbone:**
`build-gates-pipeline` · `gate-first-pass-builder` · `n8n-delivery-verification-gate` · `n8n-schema-guardrail` · `n8n-syntax-v2-enforcer` · `automation-known-issues-compass` · `n8n-agents-official` · `n8n-rag-vector-qa` · `n8n-error-boundary-architect` · `n8n-subworkflow-modularizer` · `n8n-workflow-lifecycle-official` · `n8n-e2e-test-runner` · `n8n-deployment-ops-guard` · `n8n-oom-crash-recovery` · `best-practice-first-designer` · `ai-automation-master-blueprint` · `ai-automation-security-governance` · `autonomous-ai-workers` · `enterprise-multi-agent-systems` · `zapier-system-cloner`

**Programming — the quality bar:**
`tdd` · `tdd-sandbox-proof-engine` · `test-driven-development` · `clean-code` · `clean-architecture` · `code-review` · `refactoring-improving-design` · `systematic-debugging` · `root-cause-post-mortem-analyzer` · `code-execution-guided-swemaster` · `swe-workflow` · `python-performance-optimization` · `python-testing-patterns` · `async-python-patterns` · `effective-python` · `api-design-patterns` · `verification-before-completion`

> Full index with clear display names: **[SKILLS_CATALOG.md](SKILLS_CATALOG.md)** — all 292 programming + 253 AI automation skills plus our 8 custom-built engines, each with a one-line description. Regenerate any time with `venv/bin/python scripts/build_skills_catalog.py`.

## How a weak model beats frontier here

Most agent systems **rent intelligence** per token. This one **builds it**: a compensatory scaffolding around weak/free-tier models turns their weaknesses into mandatory procedures — producing work that challenges leading models:

1. **Cognitive routing before any call** (`cognitive-task-triager`): every task is classified to the right model tier — no frontier waste on trivia, no hard reasoning sent to a weak model.
2. **Forced deep reasoning** (`frontier-deep-reasoner`): an explicit decomposition ladder before any non-trivial answer — no jumping to the first plausible guess.
3. **Verification over generation** (`elite-verifier-delegation`, `llm-council`, `adversarial-self-falsifier`): generation is cheap here, judgment belongs to the stronger model — every output is attacked before delivery.
4. **Proof by execution, not by claim** (`tdd-sandbox-proof-engine`, `code-execution-guided-swemaster`): code is never accepted on "it works" — it runs, its results are measured, and fixes are surgical with no regressions.
5. **Measured nightly evolution** (`skillopt-sleep`, `autonomous-model-self-evolver`): every failure becomes a `rules.json` rule enforced at runtime on all later runs — the system wakes up stronger than it slept.
6. **Measurement, not illusions** (`self-benchmark-runner`, `model-benchmark-harness`): performance is measured on public benchmarks (AIME/MATH-500/...) against published scores, and the gap vs the leading model is measured with live calls — no rule is promoted without proof.

> Honesty note: any comparison number cited for this repo must come from running the harness locally (`self-benchmark-runner`) on your machine — the mechanism above is real and shipped in code; numbers are measured, never claimed.

## The idea in short

A system that learns from your daily usage, improves its skills and rules automatically, **and returns improvements to a central repo** that all users benefit from — free.

```
Your daily sessions
       ↓
make dev-cycle (after you're done, 25-35 min):
  sleep-run → updates CLAUDE.md + SKILL.md from today's sessions
  evolve    → generates rules.json from today's HITL rejections
  discover  → fetches skills/systems from the internet + adapts + scans them
       ↓
report_update.py → notifies the central repo (client-update Issue + details)
       ↓
sync_upstream.py → pushes a PR to the central repo
       ↓
verify_update.yml → security scan of additions + autofix before merge
  (blocking findings stop the merge until a human fixes them)
       ↓
Maintainer publishes a Release
       ↓
check_updates.py → every user sees the changelog and may **accept or reject**
  (accept applies after a local security scan + backup — reject is recorded forever)
       ↓
Everyone benefits in the next cycle
```

---

## Quickstart

```bash
# 1. Clone
git clone https://github.com/ezzeldinahmede31-bit/self-improving-ai-workflows.git
cd self-improving-ai-workflows

# 2. Environment
python -m venv venv
source venv/bin/activate
pip install -e .[dev]

# 3. First-time setup: consent + link + hook (it asks, you choose — declining is fine)
make setup

# 4. Run a full improvement cycle (after you finish work for the day)
make dev-cycle
```

### Update setup (once — `make setup` walks you through it)

```bash
make setup   # 1) your consent (accept/decline — declining is fine)  2) link OWNER/REPO  3) install hook
export GITHUB_TOKEN=ghp_...   # for writing to GitHub — from the environment only, never stored in files

# On GitHub: create the labels once (Settings → Labels)
# client-update / security-verified / needs-fix
```

**Your rights as a user (non-negotiable):**
- `make check-updates` — see what's new with **zero changes** to your machine.
- `make apply-update` — accept (applies after a local security scan + `backup/pre-update-*` snapshot) or reject (recorded, never asked again).
- Nothing is ever applied automatically — acceptance is yours alone.

---

## Core components

| Component | Role | Timing |
|-----------|------|--------|
| **skillopt-sleep** | Extracts patterns from today's sessions, updates memory + skills | cron 03:47 or `make sleep-run` |
| **autonomous-model-self-evolver** | Measures model performance, generates safety rules from today's rejections | cron 04:00 or `make evolve` |
| **discover_skills.py** | Finds skills/systems on the internet from today's work, adapts them programmatically, security-scans them | inside `make dev-cycle` or `make discover` (~5-10 min) |
| **sync_upstream.py** | Sends changes as a PR to the central repo | automatic after each commit (hook) |
| **report_update.py** | Notifies GitHub of a client update (Issue + details, no secrets) | `make report-update` |
| **verify_update.yml** | Security scan of additions + autofix before merge | on every PR |
| **check_updates.py** | Shows new updates — **the user's accept/reject right** | `make check-updates` / `make apply-update` |
| **security_scan.py** | Shared security scan (secrets + dangerous code + autofix) | `make sec-scan P=<path> FIX=1` |
| **GitHub Actions CI** | Verifies quality on every PR — merge always requires human review, never automatic | on every PR |

---

## Useful commands

```bash
# Full improvement cycle (run it after you're done for the day)
make dev-cycle

# Each component alone
make sleep-run      # skillopt-sleep only
make evolve         # self-evolver only
make discover       # internet discovery only
make sync           # manual sync

# Test and verify
make test           # validation experiments (held-out gate)
make validate       # build gates pipeline

# Nightly scheduling
make schedule       # adds 03:47 + 04:00 cron entries
make unschedule     # removes them

# Updates (your right: accept or reject)
make check-updates  # list only, no changes
make apply-update   # interactive accept/reject

# Maintenance
make clean          # cleans caches and temp files
```

---

## How collaboration works (voluntary — on by default)

> **Contribution is voluntary** (MIT). The network grows stronger by sharing, and sharing is on by default for ease — turn it off with `[skip-sync]` or by not running the send tools. **Never any silent sending**: `report_update.py` shows what will be sent (metadata only by default) and asks your approval.

1. **Install the hook once** (optional): `make install-hook`
2. **Work normally** — improve skills, add rules, update CLAUDE.md
3. **When done → run `make dev-cycle`** (25-35 minutes, machine stays on):
   - `sleep-run` — memory + skill updates from today's sessions (~15-30 min)
   - `evolve` — new rules from today's rejections (~3-5 min)
   - `discover` — internet search for new skills/systems + programmatic adaptation + security scan (~5-10 min)
4. **(With your approval)** `report_update` notifies + `sync` opens a PR → security scan + hole closing
5. **Mandatory human review** → merge → Release (never any auto-merge)
6. **Everyone benefits** in the next cycle — and every user accepts/rejects (`make check-updates`)

---

## Project structure

```
├── .opencode/skills/          # skills (self-evolving)
├── memory/                    # compressed memory + sleep staging
├── scripts/                   # improvement engines
│   ├── sync_upstream.py      # sync to the central repo
│   ├── discover_skills.py    # discover internet skills/systems + adapt + scan
│   ├── report_update.py      # notify GitHub (metadata-only + approval)
│   ├── check_updates.py      # accept/reject upstream updates
│   ├── security_scan.py      # shared security gate
│   ├── setup_consent.py      # install-time consent gate
│   ├── install_hook.sh       # install git hook
│   ├── build_gates_pipeline.py
│   └── ...
├── .github/workflows/         # ci.yml + verify_update.yml (no auto-merge, ever)
├── CONTRIBUTING.md            # collaboration rules (voluntary)
├── LICENSE                    # MIT License
├── Makefile                   # shortcuts
└── README.md                  # this file
```

---

## Security and privacy

**Never leaves your machine** (in `.gitignore`):
- `.env`, API keys, secrets
- personal sessions (`memory/.sessions/`, `.operator/`)
- local databases (`*.db`)
- virtual environments (`venv/`)

**What gets sent** (improvements only, with your approval):
- new/updated skills (`.opencode/skills/*/SKILL.md`)
- safety rules (`rules.json`)
- project memory (`CLAUDE.md`, `memory/conversation-memory.md`)
- improved scripts (`scripts/*.py`)

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) — the standing rule for those who choose to share: **what evolves on your machine returns to the origin**.

---

## License

[MIT License](LICENSE) — free for commercial use, modification, and distribution.

---

## Thank you

By using this system, you are part of a **collective learning network**. Every session on your machine strengthens the system for everyone, and every session elsewhere strengthens yours.

> **"Real improvement doesn't happen in code... it happens in sharing."**
