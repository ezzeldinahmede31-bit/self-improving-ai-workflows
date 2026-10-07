#!/usr/bin/env python3
"""device_permissions.py — Claude-order permission gate: Deny > Ask > Allow.

Rules use the Tool(spec) format from Claude Code docs:
  Bash(npm run *)   wildcard * matches any text
  Read(./path)      path prefix match
  Edit(src/**)      glob match
  WebFetch(domain:github.com)
  Bash / Read       bare name = match all uses of the tool

Evaluation: every DENY rule first, then ASK, then ALLOW. No match -> default
(ask for write/exec tools, allow for read-only tools).

Usage:
  device_permissions.py check --tool Bash --input "git status"
  device_permissions.py check --tool Bash --input "rm -rf /"      -> DENY
  device_permissions.py selftest
Policy lives in device_policy.json next to this script (edit it to change
the Ask-first posture). Exits 0=ALLOW, 10=ASK, 20=DENY.
"""
import fnmatch
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
POLICY_FILE = HERE / "device_policy.json"

DEFAULT_POLICY = {
    "rules": [
        {"tool": "Bash", "pattern": "rm -rf *", "tier": "deny"},
        {"tool": "Bash", "pattern": "sudo rm*", "tier": "deny"},
        {"tool": "Bash", "pattern": "sudo *", "tier": "ask"},
        {"tool": "Bash", "pattern": "git push --force*", "tier": "deny"},
        {"tool": "Bash", "pattern": "git status*", "tier": "allow"},
        {"tool": "Bash", "pattern": "git diff*", "tier": "allow"},
        {"tool": "Bash", "pattern": "git log*", "tier": "allow"},
        {"tool": "Bash", "pattern": "ls*", "tier": "allow"},
        {"tool": "Bash", "pattern": "pwd", "tier": "allow"},
        {"tool": "Bash", "pattern": "wmctrl -l*", "tier": "allow"},
        {"tool": "Bash", "pattern": "git push*", "tier": "ask"},
        {"tool": "Read", "pattern": "*.env", "tier": "deny"},
        {"tool": "Read", "pattern": "*.env.*", "tier": "deny"},
        {"tool": "Read", "pattern": "~/.ssh/*", "tier": "deny"},
        {"tool": "Read", "pattern": "memory/.sessions/*", "tier": "deny"},
        {"tool": "Read", "pattern": "*", "tier": "allow"},
        {"tool": "Edit", "pattern": "*", "tier": "ask"},
        {"tool": "Write", "pattern": "*", "tier": "ask"},
        {"tool": "WebFetch", "pattern": "*", "tier": "allow"},
    ],
    "default": {"Read": "allow", "Glob": "allow", "Grep": "allow"},
}


def load_policy():
    if not POLICY_FILE.exists():
        POLICY_FILE.write_text(json.dumps(DEFAULT_POLICY, indent=2))
        return DEFAULT_POLICY
    return json.loads(POLICY_FILE.read_text())


def match_rule(pattern, value, is_path=False):
    if pattern in ("*", ""):
        return True
    if is_path or "/" in pattern:
        return fnmatch.fnmatch(value, pattern) or value.startswith(
            pattern.rstrip("*")
        )
    return fnmatch.fnmatchcase(value, pattern)


def evaluate(tool, value="", policy=None):
    policy = policy or load_policy()
    rules = [r for r in policy["rules"] if r["tool"] == tool]
    is_path = tool in ("Read", "Edit", "Write", "Glob")
    for tier in ("deny", "ask", "allow"):
        for r in rules:
            if r["tier"] == tier and match_rule(
                r.get("pattern", "*"), value, is_path
            ):
                return tier, r
    return policy.get("default", {}).get(tool, "ask"), None


def main(argv):
    if len(argv) >= 2 and argv[1] == "selftest":
        cases = [
            ("Bash", "git status", "allow"),
            ("Bash", "rm -rf /tmp/x", "deny"),
            ("Bash", "sudo apt update", "ask"),
            ("Bash", "npm run build", "ask"),
            ("Read", "src/app.py", "allow"),
            ("Read", ".env", "deny"),
            ("Read", "memory/.sessions/x", "deny"),
            ("Edit", "src/app.py", "ask"),
            ("WebFetch", "https://example.com", "allow"),
        ]
        failed = 0
        for tool, value, want in cases:
            got, _ = evaluate(tool, value)
            ok = got == want
            failed += not ok
            print(f"{'PASS' if ok else 'FAIL'} {tool}({value!r}) = {got} (want {want})")
        print("SELFTEST " + ("OK" if not failed else f"{failed} FAILURES"))
        return 1 if failed else 0
    if len(argv) >= 4 and argv[1] == "check":
        tool = argv[argv.index("--tool") + 1]
        value = argv[argv.index("--input") + 1] if "--input" in argv else ""
        tier, rule = evaluate(tool, value)
        print(f"{tier.upper()} tool={tool} input={value!r} rule={rule}")
        return {"allow": 0, "ask": 10, "deny": 20}[tier]
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
