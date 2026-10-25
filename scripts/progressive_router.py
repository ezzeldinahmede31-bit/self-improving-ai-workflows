#!/usr/bin/bin/env python3
"""Progressive router: fires skills by task type, not on every request.

Replaces the 15-skill-every-request baseline with a tiered system:
  SIMPLE   -> direct path, reasoning only (STATE -1)
  MEDIUM   -> reasoning + one domain skill lookup + verify
  COMPLEX  -> reasoning + plan + domain skills + gates + verify
  HIGH_RISK-> reasoning + plan + gates + HITL approval + verify

Fails open: if skill discovery or MCP is down, degrade gracefully and never
block the task. Never fabricates success.
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / ".opencode/skills"
LIBRARY = ROOT / "memory" / "skills-library.md"
CLASSIFICATION = ROOT / "memory" / "skills-classification.json"

# Task-type keywords -> required skill families
ROUTING = {
    "simple": {
        "keywords": ["hi", "hello", "ok", "thanks", "what time", "ls ", "pwd",
                     "echo ", "date", "whoami", "list files", "show me"],
        "skills": [],  # reasoning gate only
        "desc": "Direct path. Reasoning gate only. No skill loading.",
    },
    "medium": {
        "keywords": ["write a", "create a", "build a", "fix", "debug",
                     "review", "implement", "edit", "refactor", "test",
                     "analyze", "summarize", "explain"],
        "skills": ["frontier-deep-reasoner"],
        "desc": "Reasoning + one domain skill lookup + verify.",
    },
    "complex": {
        "keywords": ["system", "architecture", "pipeline", "workflow",
                     "deploy", "migrate", "scale", "design a", "build an",
                     "agent", "automation", "orchestrat", "integration"],
        "skills": ["frontier-deep-reasoner", "writing-plans", "executing-plans",
                   "verification-before-completion"],
        "desc": "Reasoning + plan + domain skills + gates + verify.",
    },
    "high_risk": {
        # Only TRULY destructive / credential / production-mutating actions.
        # Deliberately narrow: "workflow" alone is NOT high risk — building
        # one is complex, destroying one is high risk.
        "keywords": ["delete", "rm -rf", "rm -f", "drop table", "destroy",
                     "wipe", "purge", "production deploy", "push to main",
                     "force push", "credential", "secret", "api key",
                     "token", "payment", "purchase", "buy ", "payout",
                     "grant access", "firewall", "disable security"],
        "skills": ["frontier-deep-reasoner", "writing-plans",
                   "human-approval-gates", "verification-before-completion"],
        "desc": "Reasoning + plan + gates + HITL approval + verify.",
    },
}

# Domain keyword -> skill name (from the 240 actionable skills)
DOMAIN_MAP = {
    "video": ["video-edit", "video-processing-editing", "video-downloader",
              "video-ad-system", "podcast-edit"],
    "browser": ["playwright-modern-automation", "browser-automation-scale-v2",
                "stealth-browser-evasion", "claude-device-use",
                "claude-code-style-web-login"],
    "n8n": ["n8n-workflow", "n8n-agents-official", "n8n-error-handling-official",
            "n8n-delivery-verification-gate", "n8n-mcp-workflow-builder"],
    "security": ["security-engineering-threat-modeling", "security-testing-owasp-fuzz",
                 "security-review", "secrets-scan-testing"],
    "code": ["code-review", "code-linter-python-js", "tdd",
             "clean-code", "systematic-debugging"],
    "data": ["data-analysis", "database-internals-engines", "sql-code-review"],
    "web": ["web-search", "web-design-reviewer", "frontend-design"],
    "device": ["desktop-gui-controller", "device_permissions", "device_state"],
    "memory": ["remembering-conversations", "memory-context-compaction-vector-large",
               "context-compression"],
    "skills": ["find-skills", "skill-creator", "writing-skills"],
}


def load_classification():
    """Load skill classification; fall back to empty if missing."""
    if CLASSIFICATION.exists():
        return json.loads(CLASSIFICATION.read_text())
    return []


def classify_request(text):
    """Return (tier, domain_skills) for a request text."""
    t = text.lower()
    tier = "simple"
    for tier_name in ("high_risk", "complex", "medium"):
        if any(kw in t for kw in ROUTING[tier_name]["keywords"]):
            tier = tier_name
            break
    # domain detection
    domain_skills = []
    for domain, skills in DOMAIN_MAP.items():
        if domain in t:
            domain_skills.extend(skills)
    # library lookup: only load actionable skills that match
    return tier, domain_skills


def route(text):
    """Return the skill plan for a request. Never fabricates."""
    tier, domain_skills = classify_request(text)
    plan = ROUTING[tier]["skills"] + domain_skills
    return {
        "tier": tier,
        "desc": ROUTING[tier]["desc"],
        "skills_to_load": plan,
        "skill_count": len(plan),
        "baseline_skills_avoided": 15 - len(plan),
    }


def main():
    if len(sys.argv) < 2:
        print(json.dumps(route("help"), indent=2))
        return 0
    text = " ".join(sys.argv[1:])
    print(json.dumps(route(text), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())