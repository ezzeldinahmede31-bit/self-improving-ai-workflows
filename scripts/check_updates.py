#!/usr/bin/env python3
"""
check_updates.py — GitHub → client: check updates + the accept/reject right.

Principle: nothing is ever applied automatically to the user's machine. Every
new release is shown with its changelog, and the user accepts (applies after a
local security scan) or rejects (the decision is recorded, never asked again).

Without the `gh` CLI: uses the GitHub REST API via urllib + GITHUB_TOKEN
(optional for public reads). Applying is done via git fetch of the tag.

Usage:
    venv/bin/python scripts/check_updates.py [--check-only]
        [--yes (accept all)] [--apply <tag>] [--reject <tag>]

State: memory/.skillopt-sleep/updates-state.json
    {"current": "<tag>", "decided": {"<tag>": "accepted|rejected"}}
"""

import json
import os
import subprocess
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UPSTREAM_PATH = ROOT / "memory" / ".skillopt-sleep" / "upstream.json"
UPDATES_STATE = ROOT / "memory" / ".skillopt-sleep" / "updates-state.json"
VENV_PY = ROOT / "venv" / "bin" / "python"

APPLY_PATHS = [".opencode/skills", "scripts", "README.md", "CONTRIBUTING.md",
               "Makefile", ".github"]


def run(cmd, timeout=120):
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


def api_get(url, token=""):
    headers = {"Accept": "application/vnd.github+json",
               "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def list_releases(repo, token):
    try:
        data = api_get(f"https://api.github.com/repos/{repo}/releases?per_page=10", token)
        return data if isinstance(data, list) else []
    except Exception as e:
        print(f"❌ Cannot reach releases for {repo}: {e}")
        return []


def pending_releases(releases, state):
    decided = state.get("decided", {})
    current = state.get("current")
    out = []
    for r in releases:
        tag = r.get("tag_name", "")
        if not tag or decided.get(tag):
            continue
        if current and tag == current:
            continue
        out.append(r)
        if tag == current:
            break
    # no recorded current: show everything undecided
    return out


def apply_release(repo, tag, state):
    """Apply a release after a local security scan + backup. True on success."""
    print(f"\nApplying {tag} ...")
    dirty = run(["git", "status", "--porcelain"] + APPLY_PATHS)
    if (dirty.stdout or "").strip():
        print("❌ Working tree has local changes in update paths. Commit/stash first.")
        return False

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = f"backup/pre-update-{ts}"
    run(["git", "branch", backup])
    print(f"   backup branch: {backup}")

    f = run(["git", "fetch", "origin", "tag", tag])
    if f.returncode != 0:
        # remote tags may not exist yet — try a general fetch
        f = run(["git", "fetch", "origin", "--tags"])
    c = run(["git", "checkout", tag, "--"] + APPLY_PATHS)
    if c.returncode != 0:
        print(f"❌ checkout failed: {(c.stderr or '')[:300]}")
        return False

    # local security scan of what would be applied
    sys.path.insert(0, str(ROOT / "scripts"))
    from security_scan import scan_tree
    findings = []
    for p in APPLY_PATHS:
        target = ROOT / p
        if target.exists():
            findings += scan_tree(target)
    blocking = [x for x in findings if x["kind"] == "blocking"]
    if blocking:
        print("Update contains BLOCKING findings — NOT applied, rolled back:")
        for b in blocking[:10]:
            print(f"   - {b['label']} in {b['file']}:{b['line']}")
        run(["git", "checkout", "HEAD", "--"] + APPLY_PATHS)
        return False

    # register new skills in the router
    skills_dir = ROOT / ".opencode" / "skills"
    if skills_dir.exists():
        for d in sorted(skills_dir.iterdir()):
            if d.is_dir() and (d / "SKILL.md").exists():
                run([str(VENV_PY), "scripts/router_register.py", d.name])

    state["current"] = tag
    state.setdefault("decided", {})[tag] = "accepted"
    save_json(UPDATES_STATE, state)
    run(["git", "add"] + APPLY_PATHS)
    run(["git", "commit", "-m", f"chore: accept upstream update {tag}\n\nBackup: {backup}"])
    print(f"{tag} applied and committed (backup: {backup})")
    return True


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--check-only", action="store_true")
    ap.add_argument("--yes", action="store_true")
    ap.add_argument("--apply", default="")
    ap.add_argument("--reject", default="")
    args = ap.parse_args()

    upstream = load_json(UPSTREAM_PATH, {})
    repo = upstream.get("repo") or os.environ.get("GITHUB_REPO", "")
    token = os.environ.get("GITHUB_TOKEN", "")
    state = load_json(UPDATES_STATE, {})

    if not repo:
        print("ℹ️  No upstream configured yet.")
        print(f"   Setup: echo '{{\"repo\": \"OWNER/REPO\"}}' > {UPSTREAM_PATH.relative_to(ROOT)}")
        return 0

    if args.reject:
        state.setdefault("decided", {})[args.reject] = "rejected"
        save_json(UPDATES_STATE, state)
        print(f"✅ {args.reject} rejected — you won't be asked again.")
        return 0

    if args.apply:
        return 0 if apply_release(repo, args.apply, state) else 1

    releases = list_releases(repo, token)
    if not releases:
        print("ℹ️  No releases published upstream yet.")
        return 0

    pending = pending_releases(releases, state)
    if not pending:
        print(f"✅ Up to date (current: {state.get('current', '(unknown)')}).")
        return 0

    print(f"{len(pending)} update(s) available:\n")
    for r in pending:
        print(f"--- {r.get('tag_name')} ({(r.get('published_at') or '')[:10]}) ---")
        print((r.get("body") or "(no changelog)")[:1200])
        print()

    if args.check_only:
        return 0

    for r in pending:
        tag = r["tag_name"]
        if args.yes:
            ans = "y"
        else:
            try:
                ans = input(f"Accept update {tag}? [y/n] ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\nDeferred — will ask again next time.")
                return 0
        if ans in ("y", "yes", "ok"):
            if not apply_release(repo, tag, state):
                print(f"{tag} NOT applied (see above). Stopping.")
                return 1
        else:
            state.setdefault("decided", {})[tag] = "rejected"
            save_json(UPDATES_STATE, state)
            print(f"✅ {tag} rejected — recorded, won't ask again.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
