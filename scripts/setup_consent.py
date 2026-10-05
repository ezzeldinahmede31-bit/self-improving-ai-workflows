#!/usr/bin/env python3
"""
setup_consent.py — install-time consent gate.

Principle: nothing leaves your machine without your explicit consent, recorded
once at setup time. Re-run this script any time to change your decision.

- Accept → sharing enabled (metadata only + explicit approval per send)
  in exchange for receiving network improvements.
- Decline → fully local usage, zero sending. Perfectly fine — nobody forces you.

Usage:
    venv/bin/python scripts/setup_consent.py [--accept | --decline]
    make setup
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONSENT_PATH = ROOT / "memory" / ".skillopt-sleep" / "consent.json"
UPSTREAM_PATH = ROOT / "memory" / ".skillopt-sleep" / "upstream.json"


def load_consent():
    try:
        with open(CONSENT_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_consent(contribute: bool):
    CONSENT_PATH.parent.mkdir(parents=True, exist_ok=True)
    data = {"contribute": contribute,
            "scope": "metadata-only + explicit approval per send" if contribute else "local-only",
            "at": datetime.now().isoformat()}
    with open(CONSENT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return data


def check_consent(interactive=False):
    """True = sending allowed. Missing/False + interactive → ask and record.

    interactive=False (e.g. background git hook): the safe default = no sending.
    """
    data = load_consent()
    if "contribute" in data:
        return bool(data["contribute"])
    if not interactive:
        return False
    print("\n" + "=" * 60)
    print("First use of the sharing tools — we need your consent (once):")
    print("  - What gets sent: metadata only (skill names + numbers) + explicit")
    print("    approval before every send — never any silent sending.")
    print("  - In exchange: you receive network improvements (accept/reject is")
    print("    always yours).")
    print("  - Declining is fine: fully local usage, zero sending.")
    print("=" * 60)
    try:
        ans = input("Agree to share? [y/n] ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("\nNo consent recorded — nothing will be sent.")
        return False
    ok = ans in ("y", "yes", "ok")
    save_consent(ok)
    print("Consent recorded — thank you for sharing." if ok
          else "Decline recorded — local-only, won't ask again here.")
    return ok


def ask(prompt, default=""):
    try:
        ans = input(prompt).strip()
        return ans if ans else default
    except (EOFError, KeyboardInterrupt):
        return default


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--accept", action="store_true")
    ap.add_argument("--decline", action="store_true")
    args = ap.parse_args()

    print("=" * 60)
    print("Self-Improving AI Workflows setup — consent first")
    print("=" * 60)

    if args.accept:
        save_consent(True)
        print("Consent recorded (--accept).")
    elif args.decline:
        save_consent(False)
        print("Decline recorded (--decline) — local-only mode.")
        return 0
    else:
        cur = load_consent().get("contribute")
        if cur is True:
            print("Current status: sharing **accepted**.")
        elif cur is False:
            print("Current status: **declined** (local-only).")
        else:
            print("No consent recorded yet.")
        print()
        print("The trade, honestly:")
        print("  Accept → your improvements (metadata + your approval each time)")
        print("            strengthen the network, and you receive everyone's")
        print("            improvements (you accept/reject each one).")
        print("  Decline → everything stays local, not a single bit leaves.")
        print("            Perfectly fine.")
        ans = ask("\nAgree to share? [y/n] (default: n): ", "n")
        ok = ans.lower() in ("y", "yes", "ok")
        save_consent(ok)
        print("Consent recorded." if ok else "Decline recorded — local-only.")

    if not load_consent().get("contribute"):
        print("\nSkipping network setup (local mode).")
        print("   To change your mind later: venv/bin/python scripts/setup_consent.py")
        return 0

    # Network setup for contributors only
    print("\n--- Network setup (contributors) ---")
    repo = ask("Central repo OWNER/REPO (empty = later): ")
    if repo and "/" in repo:
        UPSTREAM_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(UPSTREAM_PATH, "w", encoding="utf-8") as f:
            json.dump({"repo": repo.strip()}, f, ensure_ascii=False, indent=2)
        print(f"Saved: {UPSTREAM_PATH.relative_to(ROOT)}")
    else:
        print("Skipped — reports stay in the local outbox until linked.")
    if not os.environ.get("GITHUB_TOKEN"):
        print("Tip: for writing to GitHub later: export GITHUB_TOKEN=ghp_... (never stored in files)")

    hook = ask("Install git hook for auto-sync? [y/n] (default: y): ", "y")
    if hook.lower() in ("y", "yes", "ok", ""):
        r = subprocess.run(["bash", "scripts/install_hook.sh"], cwd=str(ROOT))
        if r.returncode != 0:
            print("Could not install the hook — try later: make install-hook")
    else:
        print("Hook skipped — use make sync manually when you want.")
    print("\nSetup complete. Start with: make dev-cycle")
    return 0


if __name__ == "__main__":
    sys.exit(main())
