#!/usr/bin/env python3
"""
build_skills_catalog.py — generate SKILLS_CATALOG.md with clear display names.

Reads every skill's real frontmatter (name + description) from
.opencode/skills/<slug>/SKILL.md and builds a full, grouped catalog of:
  1. ALL programming skills
  2. ALL AI automation skills
  3. Our custom-built skills + engines (with clear display titles)

Display titles are humanized slugs with correct acronyms (n8n, AI, LLM, RAG...)
plus the skill's own first-sentence description — so GitHub visitors see names
that actually describe things. Nothing inside the system is renamed.

Usage:
    venv/bin/python scripts/build_skills_catalog.py [--check-router] [--register-missing]
"""

import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / ".opencode" / "skills"
ROUTER = SKILLS / "compensatory-router" / "SKILL.md"
OUT = ROOT / "SKILLS_CATALOG.md"

PROG_PAT = re.compile(
    r"test|tdd|qa-|quality|python|refactor|clean|review|debug|\bapi\b|java|"
    r"javascript|typescript|node|golang|rust|ruby|php|swift|kotlin|dotnet|sql|"
    r"database|postgres|mysql|docker|kuber|helm|terraform|ansible|swe|software|"
    r"program|engineer|architect|benchmark|profil|lint|pytest|junit|xunit|mock|"
    r"fixture|coverage|mutation|fuzz|owasp|sast|devops|sre|observab|monitor|code",
    re.IGNORECASE)
AUTO_PAT = re.compile(
    r"^n8n|zapier|rpa|automat|agent|llm|rag|vector|prompt|mcp|webhook|workflow|"
    r"bot-|orchestrat|integrat|schedul|cron",
    re.IGNORECASE)

# slugs excluded from the catalog (off-topic strays matching a keyword by accident)
EXCLUDE = {"caples-tested-advertising"}

# overlap members that belong to Programming despite matching automation pattern
PROG_OVERRIDE = {
    "code-coverage-mastery", "dast-sast-integration", "jit-pragmatic-architect",
    "pragmatic-programmer", "prompt-engineering-for-developers",
    "prompt-regression-testing", "python-mcp-server-generator",
    "scrum-qa-integration", "swe-workflow",
}

PROG_GROUPS = [
    ("Testing & Quality", r"test|tdd|qa|quality|coverage|mutation|fuzz|xunit|pytest|junit|mock|fixture|sast|owasp|pentest|injection|xss|regression|snapshot|property|contract-test|chaos|resilien|flaky|trio|quadrant|kanban|scrum-qa|bdd|cucumber|cypress|selenium|playwright|espresso|appium|jmeter|k6|postman|pact"),
    ("Python", r"python"),
    ("Clean Code & Design", r"clean|refactor|solid|pattern|coupling|cohesion|modular|architect|simplif|readab|naming|craftsman|art-of| Elements|pearls|pragmatic"),
    ("Debugging & Root Cause", r"debug|root-cause|postmortem|post-mortem|trace|diagnos|bisect|profiler"),
    ("APIs & Backend", r"\bapi\b|rest|graphql|grpc|backend|server|database|sql|postgres|endpoint|webhook-security|contract"),
    ("DevOps & Delivery", r"devops|sre|docker|kuber|helm|terraform|ansible|deploy|ci|cd-|pipeline|observab|monitor|alert|incident|on-call|capacity|performenter|performance|load|stress|soak|spike|benchmark|slo|dgbr|action"),
    ("Languages & Systems", r"java|javascript|typescript|golang|rust|ruby|php|swift|kotlin|dotnet|cpp|compiler|language|concurren|parallel|thread|kernel|linux|unix|network|tcp|http|security|crypto|kernel|embedded|firmware"),
]
AUTO_GROUPS = [
    ("n8n Platform (build, run, debug, deploy)", r"^n8n-(?!.*(agent|rag|vector|embed|ai-|security|governance|guard|proctor|flowguard))|using-n8n|^n8n-workflow|^n8n-code|^n8n-node|^n8n-expression|^n8n-loop|^n8n-sub|^n8n-git|^n8n-self|^n8n-multi|^n8n-mcp|^n8n-valid|^n8n-debug|^n8n-deploy|^n8n-oom|^n8n-pinned|^n8n-autodoc|^n8n-binary|^n8n-data|^n8n-credential|^n8n-error|^n8n-extend"),
    ("n8n AI Agents & RAG", r"agent|rag|vector|embed|qdrant|nvidia-embed|llm|prompt|langchain|intelligence|modern-approach|ml-powered|ml-systems|hands-on"),
    ("Automation Platforms (Zapier/Make/RPA/low-code)", r"zapier|make-|uipath|rpa|lowcode|low-code|airflow|temporal|blueprism|servicenow|salesforce-testing|sap-erp|mainframe|screen-scraping|terminal-automation|attended|bot-farm|task-mining|process-mining|idempotency-distributed|legacy-modern"),
    ("Multi-Agent Systems", r"multi-agent|swarm|orchestrat|delegat|handoff|squad|a2a|collaborat|hierarch|dispatch|supervis|foreman|fleet|consensus|council"),
    ("Integration & Messaging", r"webhook|integrat|mcp|event-|stream|kafka|queue|celery|saga|pub|sub|message|aftl|etl|elt|sync|connect|trigger|cron|schedul|poll|digests|notif|lead-capture|invoice|docusign|calendar|email|slack|teams|discord|telegram|whatsapp|twilio|intercom|zendesk|hubspot|salesforce|crm|jira|linear|trello|asana|clickup|monday|notion|obsidian|sheets|excel|airtable|mailchimp|shopify|youtube|spotify|podcast|stripe|quickbooks|pipedrive|woocommerce|linkedin|twitter"),
    ("LLM Production (serve, tune, evaluate, govern)", r"llmops|serving|fine-tun|eval|guardrail|gateway|token|cost|latency|deploy.*llm|scale.*model|quantiz|distill|compress|infer|vllm|tgi|tensorrt|nim|router-tier|tier-router|benchmark-harness|drift-watch|regression-gate|rails|hitl|human-oversight|oversight|redteam|red-team|jailbreak|injection-defense|alignment|safety|robustness|adversarial|risk|compliance|audit|accountab|liab|fairness|bias|privacy|consent|ip-protection|copyright|secret|vault|soc|defense|policy|zero-trust|rbac|enclave|mpc|homomorphic|drift|poisoning|concept-drift|context-window|memory-persist|memory-context|recall|forget|rag-|hybrid-search|rerank|hyde|chunk|splitter|parser|ocr|document|graphrag|knowledge-graph|multimodal|cross-lingual|semantic-cache|distribut.*search|indexing|hnsw|ivf|ann|pinecone|milvus|weaviate|similarity|relevance|ranking|elasticsearch"),
]

ACRONYMS = {"n8n": "n8n", "ai": "AI", "llm": "LLM", "api": "API", "rag": "RAG",
            "mcp": "MCP", "ci": "CI", "cd": "CD", "qa": "QA", "tdd": "TDD",
            "bdd": "BDD", "rpa": "RPA", "sql": "SQL", "ux": "UX", "ui": "UI",
            "e2e": "E2E", "k8s": "K8s", "devops": "DevOps", "ml": "ML",
            "json": "JSON", "http": "HTTP", "oauth": "OAuth", "jwt": "JWT",
            "cli": "CLI", "sdk": "SDK", "ddd": "DDD", "cqrs": "CQRS",
            "rest": "REST", "graphql": "GraphQL", "grpc": "gRPC", "kafka": "Kafka",
            "qdrant": "Qdrant", "nvidia": "NVIDIA", "github": "GitHub",
            "git": "Git", "python": "Python", "javascript": "JavaScript",
            "typescript": "TypeScript", "slo": "SLO", "sli": "SLI",
            "atdd": "ATDD", "okr": "OKR", "seo": "SEO", "crm": "CRM",
            "erp": "ERP", "hr": "HR", "sms": "SMS", "voip": "VoIP",
            "iot": "IoT", "rl": "RL", "nlp": "NLP", "asr": "ASR",
            "tts": "TTS", "ocr": "OCR", "gpu": "GPU", "tpu": "TPU",
            "sso": "SSO", "rbac": "RBAC", "mtls": "mTLS", "hmac": "HMAC",
            "owasp": "OWASP", "sast": "SAST", "dast": "DAST", "ssrf": "SSRF",
    "wcag": "WCAG", "mit": "MIT", "cs": "CS",
            "xss": "XSS", "csrf": "CSRF", "pii": "PII", "kpi": "KPI"}

CUSTOM = [
    ("skillopt-sleep", "Nightly Skill Evolver",
     "Learns from your sessions while you sleep: harvests transcripts, mines recurring tasks, replays them, and consolidates only held-out-validated improvements into memory and skills. Runs nightly via cron or on demand with make dev-cycle."),
    ("autonomous-model-self-evolver", "Measured Model Evolver",
     "Measures the current model against a live leader on deterministic probes, extracts real weaknesses from the rejection audit trail, and promotes a fix into an enforced rules.json only after the model passes the exact regression probe. No measured gap, no promotion — ever."),
    ("discover_skills.py", "Internet Skill Discoverer",
     "Derives search queries from today's work, searches skills.sh, fetches candidates, adapts their files programmatically (frontmatter, paths, adapter wrappers), security-scans them, and stages or adopts. Part of make dev-cycle."),
    ("security_scan.py", "Shared Security Gate",
     "One scanner for all external content: exposed secrets (auto-fixable) and dangerous code (blocking). Used by discovery, update-apply, and the GitHub verify_update workflow."),
    ("sync_upstream.py", "Upstream Publisher",
     "Collects local improvements and opens a community-contributions PR to the central repo. Consent-gated; silent by default without approval."),
    ("report_update.py", "Update Notifier",
     "Notifies the central repo of a client update as a metadata-only GitHub Issue — shows you the exact text and requires explicit [y/n] approval. Nothing secret ever leaves."),
    ("check_updates.py", "Update Acceptor",
     "Shows upstream releases with changelogs and lets you accept (local security scan + backup + apply) or reject (recorded forever) each one. Nothing auto-applies."),
    ("setup_consent.py", "Consent Gate",
     "Install-time consent: accept sharing (metadata-only + per-send approval) or decline into fully-local mode. Re-runnable any time via make setup."),
]


def parse_frontmatter(md_path):
    try:
        text = md_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return None, None
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return None, None
    fm = m.group(1)
    name, desc = None, None
    for line in fm.splitlines():
        if re.match(r"\s*name\s*:", line):
            name = line.split(":", 1)[1].strip().strip("\"'")
        elif re.match(r"\s*description\s*:", line):
            desc = line.split(":", 1)[1].strip().strip("\"'")
    return name, desc


def humanize(slug):
    words = re.sub(r"[-_]+", " ", slug).split()
    out = []
    for w in words:
        lw = w.lower()
        out.append(ACRONYMS.get(lw, w[:1].upper() + w[1:] if w else w))
    return " ".join(out)


def one_liner(desc):
    if not desc:
        return "See SKILL.md for details."
    desc = " ".join(desc.split())
    parts = re.split(r"\.\s+", desc, maxsplit=1)
    first = parts[0].rstrip(".")
    if len(first) > 220:
        first = first[:217] + "..."
    return first + "."


def load_collection():
    all_dirs = sorted(d.name for d in SKILLS.iterdir()
                      if d.is_dir() and (d / "SKILL.md").exists())
    prog, auto = [], []
    for slug in all_dirs:
        if slug in EXCLUDE:
            continue
        in_prog = bool(PROG_PAT.search(slug))
        in_auto = bool(AUTO_PAT.search(slug))
        if slug in PROG_OVERRIDE:
            prog.append(slug)
        elif in_auto:
            auto.append(slug)
        elif in_prog:
            prog.append(slug)
    return prog, auto


def group(slugs, groups):
    buckets = {t: [] for t, _ in groups}
    buckets["General"] = []
    placed = set()
    for title, pat in groups:
        rx = re.compile(pat, re.IGNORECASE)
        for s in slugs:
            if s not in placed and rx.search(s):
                buckets[title].append(s)
                placed.add(s)
    for s in slugs:
        if s not in placed:
            buckets["General"].append(s)
            placed.add(s)
    return {k: sorted(v) for k, v in buckets.items() if v}


def entry(slug):
    name, desc = parse_frontmatter(SKILLS / slug / "SKILL.md")
    title = humanize(slug)
    link = f".opencode/skills/{slug}/SKILL.md"
    return f"- [{title}]({link}) (`{slug}`) — {one_liner(desc)}"


def main():
    check_router = "--check-router" in sys.argv
    register = "--register-missing" in sys.argv

    prog, auto = load_collection()
    custom_slugs = {c[0] for c in CUSTOM if (SKILLS / c[0]).exists()}
    prog = [s for s in prog if s not in custom_slugs]
    auto = [s for s in auto if s not in custom_slugs]

    lines = [
        "# Skills Catalog — Programming, AI Automation & Custom-Built",
        "",
        f"> Full index of this repo's `{len(prog)} programming` + `{len(auto)} AI automation` "
        f"skills plus our custom-built engines — every entry shows a **clear display name**, "
        f"its machine `slug`, and a one-line description taken from the skill itself. "
        f"Generated {datetime.now().strftime('%Y-%m-%d')} by `scripts/build_skills_catalog.py`.",
        "",
        f"- **Programming: {len(prog)}** · **AI Automation: {len(auto)}** · "
        f"**Custom-built: {len(CUSTOM)}**",
        "",
        "---",
        "",
        "## Part 1 — Programming Skills",
        "",
    ]
    for title, slugs in group(prog, PROG_GROUPS).items():
        lines += [f"### {title} ({len(slugs)})", ""]
        lines += [entry(s) for s in slugs] + [""]

    lines += ["---", "", "## Part 2 — AI Automation Skills", ""]
    for title, slugs in group(auto, AUTO_GROUPS).items():
        lines += [f"### {title} ({len(slugs)})", ""]
        lines += [entry(s) for s in slugs] + [""]

    lines += ["---", "",
              "## Part 3 — Custom-Built (this project)",
              "",
              "Designed and built here to make weak/free-tier LLMs behave like frontier "
              "models — then shared back so the network compounds:",
              ""]
    for slug, display, blurb in CUSTOM:
        if (SKILLS / slug).exists():
            lines.append(f"- **{display}** (`{slug}`) — {blurb} "
                         f"[SKILL.md](.opencode/skills/{slug}/SKILL.md)")
        else:
            lines.append(f"- **{display}** (`scripts/{slug}`) — {blurb} "
                         f"[source](scripts/{slug})")
    lines += ["", "Also part of the engine: `build_gates_pipeline.py` (7-stage build gates), "
              "`build_skills_catalog.py` (this file's generator), `install_hook.sh`, "
              "and the GitHub workflows `ci.yml` + `verify_update.yml`.", ""]

    OUT.write_text("\n".join(lines), encoding="utf-8")
    total = len(prog) + len(auto)
    print(f"Catalog written: {OUT.relative_to(ROOT)} "
          f"({len(prog)} programming + {len(auto)} automation + {len(CUSTOM)} custom)")

    if check_router or register:
        router_text = ROUTER.read_text(encoding="utf-8", errors="ignore")
        missing = [s for s in prog + auto
                   if f"`{s}`" not in router_text and s not in custom_slugs]
        print(f"Router check: {len(missing)} cataloged skills missing from router.")
        if register and missing:
            import subprocess
            r = subprocess.run(
                [str(ROOT / "venv" / "bin" / "python"),
                 "scripts/router_register.py"] + missing,
                cwd=str(ROOT), capture_output=True, text=True, timeout=600)
            print((r.stdout or "")[-500:])
            print((r.stderr or "")[-500:])
        elif missing:
            print("Run with --register-missing to register them.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
