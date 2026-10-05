#!/usr/bin/env python3
"""
report_update.py — client → GitHub: local-update notification (metadata only by default).

Principles (post design review):
  1. Voluntary: sharing is optional and on by default — turn it off any time
     ([skip-sync] in a commit message, or simply don't run this script).
  2. Metadata only by default: sends skill names + stats + file list
     (no diffs, no content, no CLAUDE.md/memory).
  3. Explicit approval: shows exactly what will be sent and asks [y/n] — never
     any silent sending, except with --yes (conscious automation).
  4. --send-content: attaches *new* skill files only, after a security scan +
     autofix — and always excludes: memory/, CLAUDE.md, .env, secrets.

Without the `gh` CLI: uses the GitHub REST API via urllib + GITHUB_TOKEN.
Without upstream setup: saves the report to a local outbox until linked.

Usage:
    venv/bin/python scripts/report_update.py [--force] [--yes] [--send-content]
"""

import hashlib
import json
import os
import socket
import subprocess
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from setup_consent import check_consent  # consent gate — no sending without consent
UPSTREAM_PATH = ROOT / "memory" / ".skillopt-sleep" / "upstream.json"
UPDATES_STATE = ROOT / "memory" / ".skillopt-sleep" / "updates-state.json"
OUTBOX = ROOT / ".skillopt-sleep" / "outbox"
WATCH_PREFIXES = (".opencode/skills", "scripts/")

# never leaves the machine, even with --send-content
NEVER_SEND = ("memory/", "CLAUDE.md", ".env", ".operator/",
              ".skillopt-sleep/", "venv/", ".git/")


def run(cmd, timeout=60):
    try:
        return subprocess.run(cmd, cwd=str(ROOT), capture_output=True,
                              text=True, timeout=timeout)
    except Exception as e:
        return subprocess.CompletedProcess(cmd, 1, "", str(e))


def load_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def client_fingerprint():
    raw = socket.gethostname() + "|" + os.path.expanduser("~")
    return hashlib.sha256(raw.encode()).hexdigest()[:12]


def collect_metadata(since_sha):
    """Metadata only: skill names + stats — no content, no diffs."""
    if since_sha:
        stat = run(["git", "diff", "--numstat", f"{since_sha}..HEAD"])
        status = run(["git", "diff", "--name-status", f"{since_sha}..HEAD"])
    else:
        stat = run(["git", "diff", "--numstat"])
        status = run(["git", "status", "--porcelain"])
    numstat = {}
    for line in (stat.stdout or "").splitlines():
        parts = line.split()
        if len(parts) >= 3:
            numstat[parts[2]] = (parts[0], parts[1])
    skills, files = set(), []
    for line in (status.stdout or "").splitlines():
        line = line.strip()
        if not line:
            continue
        path = line.split()[-1]
        if not path.startswith(WATCH_PREFIXES):
            continue
        if any(path.startswith(n) for n in NEVER_SEND):
            continue
        ins, dele = numstat.get(path, ("?", "?"))
        files.append({"path": path, "added": ins, "deleted": dele})
        if path.startswith(".opencode/skills/"):
            segs = path.split("/")
            if len(segs) > 2:
                skills.add(segs[2])
    head = run(["git", "rev-parse", "HEAD"])
    return sorted(skills), files, (head.stdout or "").strip()


def collect_content(skills):
    """New skill files only — after security scan + fix. Returns (text, files)."""
    sys.path.insert(0, str(ROOT / "scripts"))
    from security_scan import scan_tree, autofix_tree
    chunks, included = [], []
    skills_dir = ROOT / ".opencode" / "skills"
    for skill in skills:
        md = skills_dir / skill / "SKILL.md"
        if not md.exists():
            continue
        findings = scan_tree(md)
        blocking = [f for f in findings if f["kind"] == "blocking"]
        if blocking:
            return None, [f"BLOCKED {skill}: security gate — will not send ({blocking[0]['label']})"]
        autofix_tree(md.parent, findings)  # redact secrets before sending
        try:
            text = md.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if len(text) > 20000:
            text = text[:20000] + "\n…(truncated)"
        chunks.append(f"\n### SKILL.md — {skill}\n\n```markdown\n{text}\n```")
        included.append(f".opencode/skills/{skill}/SKILL.md")
    return "\n".join(chunks), included


def build_body(fp, skills, files, head_sha, content, included):
    total_add = sum(int(f["added"]) for f in files if str(f["added"]).isdigit())
    total_del = sum(int(f["deleted"]) for f in files if str(f["deleted"]).isdigit())
    lines = [
        "## Client Update Report (metadata)",
        "",
        f"- **Client**: `{fp}` (anonymous fingerprint)",
        f"- **At**: {datetime.now().isoformat()}",
        f"- **HEAD**: `{head_sha[:12]}`",
        f"- **Skills**: {', '.join(f'`{s}`' for s in skills) or '(none)'}",
        f"- **Files**: {len(files)} (+{total_add}/-{total_del} lines)",
        "",
        "### Files (names + stats only — no content, no diffs)",
        "",
    ]
    for f in files[:60]:
        lines.append(f"- `{f['path']}` (+{f['added']}/-{f['deleted']})")
    if len(files) > 60:
        lines.append(f"- … and {len(files) - 60} more")
    if content is not None:
        lines += ["", "### Attached skill content (NEW files only, security-scanned)",
                  ", ".join(f"`{p}`" for p in included) or "(none)", content]
    lines += [
        "",
        "### Reviews (automation)",
        "- `verify_update.yml` will security-scan the additions, auto-redact secrets, and stop the merge on any blocker.",
        "- **Merging requires human review — no auto-merge for client contributions.**",
        "- After publishing as a Release, every user has the **accept or reject** right (`make check-updates`).",
        "",
        "_Auto-generated by `scripts/report_update.py` (metadata-only mode)._",
    ]
    return "\n".join(lines)


def ask_approval(preview):
    print("\n" + "=" * 60)
    print("What will be sent to GitHub (review before approving):")
    print("=" * 60)
    print(preview[:3000])
    if len(preview) > 3000:
        print(f"... (+{len(preview) - 3000} chars)")
    print("=" * 60)
    try:
        ans = input("Send this report? [y/n] ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("\nCancelled — nothing will be sent.")
        return False
    return ans in ("y", "yes", "ok")


def post_issue(repo, token, title, body):
    req = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/issues",
        data=json.dumps({"title": title, "body": body,
                         "labels": ["client-update"]}).encode(),
        headers={"Authorization": f"Bearer {token}",
                 "Accept": "application/vnd.github+json",
                 "X-GitHub-Api-Version": "2022-11-28"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r).get("html_url")


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--yes", action="store_true",
                    help="skip the approval question (conscious automation only)")
    ap.add_argument("--send-content", action="store_true",
                    help="attach new skill content after the security scan")
    args = ap.parse_args()

    if not (ROOT / ".git").exists():
        print("❌ Not a git repository")
        return 1

    # install-time consent gate: decline = zero sending, fine
    if not check_consent(interactive=True):
        print("Sharing is off (no consent) — nothing will be sent.")
        print("   To change your mind: venv/bin/python scripts/setup_consent.py")
        return 0

    state = load_json(UPDATES_STATE, {})
    since = None if args.force else state.get("last_reported_sha")
    skills, files, head = collect_metadata(since)

    if not files and not args.force:
        print("ℹ️  No new watched-path changes since last report — nothing to notify.")
        return 0

    content, included = None, []
    if args.send_content:
        if not skills:
            print("ℹ️  --send-content but no new skills — sending metadata only.")
        else:
            content, included = collect_content(skills)
            if content is None:
                print("\n".join(included))  # block reasons
                print("Content blocked by security — send metadata only or fix first.")
                content = None
                # continue as metadata-only after fresh approval
    fp = client_fingerprint()
    title = f"Client update {fp} — {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    body = build_body(fp, skills, files, head, content, included)

    # approval gate — mandatory unless --yes
    if not args.yes:
        if not ask_approval(f"# {title}\n\n{body}"):
            print("Cancelled on your request — nothing sent, nothing saved.")
            return 0

    upstream = load_json(UPSTREAM_PATH, {})
    repo = upstream.get("repo") or os.environ.get("GITHUB_REPO", "")
    token = os.environ.get("GITHUB_TOKEN", "")

    if not repo or not token:
        OUTBOX.mkdir(parents=True, exist_ok=True)
        out = OUTBOX / f"report-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{fp}.md"
        out.write_text(f"# {title}\n\n{body}\n", encoding="utf-8")
        print(f"⏳ No upstream configured — queued locally: {out.relative_to(ROOT)}")
        print(f"   Setup: echo '{{\"repo\": \"OWNER/REPO\"}}' > {UPSTREAM_PATH.relative_to(ROOT)}")
        return 0

    try:
        url = post_issue(repo, token, title, body)
    except Exception as e:
        print(f"❌ Issue creation failed: {e}")
        return 1

    state["last_reported_sha"] = head
    save_json(UPDATES_STATE, state)
    print(f"✅ Update reported (by your approval): {url}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
