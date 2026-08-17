#!/usr/bin/env python3
"""Register newly installed skills into the compensatory-router SKILL.md.

Usage (from project root):
    venv/bin/python scripts/router_register.py <skill-name> [<skill-name> ...]

Reads each skill's frontmatter from .opencode/skills/<name>/SKILL.md, then:
  1. Adds a routing row to the proactive-stack table (trigger derived from the
     description's keywords, primary skill = the skill itself).
  2. Adds the skill to the matching family bucket in the registry section
     (keyword-matched; unknown families go to an "Auto-installed" bucket).
  3. Bumps the bucket count and the total count in the registry header.

Idempotent: a skill already present in the router is skipped silently.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ROUTER = ROOT / ".opencode" / "skills" / "compensatory-router" / "SKILL.md"
SKILLS_DIR = ROOT / ".opencode" / "skills"

FALLBACK_BUCKET = "Auto-installed (find-skills)"

# keyword -> registry bucket header (must match existing ### headers)
BUCKET_RULES = [
    ("Automation", ["automation", "workflow automation", "zap", "make (integromat)", "workflow-orchestration", "workflow-patterns", "webhook", "airtable", "sheets", "excel", "notion", "mailchimp", "jira", "linear", "trello", "asana", "clickup", "monday", "calendar", "docusign", "invoice", "quickbooks", "pipedrive", "shopify", "woocommerce", "linkedin", "twitter", "youtube", "spotify", "whatsapp", "twilio", "teams", "intercom", "zendesk", "home-assistant", "weather", "devops", "ansible", "hr", "transcription", "podcast", "obsidian", "security monitoring", "email", "crm", "hubspot", "salesforce"]),
    ("n8n", ["n8n"]),
    ("Zapier", ["zapier", "zaps", "durable workflow"]),
    ("Marketing/SEO/Growth", ["marketing", "seo", "keyword", "serp", "analytics", "ads", "landing", "copywrit", "blog", "email sequence", "newsletter", "lead magnet", "growth", "pricing", "positioning", "launch", "referral", "affiliate", "psychology", "persuasion", "cialdini", "hook", "content", "brand", "geo", "semrush", "ahrefs", "gsc", "competitor", "cro", "conversion", "onboarding", "signup", "demand gen", "icp", "community", "influencer", "council"]),
    ("Social media", ["social", "bluesky", "reddit", "thread", "tiktok", "wechat", "discord", "slack", "telegram", "feishu", "instagram", "facebook", "linkedin post"]),
    ("Video/Media", ["video", "ffmpeg", "media", "whisper", "transcri", "download", "yt-dlp", "podcast edit", "montage", "edit video", "inpaint"]),
    ("Research", ["research", "search", "literature", "academic", "semantic scholar", "arxiv", "company research", "customer research", "lead research", "deep research", "web search", "github research"]),
    ("Reasoning/Math/Logic", ["math", "reasoning", "logic", "olympiad", "algorithm", "equation", "counting", "boundary", "tot", "verifier", "benchmark", "symbolic", "proof"]),
    ("Thinking frames", ["thinking-", "frame", "socratic", "pre-mortem", "red-team", "steel-man", "probabilistic", "cynefin", "first-principles", "thought experiment", "triz", "via-negativa"]),
    ("Context/Memory/System", ["context", "memory", "token", "compression", "evaluation", "harness", "hosted", "latent briefing", "multi-agent", "project-development", "tool design", "bdi", "state-machine", "rate-limit", "compactor", "degradation"]),
    ("Agents/Architecture", ["agent", "architecture", "orchestrator", "squad", "tool", "autonomous", "workflow", "api-integration", "make-automation", "site-architecture", "git coworker"]),
    ("Security", ["security", "auth", "firebase", "owasp", "red team", "hardening", "ssrf", "secret", "gate"]),
    ("Coding/SWE", ["code", "swemaster", "swe-bench", "tdd", "debug", "algorithm design", "paper-to-code", "surgical", "refactor", "single-pass", "codebase", "ast", "decomposition", "git worktree", "review"]),
    ("Browser/Device", ["browser", "login", "session", "desktop", "gui", "captcha", "stealth", "playwright", "visual", "x11"]),
    ("Creative/Reasoning", ["analogy", "inversion", "lateral", "provocation", "scamper", "six-hats", "worst idea", "concept fan", "brainstorm", "council", "consensus", "emergent", "creative"]),
    ("Delivery/Gates", ["gate", "delivery", "verification", "omni", "clarify", "spec", "router", "find-skills", "deployment", "hitl", "audit"]),
    ("Dev utilities", ["i18n", "prompt", "banner", "organize", "image", "stock", "stars", "domain", "stripe", "brand"]),
    ("Superpowers pack — obra", ["superpowers", "plan", "execut", "brainstorm", "test-driven", "debug", "code-review", "subagent", "worktree", "finishing-a-development"]),
    ("Video-pack extras", ["remembering-conversations", "impeccable", "wizard"]),
]


def read_frontmatter(path):
    txt = path.read_text(encoding="utf-8", errors="replace")
    m = re.match(r"\A---\n(.*?)\n---", txt, re.S)
    if not m:
        return None, txt
    fm = m.group(1)
    name = re.search(r"^name:\s*(.+)$", fm, re.M)
    desc = re.search(r"^description:\s*(.+)$", fm, re.M)
    return (name.group(1).strip() if name else None,
            desc.group(1).strip() if desc else ""), txt


def classify(desc):
    dl = desc.lower()
    for bucket, kws in BUCKET_RULES:
        for kw in kws:
            if kw in dl:
                return bucket
    return FALLBACK_BUCKET


def _truncate_word_boundary(text, limit):
    """Cut at the last whitespace before `limit` so rows never end mid-word.

    Falls back to a hard cut if the text has no whitespace within the limit.
    """
    if len(text) <= limit:
        return text
    cut = text[:limit]
    space = cut.rfind(" ")
    if space > 0:
        cut = cut[:space]
    return cut.strip() + " …"


def ensure_routing_row(router_txt, name, desc):
    """Insert a routing row just before the '## Decision table' section."""
    row_marker = "## Decision table"
    if row_marker not in router_txt:
        return router_txt, False
    # already present? the row is '| 'Use <name>: ...' (Auto-registered) | `<name>` |'
    if re.search(r"\(Auto-registered\)\s*\|\s*`" + re.escape(name) + r"`\s*\|", router_txt):
        return router_txt, False
    first = _truncate_word_boundary(desc.split(".")[0], 90)
    trigger = f"'Use {name}: {first}'"
    row = (f"| {trigger} (Auto-registered) | `{name}` | {_truncate_word_boundary(desc, 400)} |\n")
    router_txt = router_txt.replace("## Decision table", row + "## Decision table", 1)
    return router_txt, True


def ensure_registry_entry(router_txt, name, bucket):
    """Add the skill to the matching '### bucket (N)' list line."""
    reg_marker = "## Full skill registry"
    if reg_marker not in router_txt:
        return router_txt, False
    # Only consider the registry section (from its header to EOF) for
    # presence checks and bucket headers — the routing table above also
    # mentions skill names in backticks.
    registry_part = router_txt[router_txt.index(reg_marker):]
    if re.search(r"`" + re.escape(name) + r"`", registry_part):
        return router_txt, False
    # header may carry a suffix between the bucket name and the count, e.g.
    # "### Automation (per-tool) (37)" — match the LAST parenthetical as count.
    header_re = re.compile(
        r"^### " + re.escape(bucket) + r"(?: \([^)]*\))* \((\d+)\)", re.M
    )
    m = header_re.search(router_txt)
    if m:
        lines = router_txt.splitlines(keepends=True)
        # find the list index of the line containing the header
        consumed = 0
        hdr_line_idx = None
        for i, ln in enumerate(lines):
            if consumed <= m.start() < consumed + len(ln):
                hdr_line_idx = i
                break
            consumed += len(ln)
        if hdr_line_idx is None:
            return router_txt, False
        # first following non-empty line = the bucket's content line
        nxt = hdr_line_idx + 1
        while nxt < len(lines) and not lines[nxt].strip():
            nxt += 1
        if nxt < len(lines):
            # bump the '### Bucket (N)' count
            lines[hdr_line_idx] = lines[hdr_line_idx].replace(
                f"({m.group(1)})", f"({int(m.group(1)) + 1})", 1
            )
            content = lines[nxt]
            if content.strip().startswith("|"):
                indent = content[: len(content) - len(content.lstrip())]
                lines[nxt] = f"{indent}`{name}` (D) - " + content.lstrip()
            else:
                lines[nxt] = content.rstrip() + f" - `{name}` (D)\n"
            router_txt = "".join(lines)
            return router_txt, True
    else:
        # create the bucket at the end of the registry (before the final line)
        if re.search(r"`" + re.escape(name) + r"`", registry_part):
            return router_txt, False
        block = f"\n### {bucket} (1)\n`{name}` (D)\n"
        router_txt = router_txt.rstrip() + "\n" + block
        return router_txt, True
    return router_txt, False


def bump_total(router_txt, n=1):
    m = re.search(r"## Full skill registry \(complete inventory — (\d+) installed\)", router_txt)
    if m and n > 0:
        router_txt = router_txt.replace(m.group(0), m.group(0).replace(m.group(1), str(int(m.group(1)) + n)), 1)
    return router_txt


def main(names=None):
    if names is None:
        names = sys.argv[1:]
    names = [n.strip("/") for n in names]
    if len(names) < 1:
        print("usage: router_register.py <skill-name> [...]")
        return 1
    router_txt = ROUTER.read_text(encoding="utf-8")
    new_skills = []
    for name in names:
        skill_dir = SKILLS_DIR / name
        if not (skill_dir / "SKILL.md").exists():
            print(f"[skip] {name}: not found in .opencode/skills/")
            continue
        (name_ok, desc), _ = read_frontmatter(skill_dir / "SKILL.md")
        if not desc:
            print(f"[skip] {name}: no description in frontmatter")
            continue
        bucket = classify(desc)
        router_txt, row_added = ensure_routing_row(router_txt, name, desc)
        router_txt, reg_added = ensure_registry_entry(router_txt, name, bucket)
        is_new = row_added or reg_added
        if is_new:
            new_skills.append(name)
        print(f"[ok] {name} -> bucket '{bucket}' (row={'yes' if row_added else 'no'}, registry={'yes' if reg_added else 'no'})")
    router_txt = bump_total(router_txt, len(new_skills))
    ROUTER.write_text(router_txt, encoding="utf-8")
    print(f"new: +{len(new_skills)} skill(s) ({', '.join(new_skills) if new_skills else 'none'})")
    if new_skills:
        gen = ROOT / "scripts" / "skills_docs_generator.py"
        if gen.exists():
            try:
                subprocess.run(
                    [sys.executable, str(gen), "--library-only"],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                print("[lib] memory/skills-library.md refreshed")
            except subprocess.CalledProcessError as e:
                print(f"[lib] refresh failed (non-fatal): {e.stderr.strip()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
