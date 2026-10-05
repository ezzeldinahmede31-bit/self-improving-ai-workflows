#!/usr/bin/env python3
"""
security_scan.py — الفحص الأمني المشترك لكل محتوى قادم من الخارج.

يُستخدم في:
  1. discover_skills.py — قبل اعتماد أي مهارة من الإنترنت.
  2. .github/workflows/verify_update.yml — التحقق من إضافات العملاء قبل الدمج.
  3. check_updates.py — فحص التحديثات القادمة من GitHub قبل التطبيق محليًا.

السياسة:
  - أسرار مكشوفة (API keys/tokens/private keys) → قابلة للإصلاح التلقائي
    (استبدال بقيمة عنصر نائب + وسم needs-review).
  - كود خطر (subprocess/eval/exec/pipe-to-shell/rm -rf /) → حاجب (blocking)،
    لا إصلاح تلقائي له (قرار دلالي يحتاج بشرًا).
  - حد حجم اختياري للمجلدات.

Usage:
    venv/bin/python scripts/security_scan.py <path> [--autofix] [--json]
      [--max-mb 2]

Exit codes: 0 نظيف | 1 ثغرات أُصلحت تلقائيًا (غير حاجبة) | 2 ثغرات حاجبة متبقية.
"""

import json
import re
import sys
from pathlib import Path

SECRET_PATTERNS = [
    (r"AKIA[0-9A-Z]{16}", "AWS access key"),
    (r"ghp_[A-Za-z0-9]{20,}", "GitHub PAT"),
    (r"gho_[A-Za-z0-9]{20,}", "GitHub OAuth token"),
    (r"github_pat_[A-Za-z0-9_]{10,}", "GitHub fine-grained PAT"),
    (r"sk-(live|test|ant)-[A-Za-z0-9_-]{8,}", "API secret key"),
    (r"xox[baprs]-[A-Za-z0-9-]{8,}", "Slack token"),
    (r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----", "private key"),
    (r"(?i)(api[_-]?key|api[_-]?secret|secret[_-]?key)\s*[:=]\s*['\"][^'\"]{8,}['\"]",
     "hardcoded secret"),
    (r"(?i)(password|passwd|pwd)\s*[:=]\s*['\"][^'\"]{4,}['\"]", "hardcoded password"),
]

DANGEROUS_CODE = [
    (r"\bsubprocess\b", "subprocess"),
    (r"\bos\.system\s*\(", "os.system"),
    (r"\bos\.popen\s*\(", "os.popen"),
    (r"(?<![A-Za-z0-9_])eval\s*\(", "eval()"),
    (r"(?<![A-Za-z0-9_])exec\s*\(", "exec()"),
    (r"child_process", "child_process"),
    (r"curl[^\n]*\|\s*(ba)?sh", "curl-pipe-shell"),
    (r"wget[^\n]*\|\s*(ba)?sh", "wget-pipe-shell"),
    (r"rm\s+-rf\s+/", "rm -rf /"),
    (r"pickle\.loads\s*\(", "pickle.loads"),
]

SCAN_EXTENSIONS = (".md", ".py", ".js", ".ts", ".sh", ".yml", ".yaml", ".json")
CODE_EXTENSIONS = (".py", ".js", ".ts", ".sh")
MAX_FILE_BYTES = 1_000_000


def iter_files(root: Path):
    if root.is_file():
        yield root
        return
    for p in sorted(root.rglob("*")):
        if p.is_file() and not p.is_symlink():
            yield p


def scan_tree(root: Path, max_mb: float = 0):
    """يفحص شجرة ملفات. يعيد قائمة findings: {kind,file,line,label,match}."""
    findings = []
    if max_mb and root.is_dir():
        total = sum(p.stat().st_size for p in root.rglob("*") if p.is_file())
        if total / (1024 * 1024) > max_mb:
            findings.append({"kind": "blocking", "file": ".",
                             "line": 0, "label": "oversize",
                             "match": f"{total/1024/1024:.1f}MB > {max_mb}MB cap"})
    for p in iter_files(root):
        if p.suffix.lower() not in SCAN_EXTENSIONS:
            continue
        try:
            if p.stat().st_size > MAX_FILE_BYTES:
                continue
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        rel = str(p.relative_to(root)) if root.is_dir() else p.name
        for i, line in enumerate(text.splitlines(), 1):
            for pat, label in SECRET_PATTERNS:
                m = re.search(pat, line)
                if m:
                    findings.append({"kind": "fixable", "file": rel, "line": i,
                                     "label": f"SECRET:{label}",
                                     "match": m.group(0)[:80]})
        if p.suffix.lower() in CODE_EXTENSIONS:
            for i, line in enumerate(text.splitlines(), 1):
                for pat, label in DANGEROUS_CODE:
                    m = re.search(pat, line)
                    if m:
                        findings.append({"kind": "blocking", "file": rel, "line": i,
                                         "label": f"DANGEROUS:{label}",
                                         "match": m.group(0)[:80]})
    return findings


def autofix_tree(root: Path, findings):
    """يصلّح الثغرات القابلة للإصلاح (الأسرار فقط). يعيد (fixed, remaining)."""
    fixed, remaining = 0, []
    by_file = {}
    for f in findings:
        if f["kind"] == "fixable":
            by_file.setdefault(f["file"], []).append(f)
        else:
            remaining.append(f)
    for rel, items in by_file.items():
        p = (root / rel) if root.is_dir() else root
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            remaining.extend(items)
            continue
        for item in items:
            for pat, label in SECRET_PATTERNS:
                new_text, n = re.subn(pat, f"[REDACTED:{label}]", text)
                if n:
                    text, fixed = new_text, fixed + n
        try:
            p.write_text(text, encoding="utf-8")
        except Exception:
            remaining.extend(items)
    return fixed, remaining


def format_flags(findings):
    return [f"{f['label']} in {f['file']}:{f['line']}" for f in findings]


def scan_security(root):
    """واجهة توافق مع discover_skills.py — تعيد (flags[], notes[])."""
    root = Path(root)
    return format_flags(scan_tree(root)), []


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--autofix", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--max-mb", type=float, default=0)
    args = ap.parse_args()

    root = Path(args.path)
    if not root.exists():
        print(f"❌ Path not found: {root}")
        return 2

    findings = scan_tree(root, args.max_mb)
    fixed = 0
    if args.autofix and any(f["kind"] == "fixable" for f in findings):
        fixed, findings = autofix_tree(root, findings)
        print(f"🔧 autofixed {fixed} secret occurrence(s)")

    blocking = [f for f in findings if f["kind"] == "blocking"]
    if args.json:
        print(json.dumps({"fixed": fixed, "findings": findings,
                          "blocking": len(blocking)}, ensure_ascii=False, indent=2))
    else:
        if not findings:
            print("✅ clean — no secrets, no dangerous code")
        for f in findings:
            mark = "⛔ BLOCKING" if f["kind"] == "blocking" else "⚠️  FIXABLE"
            print(f"{mark} {f['label']} in {f['file']}:{f['line']}")

    if blocking:
        return 2
    return 1 if (fixed or findings) else 0


if __name__ == "__main__":
    sys.exit(main())
