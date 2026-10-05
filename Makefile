# Makefile for Skill Evolution System
# Usage: make <target>

.PHONY: help install-hook sync test validate clean

# Default target
help:
	@echo "Skill Evolution System — Make Targets"
	@echo ""
	@echo "  setup           First-time setup: consent + upstream + hook"
	@echo "  install-hook    Install git post-commit hook for auto-sync"
	@echo "  sync            Run sync_upstream.py manually"
	@echo "  report-update   Notify GitHub of local client update (Issue)"
	@echo "  check-updates   List upstream releases (no changes)"
	@echo "  apply-update    Accept/reject upstream updates (your right)"
	@echo "  sec-scan        Security scan path (P=<path> FIX=1 for autofix)"
	@echo "  test            Run skillopt-sleep validation experiments"
	@echo "  validate        Run build gates pipeline on changed workflows"
	@echo "  sleep           Run skillopt-sleep cycle (dry-run)"
	@echo "  sleep-run       Run skillopt-sleep full cycle + adopt"
	@echo "  evolve          Run autonomous-model-self-evolver"
	@echo "  discover        Internet skill discovery (fetch+adapt+stage)"
	@echo "  discover-dry    Discovery search only (no fetch)"
	@echo "  discover-adopt  Discovery with auto-adopt (trusted+clean only)"
	@echo "  clean           Clean temp files and caches"
	@echo ""

# First-time setup: install-time consent + upstream + hook
setup:
	venv/bin/python scripts/setup_consent.py

# Install git hook for auto-sync
install-hook:
	bash scripts/install_hook.sh

# Manual sync to upstream
sync:
	venv/bin/python scripts/sync_upstream.py

# Notify GitHub of local client update (Issue + details)
report-update:
	venv/bin/python scripts/report_update.py

# Check upstream releases (lists only, no changes)
check-updates:
	venv/bin/python scripts/check_updates.py --check-only

# Check + interactively accept/reject upstream updates
apply-update:
	venv/bin/python scripts/check_updates.py

# Security scan any path (shared gate)
sec-scan:
	venv/bin/python scripts/security_scan.py $(or $(P),.opencode/skills) $(if $(FIX),--autofix)

# Run validation experiments
test:
	venv/bin/python -m skillopt_sleep.experiments.run_experiment --persona researcher --assert-improves
	venv/bin/python -m skillopt_sleep.experiments.run_experiment --persona programmer --assert-improves

# Validate workflows through build gates
validate:
	venv/bin/python scripts/build_gates_pipeline.py

# Skillopt-sleep dry-run (preview)
sleep:
	venv/bin/python -m skillopt_sleep dry-run --project "$(PWD)"

# Skillopt-sleep full cycle + auto-adopt
sleep-run:
	venv/bin/python -m skillopt_sleep run --project "$(PWD)" --claude-home memory/.skillopt-sleep/home --scope invoked --backend nim --auto-adopt --target-skill-path .opencode/skills/skillopt-sleep/SKILL.md

# Autonomous model self-evolver
evolve:
	venv/bin/python -m autonomous_model_self_evolver run

# Clean temp files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache 2>/dev/null || true
	rm -rf logs/*.log 2>/dev/null || true

# Internet discovery: search skills.sh from today's work, fetch, adapt, stage
discover:
	venv/bin/python scripts/discover_skills.py --lookback-hours 24 --max-queries 5 --max-installs 3

# Internet discovery, dry-run (search only, no fetch)
discover-dry:
	venv/bin/python scripts/discover_skills.py --dry-run --max-queries 5

# Internet discovery with auto-adopt (trusted owners + clean scan only)
discover-adopt:
	venv/bin/python scripts/discover_skills.py --auto-adopt --max-queries 5 --max-installs 3

# Full development cycle (what runs after "اه")
dev-cycle: sleep-run evolve discover sync
	@echo "✅ Full dev cycle complete: sleep + evolve + discover + sync"

# Schedule nightly cron (3:47 AM sleep, 4:00 AM evolve)
schedule:
	venv/bin/python -m skillopt_sleep schedule --project "$(PWD)" --hour 3 --minute 17
	@echo "Add this to crontab for evolve:"
	@echo "0 4 * * * cd $(PWD) && venv/bin/python -m autonomous_model_self_evolver run >> logs/self_evolver.log 2>&1"

# Unschedule cron
unschedule:
	venv/bin/python -m skillopt_sleep unschedule --project "$(PWD)"