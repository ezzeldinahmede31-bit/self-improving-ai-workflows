#!/usr/bin/env python3
"""Generate a per-skill documentation file explaining exactly what each skill does.

Reads every SKILL.md under .opencode/skills/ (recursively, so nested packs like
weather-automation/ are covered) and produces one markdown doc per skill under
memory/skills-docs/. The docs are a "reference shelf" kept separate from the
skill tree itself (as the user requested: 'خلي الملفات ديه علي جنب').

Each doc includes: source path, name, full description, extracted structure
(sections/headers), commands/tools referenced, and frontmatter metadata.
"""

import os
import re
import sys
import json
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_ROOT = os.path.join(ROOT, ".opencode", "skills")
DOCS_DIR = os.path.join(ROOT, "memory", "skills-docs")
LIBRARY_PATH = os.path.join(ROOT, "memory", "skills-library.md")
ROUTER_PATH = os.path.join(SKILLS_ROOT, "compensatory-router", "SKILL.md")

# Families in the exact order they appear in the router registry (same pattern).
# New skills with no family land in the catch-all bucket at the end.
CATCHALL_BUCKET = "Other / custom (not yet in router registry)"

# Keyword -> family fallback for skills that are not named in the router registry
# (e.g. nested automation copies, brand-new skills). Mirrors router_register rules.
FALLBACK_BUCKET_RULES = [
    ("Automation (per-tool)", ["automation", "workflow", "webhook", "integration", "zap", "make", "crm", "sheets", "excel", "airtable", "notion", "calendar", "email", "invoice", "docusign", "quickbooks", "shopify", "woocommerce", "trello", "asana", "clickup", "jira", "linear", "monday", "zendesk", "intercom", "whatsapp", "twilio", "teams", "home assistant", "spotify", "podcast", "transcription", "obsidian", "devops", "ansible", "hr", "weather"]),
    ("n8n", ["n8n"]),
    ("Zapier", ["zapier", "zap", "durable workflow"]),
    ("Marketing/SEO/Growth", ["marketing", "seo", "keyword", "ads", "landing", "copy", "blog", "newsletter", "growth", "pricing", "launch", "referral", "affiliate", "psychology", "persuasion", "hook", "content", "brand", "geo", "cro", "conversion", "audience", "lead", "customer", "competitor", "analytics", "semrush", "ahrefs"]),
    ("Social media", ["social", "bluesky", "reddit", "thread", "tiktok", "wechat", "discord", "slack", "telegram", "feishu", "instagram", "facebook", "linkedin", "post"]),
    ("Video/Media", ["video", "media", "ffmpeg", "whisper", "transcri", "yt-dlp", "download", "reel", "montage", "inpaint", "audio"]),
    ("Research", ["research", "search", "literature", "academic", "arxiv", "scholar", "data", "github research"]),
    ("Reasoning/Math/Logic", ["math", "reason", "logic", "olympiad", "algorithm", "equation", "count", "boundary", "tot", "verif", "benchmark", "symbolic", "proof", "think"]),
    ("Thinking frames", ["thinking-", "frame", "socratic", "pre-mortem", "probabilistic", "cynefin", "triz", "first-principles"]),
    ("Context/Memory/System", ["context", "memory", "token", "compress", "evaluation", "harness", "hosted", "latent", "bdi", "state-machine", "rate", "compactor", "degradation"]),
    ("Agents/Architecture", ["agent", "architect", "orchestrator", "squad", "tool", "autonomous", "workflow", "api", "site", "git"]),
    ("Security", ["security", "auth", "firebase", "owasp", "hardening", "ssrf", "secret", "gate", "monitoring"]),
    ("Coding/SWE", ["code", "swe", "tdd", "debug", "surgical", "refactor", "single-pass", "codebase", "ast", "decomposition", "paper-to-code", "lint", "test"]),
    ("Browser/Device", ["browser", "login", "session", "desktop", "gui", "captcha", "stealth", "playwright", "visual", "x11"]),
    ("Creative/Reasoning", ["analogy", "inversion", "lateral", "provocation", "scamper", "six-hats", "worst", "concept", "brainstorm", "council", "consensus", "emergent", "creative"]),
    ("Delivery/Gates", ["gate", "delivery", "verification", "omni", "clarify", "spec", "router", "deployment", "hitl", "audit", "skill"]),
    ("Dev utilities", ["i18n", "prompt", "banner", "organize", "image", "stock", "stars", "domain", "stripe", "brand"]),
    ("Superpowers pack — obra", ["superpowers", "plan", "execut", "brainstorm", "test-driven", "debug", "code-review", "subagent", "worktree", "finishing-a-development"]),
    ("Video-pack extras", ["remembering-conversations", "impeccable", "wizard"]),
]


def fallback_bucket(desc):
    dl = (desc or "").lower()
    for bucket, kws in FALLBACK_BUCKET_RULES:
        for kw in kws:
            if kw in dl:
                return bucket
    return CATCHALL_BUCKET


def parse_frontmatter(text):
    """Return (frontmatter_dict, body) or ({}, text)."""
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not m:
        return {}, text
    raw = m.group(1)
    body = text[m.end():]
    fm = {}
    # simple YAML-ish parse: key: value / key: >- / lists / folded scalars
    parts = {}
    current_key = None
    for line in raw.splitlines():
        lm = re.match(r"^([A-Za-z0-9_\-]+):\s*(.*)$", line)
        if lm:
            current_key = lm.group(1)
            val = lm.group(2).strip().strip('"').strip("'")
            if val in ("", ">-", "|", ">", "|2", "|-"):
                fm[current_key] = ""
                parts[current_key] = []
            elif val.startswith("[") or val.startswith("{"):
                try:
                    fm[current_key] = json.loads(val)
                except Exception:
                    fm[current_key] = val
            else:
                fm[current_key] = val
        elif current_key and line.startswith("  - "):
            item = line.strip()[3:].strip().strip('"').strip("'")
            prev = fm.get(current_key)
            if isinstance(prev, list):
                fm[current_key] = prev + [item]
            elif prev is None:
                fm[current_key] = [item]
            elif isinstance(prev, str):
                fm[current_key] = [prev, item]
        elif current_key in parts and line.strip():
            parts[current_key].append(line.strip())
    for key, pieces in parts.items():
        if pieces:
            s = " ".join(pieces)
            if len(s) >= 2 and s[0] == s[-1] and s[0] in ('"', "'"):
                s = s[1:-1]
            fm[key] = s
    return fm, body


def extract_headers(body):
    """Extract markdown headers with their level."""
    return re.findall(r"^(#{1,4})\s+(.*)$", body, re.MULTILINE)


def extract_commands(body):
    """Extract shell-ish commands from inline code / fenced blocks."""
    cmds = []
    for m in re.finditer(r"`([^`\n]+)`", body):
        c = m.group(1)
        if re.match(r"^[\w./~\-]+(\s+[\w./~\-]+){0,4}$", c):
            cmds.append(c)
    for m in re.finditer(r"^\s*\$?\s*(npx\s+[\w@/\-\.]+|npm\s+\S+|pip\s+install\s+\S+|python[\w.\-]*\s+[\w/\-\.]+\.py)",
                         body, re.MULTILINE):
        cmds.append(m.group(0).strip())
    # dedupe preserve order
    seen = set()
    out = []
    for c in cmds:
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out[:40]


def skill_doc_path(skill_name, rel):
    # rel is like "weather-automation/airtable-automation" or "impeccable"
    parts = list(rel.split(os.sep))
    # strip the trailing skill dir name if it equals skill_name (avoid dup)
    parts = [p for p in parts if p and p != "."]
    safe = "_".join(parts)
    safe = re.sub(r"[^A-Za-z0-9._-]", "_", safe)
    return os.path.join(DOCS_DIR, f"{safe}.md")


def generate_doc(skill_path, skill_name, fm, body):
    headers = extract_headers(body)
    commands = extract_commands(body)
    fm_interesting = {k: v for k, v in fm.items()
                      if k in ("name", "version", "author", "license", "category",
                               "department", "tags", "trigger", "triggers", "models",
                               "mcp", "related_skills", "steps", "workflow",
                               "input", "output", "tools", "allowed-tools", "metadata")}
    lines = []
    lines.append(f"# {skill_name}")
    lines.append("")
    lines.append(f"- **Source file:** `{os.path.relpath(skill_path, ROOT)}`")
    if fm.get("version"):
        lines.append(f"- **Version:** {fm.get('version')}")
    if fm.get("author"):
        lines.append(f"- **Author/Origin:** {fm.get('author')}")
    if fm.get("license"):
        lines.append(f"- **License:** {fm.get('license')}")
    if fm.get("category"):
        lines.append(f"- **Category:** {fm.get('category')}")
    lines.append("")
    desc = fm.get("description") or "(no description)"
    lines.append("## What it does")
    lines.append("")
    lines.append(desc)
    lines.append("")
    lines.append("## Structure")
    lines.append("")
    if headers:
        lines.append("| # | Section |")
        lines.append("|---|---------|")
        for i, (level, title) in enumerate(headers[:60], 1):
            lines.append(f"| {i} | {'#' * len(level)} {title} |")
    else:
        lines.append("*(no markdown headings found — body is the full content)*")
    lines.append("")
    if commands:
        lines.append("## Commands / tools referenced")
        lines.append("")
        lines.append("```")
        for c in commands:
            lines.append(c)
        lines.append("```")
        lines.append("")
    if fm_interesting:
        lines.append("## Frontmatter metadata")
        lines.append("")
        lines.append("```json")
        lines.append(json.dumps(fm_interesting, ensure_ascii=False, indent=2, default=str))
        lines.append("```")
        lines.append("")
    lines.append("---")
    lines.append(f"*Auto-generated by `scripts/skills_docs_generator.py` on {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
    return "\n".join(lines)


def parse_registry_buckets(router_path=ROUTER_PATH):
    """Return ordered [(bucket_header, [skill names]), ...] from the router registry.

    Parses the '## Full skill registry' section: '### <Bucket> (N)' headers followed
    by a line of `` `name` (D) `` entries. Bucket name = everything before the LAST
    parenthetical so suffixed headers like '### Automation (per-tool) (38)' parse.
    Missing/unparseable router -> empty list (library then uses keyword fallback).
    """
    if not os.path.exists(router_path):
        return []
    txt = open(router_path, encoding="utf-8", errors="replace").read()
    m = re.search(r"## Full skill registry(.*)$", txt, re.S)
    if not m:
        return []
    section = m.group(1)
    buckets = []
    for hm in re.finditer(r"^### (.+?)\s*\(\d+\)\s*$", section, re.M):
        header = hm.group(1).strip()
        seg = section[hm.end():]
        nxt = re.search(r"^### ", seg, re.M)
        block = seg[: nxt.start()] if nxt else seg
        names = re.findall(r"`([^`]+)`", block)
        buckets.append((header, names))
    return buckets


def one_line(desc, limit=160):
    """Collapse a long description to a single scannable line (first sentence)."""
    d = " ".join((desc or "").split())
    d = d.replace('\\"', '"').replace("\\'", "'")
    if not d:
        return "(no description)"
    parts = re.split(r"(?<=[.!?])\s+(?=\S)", d)
    s = parts[0].strip()
    if len(s) > limit:
        s = s[:limit].rstrip() + "…"
    return s


def generate_library(entries):
    """Write memory/skills-library.md: every skill, one line, grouped by family.

    entries = list of (skill_name, dir_name, description). Buckets come from the
    router registry (same pattern); unmatched skills go to a keyword fallback
    bucket, then the catch-all. Duplicate names (e.g. the same automation skill
    stored both top-level and nested under weather-automation/) are shown once —
    the first occurrence (top-level, shortest path) wins.
    """
    buckets = parse_registry_buckets()
    name_to_bucket = {}
    for header, names in buckets:
        for n in names:
            name_to_bucket.setdefault(n, header)
    ordered_headers = [h for h, _ in buckets]

    grouped = {}
    seen = set()
    for skill_name, dir_name, desc in entries:
        if skill_name in seen:
            continue
        seen.add(skill_name)
        bucket = name_to_bucket.get(skill_name) or name_to_bucket.get(dir_name)
        if bucket is None:
            bucket = fallback_bucket(desc)
        grouped.setdefault(bucket, []).append((skill_name, one_line(desc)))

    # keep catch-all last, preserve router order otherwise
    headers = ordered_headers + [h for h in grouped if h not in ordered_headers]
    total = len(seen)
    lines = []
    lines.append("# Skill Library — fast lookup index")
    lines.append("")
    lines.append("One-line reference for every skill under `.opencode/skills/`.")
    lines.append("The tool-invocation skill scans this file to find the right skill fast:")
    lines.append("pick a family, read the one-liners, then open `memory/skills-docs/<name>.md`")
    lines.append("for the full doc of the chosen skill. Grouping matches the router")
    lines.append("registry buckets (`compensatory-router/SKILL.md`), so new skills that were")
    lines.append("registered in the router appear under the same family here automatically.")
    lines.append("")
    for header in headers:
        items = grouped.get(header) or []
        if not items:
            continue
        lines.append(f"## {header} ({len(items)})")
        lines.append("")
        for skill_name, one in sorted(items):
            lines.append(f"- **{skill_name}** — {one}")
        lines.append("")
    lines.append("---")
    lines.append(
        f"*Auto-generated by `scripts/skills_docs_generator.py` on "
        f"{datetime.now().strftime('%Y-%m-%d %H:%M')} — {total} skills, "
        f"{len([h for h in headers if grouped.get(h)])} families*"
    )
    with open(LIBRARY_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main():
    library_only = "--library-only" in sys.argv
    os.makedirs(DOCS_DIR, exist_ok=True)
    skills = []
    for root, dirs, files in os.walk(SKILLS_ROOT):
        if "SKILL.md" in files:
            spath = os.path.join(root, "SKILL.md")
            rel = os.path.relpath(spath, SKILLS_ROOT)
            # skill name = directory name (top-level dir) or nested dir name
            name_dir = os.path.basename(root)
            skills.append((spath, rel, name_dir))
    total = 0
    entries = []
    for spath, rel, name_dir in skills:
        with open(spath, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
        fm, body = parse_frontmatter(text)
        skill_name = fm.get("name") or name_dir
        desc = fm.get("description") or ""
        if not desc:
            # fall back to the first readable body line so the library never
            # shows "(no description)". Skip TOC/list/link/numbering artifacts.
            for line in body.splitlines():
                line = line.strip()
                if line.startswith(">"):
                    line = line.lstrip(">").strip()
                if not line or line.startswith(("#", "-", "*", "[", "<", ".")):
                    continue
                if re.match(r"^\d+[.)]", line):
                    continue
                desc = line
                break
        entries.append((skill_name, name_dir, desc))
        if not library_only:
            doc = generate_doc(spath, skill_name, fm, body)
            rel_dir = os.path.dirname(rel)
            docpath = skill_doc_path(skill_name, rel_dir)
            with open(docpath, "w", encoding="utf-8") as f:
                f.write(doc)
            total += 1
    generate_library(entries)
    print(f"Generated {len(entries)} library entries -> {LIBRARY_PATH}")
    if total:
        print(f"Generated {total} skill docs in {DOCS_DIR}")
    _sync_monkeycode()
    return 0


def _sync_monkeycode() -> None:
    """Keep the MonkeyCode bridge in sync after a library regeneration."""
    import subprocess
    sync = os.path.join(ROOT, "scripts", "monkeycode_sync.py")
    if not os.path.exists(sync):
        return
    try:
        subprocess.run([sys.executable, sync, "--quiet"], check=True,
                       capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"[sync] monkeycode_sync failed (non-fatal): {e.stderr.strip()}")


if __name__ == "__main__":
    sys.exit(main())