#!/usr/bin/env python3
"""
discover_skills.py — محرك الاكتشاف الخارجي (Internet skill discovery).

ضمن دورة التطوير الذاتي (بعد "اه"): يشتق كلمات بحث من شغل اليوم، يدور على
https://skills.sh عبر `npx skills find`، يجيب المرشحين، يظبط ملفاتهم برمجيًا
(frontmatter + paths + adapter wrapper للأنظمة غير المعمولة كمهارة)، يفحصهم
أمنيًا، ثم إما يعتمد (trusted + نظيف + --auto-adopt) أو يخزن للمراجعة.

Usage:
    venv/bin/python scripts/discover_skills.py [--queries q1 q2 ...]
        [--auto-adopt] [--max-queries 5] [--max-installs 3]
        [--lookback-hours 24] [--dry-run] [--gates]

- --dry-run: اشتقاق + بحث فقط، بدون جلب أو تثبيت (read-only).
- --auto-adopt: اعتماد تلقائي فقط للمصادر الموثوقة النظيفة. غير ذلك staging.
- --gates: تشغيل build_gates_pipeline على المهارات المعتمدة (بطيء، opt-in).

الأمان (إلزامي، لا يمكن تخطيه):
- رفض أي محتوى فيه أسرار مكشوفة (API keys, tokens, private keys).
- رفض أي سكريبت فيه subprocess/eval/exec/os.system/pipe-to-shell.
- حد حجم: SKILL.md > 500 سطر = تحذير، مجلد المهارة > 2MB = رفض.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from security_scan import scan_security  # الفحص الأمني المشترك (مصدر واحد للحقيقة)

ROOT = Path(__file__).resolve().parent.parent
VENV_PY = ROOT / "venv" / "bin" / "python"
SLEEP_HOME = ROOT / "memory" / ".skillopt-sleep" / "home"
STATE_PATH = ROOT / "memory" / ".skillopt-sleep" / "discover-state.json"
CONFIG_PATH = ROOT / "memory" / ".skillopt-sleep" / "discover-config.json"
STAGING_ROOT = ROOT / ".skillopt-sleep" / "staging" / "discovered"
AGENTS_SKILLS = ROOT / ".agents" / "skills"
OPENCODE_SKILLS = ROOT / ".opencode" / "skills"

DEFAULT_CONFIG = {
    "watch_domains": [
        "n8n workflow automation", "testing playwright", "rag vector qdrant",
        "prompt engineering", "ci-cd github actions", "docker deploy",
    ],
    "trusted_owners": [
        "vercel-labs", "anthropics", "microsoft", "obra", "pbakaus", "mattpocock",
    ],
    "min_installs": 1000,
    "suspicious_below_installs": 100,
    "max_skill_dir_mb": 2,
    "max_skill_md_lines": 500,
}

STOPWORDS = set("""
a an and are as at be but by can do for from had has have he her his how i if in
is it its not of on or that the their then there these they this to was will with
you your we our us all any out up over into more most other some such than too
very just about also when what which who will would could should there their
skill skills error errors file files code using used use get set new add make
run test tests testing failed fail work working works need needs want like just
also even still back well much many long too very really thing things something
error failed failure bug bugs issue issues problem problems fix fixed fixing
please help thanks thankしよう task tasks session day today tonight yesterday
file path directory folder script output result results data value values
""".split())

FAILURE_SIGNALS = [
    "error", "failed", "failure", "traceback", "exception", "not working",
    "فشل", "مش شغال", "غلط", "خرب", "broken", "bug", "timeout", "rejected",
]
WISH_SIGNALS = [
    "i wish", "find a skill", "is there a skill", "لو كان عندنا", "محتاج مهارة",
    "عايز مهارة", "how do i", "can you do", "wish we had",
]

# (أنماط الفحص الأمني في scripts/security_scan.py — مصدر واحد للحقيقة)
PATH_REWRITES = [
    ("~/.claude/skills", ".opencode/skills"),
    ("~/.claude", "<project-root>"),
    (".agents/skills/", ".opencode/skills/"),
]

ADAPTER_TEMPLATE = """---
name: {slug}
description: "{description}"
---

# {title} (external adapter)

> **مصدر خارجي مُكيَّف**: جُلب من `{source}` ({installs} installs) عبر
> `discover_skills.py` بتاريخ {date}، وظُبطت مساراته وملفاته برمجيًا ليعمل
> داخل هذا المشروع. الأصل غير معمول لهذا النظام — هذا الملف **adapter**
> يشرح كيف نستخدمه هنا.

## ما هو

{summary}

- **المصدر**: https://skills.sh/{source_url}
- **المالك**: `{owner}` (موثوق: {trusted})
- **الحالة الأمنية**: فحص أسرار + فحص كود خطر = نظيف بتاريخ {date}

## كيف تستخدمه هنا

الأصل مثبت في `.agents/skills/{orig_dir}/`. هذه النسخة في
`.opencode/skills/{slug}/` بعد التعديلات:

{rewrites}

## خطوات الاستخدام

{usage}

## تحقق

- [ ] frontmatter صالح (`name` == اسم المجلد)
- [ ] لا أسرار مكشوفة
- [ ] لا استدعاءات خطرة في السكريبتات المرفقة
- [ ] مسجلة في الراوتر (`scripts/router_register.py {slug}`)

## Pairs with

find-skills, ai-skill-authoring-standards, build-gates-pipeline
"""


# ---------------------------------------------------------------- helpers

def run(cmd, timeout=120, cwd=None, inp=None):
    try:
        return subprocess.run(
            cmd, cwd=str(cwd or ROOT), input=inp, capture_output=True,
            text=True, timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(cmd, 124, "", "TIMEOUT")


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


def ensure_config():
    if not CONFIG_PATH.exists():
        save_json(CONFIG_PATH, DEFAULT_CONFIG)
        print(f"ℹ️  Created default config: {CONFIG_PATH}")
    cfg = load_json(CONFIG_PATH, {})
    merged = dict(DEFAULT_CONFIG)
    merged.update(cfg)
    return merged


def slugify(text, maxlen=60):
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return (slug or "external-skill")[:maxlen]


def parse_installs(raw):
    raw = (raw or "").strip().upper().replace(",", "")
    m = re.match(r"^([\d.]+)\s*([KMB])?$", raw)
    if not m:
        return 0
    num, suf = float(m.group(1)), (m.group(2) or "")
    return int(num * {"": 1, "K": 1_000, "M": 1_000_000, "B": 1_000_000_000}[suf])


# ---------------------------------------------------------------- queries

def installed_skill_tokens():
    toks = set()
    if OPENCODE_SKILLS.exists():
        for d in OPENCODE_SKILLS.iterdir():
            toks.update(re.findall(r"[a-z]{3,}", d.name.lower()))
    return toks


def mine_queries(lookback_hours, max_queries, watch_domains):
    """اشتقاق كلمات بحث من جلسات اليوم + watch domains."""
    cutoff = datetime.now() - timedelta(hours=lookback_hours)
    owned = installed_skill_tokens()
    weighted = Counter()
    sessions_read = 0

    if SLEEP_HOME.exists():
        for jf in SLEEP_HOME.glob("projects/*/*.jsonl"):
            try:
                if datetime.fromtimestamp(jf.stat().st_mtime) < cutoff:
                    continue
            except Exception:
                continue
            try:
                with open(jf, encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()
            except Exception:
                continue
            sessions_read += 1
            for line in lines:
                low = line.lower()
                try:
                    obj = json.loads(line)
                    text = json.dumps(obj, ensure_ascii=False).lower()
                except Exception:
                    text = low
                w = 1
                if any(s in text for s in FAILURE_SIGNALS):
                    w = 3
                if any(s in text for s in WISH_SIGNALS):
                    w = 4
                if w == 1:
                    continue
                for tok in re.findall(r"[a-z][a-z0-9_-]{3,}", text):
                    if tok in STOPWORDS or tok in owned:
                        continue
                    weighted[tok] += w

    # يوم هادئ بلا إشارات فشل/احتياج: خذ المواضيع العامة الغالبة (وزن 1)
    if not weighted and sessions_read:
        general = Counter()
        for jf in SLEEP_HOME.glob("projects/*/*.jsonl"):
            try:
                if datetime.fromtimestamp(jf.stat().st_mtime) < cutoff:
                    continue
            except Exception:
                continue
            try:
                with open(jf, encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        try:
                            text = json.dumps(json.loads(line), ensure_ascii=False).lower()
                        except Exception:
                            text = line.lower()
                        for tok in re.findall(r"[a-z][a-z0-9_-]{4,}", text):
                            if tok not in STOPWORDS and tok not in owned:
                                general[tok] += 1
            except Exception:
                continue
        for tok, cnt in general.most_common(max_queries * 3):
            if cnt >= 3:
                weighted[tok] = cnt

    queries = [t for t, _ in weighted.most_common(max_queries * 3)]
    # دمج watch domains (تكملة، لا استبدال لإشارة اليوم)
    for dom in watch_domains:
        if len(queries) >= max_queries * 2:
            break
        key = slugify(dom).replace("-", " ")
        if key and key not in queries:
            queries.append(dom)
    queries = queries[: max_queries * 2]
    return queries, sessions_read, weighted.most_common(10)


# ---------------------------------------------------------------- search

FIND_RE = re.compile(
    r"^([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+@[A-Za-z0-9_.-]+)\s+([\d.,]+\s*[KMB]?)\s+installs?",
    re.IGNORECASE,
)

def skills_find(query, timeout=60):
    res = run(["npx", "--yes", "skills", "find", query],
              timeout=timeout, inp="\n")
    out = (res.stdout or "") + "\n" + (res.stderr or "")
    # strip ANSI
    out = re.sub(r"\x1b\[[0-9;]*m", "", out)
    cands = []
    for line in out.splitlines():
        m = FIND_RE.match(line.strip())
        if m:
            src, count = m.group(1).strip(), m.group(2).strip()
            owner = src.split("/")[0]
            skill = src.split("@")[-1]
            cands.append({"source": src, "owner": owner,
                          "skill": skill, "installs_raw": count,
                          "installs": parse_installs(count)})
    return cands


# ---------------------------------------------------------------- fetch

def skills_add(source, skill, timeout=240):
    """جلب مهارة لمنطقة الحجر (.agents/skills). يعيد مسار المجلد أو None."""
    res = run(["npx", "--yes", "skills", "add", source,
               "-s", skill, "-y", "--copy"], timeout=timeout)
    if res.returncode != 0:
        return None, (res.stderr or res.stdout or "")[-500:]
    # حدد المجلد الجديد في .agents/skills
    if AGENTS_SKILLS.exists():
        cands = sorted(
            [d for d in AGENTS_SKILLS.iterdir() if d.is_dir()],
            key=lambda d: d.stat().st_mtime, reverse=True,
        )
        if cands:
            return cands[0], ""
    return None, "installed but dir not found"


# ---------------------------------------------------------------- adapt

def read_frontmatter(md_path):
    try:
        text = md_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return {}, ""
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, re.DOTALL)
    if not m:
        return {}, text
    fm, body = m.group(1), m.group(2)
    data = {}
    for line in fm.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            data[k.strip()] = v.strip().strip("\"'")
    return data, body


def write_frontmatter(md_path, data, body):
    lines = ["---"]
    for k, v in data.items():
        v = str(v).replace('"', "'")
        lines.append(f'{k}: "{v}"' if (":" in v or "#" in v or v != v.strip()) else f"{k}: {v}")
    lines += ["---", "", body.lstrip("\n")]
    md_path.write_text("\n".join(lines), encoding="utf-8")


def dir_size_mb(skill_dir):
    total = sum(p.stat().st_size for p in skill_dir.rglob("*") if p.is_file())
    return total / (1024 * 1024)


def adapt_skill(fetched_dir, slug, source_meta):
    """تظبيط برمجي: frontmatter + paths. يعيد (skill_md_path, rewrites[], warnings[])."""
    rewrites, warnings = [], []
    md_files = list(fetched_dir.glob("SKILL.md")) or list(fetched_dir.rglob("SKILL.md"))
    if not md_files:
        return None, rewrites, warnings
    md_path = md_files[0]
    data, body = read_frontmatter(md_path)

    # 1) frontmatter
    if data.get("name") != slug:
        rewrites.append(f"name: {data.get('name', '(missing)')} → {slug}")
        data["name"] = slug
    if not data.get("description"):
        first = next((l.strip() for l in body.splitlines() if l.strip() and not l.startswith("#")), "")
        data["description"] = (first[:200] or f"External skill {slug}, adapted locally.") \
            + f" Use when: {slug.replace('-', ' ')}."
        rewrites.append("description: synthesized from body")
    write_frontmatter(md_path, data, body)

    # 2) paths
    for md in fetched_dir.rglob("*.md"):
        try:
            t = md.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        orig = t
        for old, new in PATH_REWRITES:
            if old in t:
                t = t.replace(old, new)
        if t != orig:
            md.write_text(t, encoding="utf-8")
            rewrites.append(f"paths rewired in {md.relative_to(fetched_dir)}")

    # 3) size warn
    try:
        lines = md_path.read_text(encoding="utf-8", errors="ignore").count("\n")
        if lines > DEFAULT_CONFIG["max_skill_md_lines"]:
            warnings.append(f"SKILL.md {lines} lines (>500): consider trimming")
    except Exception:
        pass
    return md_path, rewrites, warnings


def build_adapter(fetched_dir, slug, source_meta, rewrites):
    """تغليف نظام غير معمول كمهارة داخل SKILL.md adapter."""
    orig_name = fetched_dir.name
    readme = ""
    for cand in ("README.md", "readme.md", "README", "index.md"):
        p = fetched_dir / cand
        if p.exists():
            try:
                readme = p.read_text(encoding="utf-8", errors="ignore")[:1500]
                break
            except Exception:
                pass
    summary = (readme.split("\n\n")[0][:800] if readme else
               f"External system from {source_meta['source']}, wrapped as a local adapter.")
    usage = ("1. الأصل في `.agents/skills/" + orig_name + "/`.\n"
             "2. اقرأ README الأصل قبل الاستخدام.\n"
             "3. أي مسار خارجي حوّله لمسار مشروع نسبي.\n"
             "4. سجّل أي درس جديد عبر `contribute_knowledge`.")
    body = ADAPTER_TEMPLATE.format(
        slug=slug, title=orig_name,
        description=f"Adapter for external system {orig_name} ({source_meta['installs_raw']} installs). "
                    f"Use when the task needs {orig_name.replace('-', ' ')} capability.",
        source=source_meta["source"], installs=source_meta["installs_raw"],
        date=datetime.now().strftime("%Y-%m-%d"),
        source_url=source_meta["source"].replace("@", "/"),
        owner=source_meta["owner"], trusted=source_meta["owner"] in DEFAULT_CONFIG["trusted_owners"],
        summary=summary, orig_dir=orig_name,
        rewrites="\n".join(f"- {r}" for r in rewrites) or "- (no path rewrites needed)",
        usage=usage,
    )
    out = fetched_dir / "SKILL.md"
    out.write_text(body, encoding="utf-8")
    return out


# ---------------------------------------------------------------- main flow

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--queries", nargs="*", default=None)
    ap.add_argument("--auto-adopt", action="store_true")
    ap.add_argument("--max-queries", type=int, default=5)
    ap.add_argument("--max-installs", type=int, default=3)
    ap.add_argument("--lookback-hours", type=int, default=24)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--gates", action="store_true")
    args = ap.parse_args()

    t0 = time.time()
    cfg = ensure_config()
    state = load_json(STATE_PATH, {"seen": {}, "adopted": [], "rejected": {}})
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    stage_dir = STAGING_ROOT / ts
    stage_dir.mkdir(parents=True, exist_ok=True)

    print("🔍 [discover] Internet skill discovery — stage: derive queries")
    if args.queries:
        queries = args.queries[: args.max_queries]
        sessions_read, top_terms = 0, []
    else:
        queries, sessions_read, top_terms = mine_queries(
            args.lookback_hours, args.max_queries, cfg["watch_domains"])
    print(f"   sessions mined: {sessions_read} | top terms: {[t for t, _ in top_terms[:5]]}")
    print(f"   queries: {queries}")
    if not queries:
        print("ℹ️  No queries derived and no watch domains — nothing to do.")
        return 0

    results = []
    installs_done = 0

    for q in queries:
        print(f"\n🔎 [search] {q!r}")
        try:
            cands = skills_find(q)
        except Exception as e:
            results.append({"query": q, "status": "search-error", "error": str(e)[:200]})
            continue
        print(f"   found {len(cands)} candidate(s)")
        for c in cands:
            src = c["source"]
            slug = slugify(c["skill"])
            verdict = {"query": q, **c, "slug": slug}

            # dedupe: installed already?
            if (OPENCODE_SKILLS / slug).exists() or slug in state.get("adopted", []):
                verdict.update(status="skipped", reason="already installed")
                results.append(verdict)
                continue
            # dedupe: rejected recently (7 days)?
            rej = state.get("rejected", {}).get(src)
            if rej:
                try:
                    if datetime.now() - datetime.fromisoformat(rej["at"]) < timedelta(days=7):
                        verdict.update(status="skipped", reason=f"rejected recently: {rej['reason']}")
                        results.append(verdict)
                        continue
                except Exception:
                    pass
            # qualify: installs
            if c["installs"] < cfg["suspicious_below_installs"]:
                verdict.update(status="rejected", reason=f"only {c['installs_raw']} installs (<100 suspicious)")
                state.setdefault("rejected", {})[src] = {"at": datetime.now().isoformat(), "reason": verdict["reason"]}
                results.append(verdict)
                continue
            if c["installs"] < cfg["min_installs"]:
                verdict.update(status="staged-note",
                               reason=f"{c['installs_raw']} installs (<1000): needs manual review, not auto-fetched")
                results.append(verdict)
                continue

            if args.dry_run:
                verdict.update(status="dry-run", reason="would fetch + adapt")
                results.append(verdict)
                continue
            if installs_done >= args.max_installs:
                verdict.update(status="deferred", reason="max-installs budget reached")
                results.append(verdict)
                continue

            # ---- fetch
            print(f"   ⬇️  fetching {src} ...")
            fetched, err = skills_add(src, c["skill"])
            if not fetched:
                verdict.update(status="fetch-failed", reason=err)
                results.append(verdict)
                continue
            installs_done += 1

            # ---- security scan (mandatory)
            flags, _ = scan_security(fetched)
            size_mb = dir_size_mb(fetched)
            if size_mb > cfg["max_skill_dir_mb"]:
                flags.append(f"SIZE:{size_mb:.1f}MB > {cfg['max_skill_dir_mb']}MB cap")
            if flags:
                verdict.update(status="rejected", reason="; ".join(flags[:5]))
                state.setdefault("rejected", {})[src] = {"at": datetime.now().isoformat(), "reason": verdict["reason"]}
                shutil.rmtree(fetched, ignore_errors=True)
                print(f"   ⛔ rejected: {verdict['reason']}")
                results.append(verdict)
                continue

            # ---- adapt programmatically
            md_path, rewrites, warnings = adapt_skill(fetched, slug, c)
            adapter_built = False
            if md_path is None:
                md_path = build_adapter(fetched, slug, c, rewrites)
                adapter_built = True
                rewrites.append("adapter SKILL.md generated (no native SKILL.md upstream)")

            trusted = c["owner"] in cfg["trusted_owners"]
            verdict.update(rewrites=rewrites, warnings=warnings,
                           trusted_owner=trusted, adapter_built=adapter_built)

            # ---- adopt or stage
            if args.auto_adopt and trusted:
                dest = OPENCODE_SKILLS / slug
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.copytree(fetched, dest, symlinks=False)
                reg = run([str(VENV_PY), "scripts/router_register.py", slug], timeout=90)
                verdict.update(status="adopted",
                               reason=f"trusted owner + clean scan; router: {(reg.stdout or '')[-200:]}")
                if slug not in state.get("adopted", []):
                    state.setdefault("adopted", []).append(slug)
                if args.gates:
                    g = run([str(VENV_PY), "scripts/build_gates_pipeline.py",
                             str(dest / "SKILL.md"), "--no-hitl"], timeout=600)
                    verdict["gates_exit"] = g.returncode
                print(f"   ✅ adopted → .opencode/skills/{slug}/")
            else:
                sdir = stage_dir / slug
                if sdir.exists():
                    shutil.rmtree(sdir)
                shutil.copytree(fetched, sdir, symlinks=False)
                verdict.update(
                    status="staged",
                    reason=("clean scan; staged for review "
                            + ("(untrusted owner — manual adopt required)" if not trusted
                               else "(auto-adopt off — run with --auto-adopt)")),
                    stage_path=str(sdir.relative_to(ROOT)),
                )
                print(f"   📦 staged → {verdict['stage_path']}")
            results.append(verdict)

    save_json(STATE_PATH, state)

    # ---- report
    elapsed = (time.time() - t0) / 60
    counts = Counter(r.get("status", "?") for r in results)
    report = {
        "at": datetime.now().isoformat(), "elapsed_min": round(elapsed, 1),
        "queries": queries, "sessions_mined": sessions_read,
        "counts": dict(counts), "results": results,
    }
    save_json(stage_dir / "report.json", report)
    lines = [f"# Discovery report — {ts} ({elapsed:.1f} min)",
             f"queries: {', '.join(queries)}",
             f"sessions mined: {sessions_read}", "",
             "## Counts"]
    lines += [f"- {k}: {v}" for k, v in sorted(counts.items())]
    lines.append("\n## Results")
    for r in results:
        lines.append(f"- **{r.get('source', r.get('query'))}** → `{r.get('status')}` — {r.get('reason', '')}")
    (stage_dir / "report.md").write_text("\n".join(lines), encoding="utf-8")

    print(f"\n{'='*60}\n✅ done in {elapsed:.1f} min | " +
          " ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    print(f"📄 report: {stage_dir.relative_to(ROOT)}/report.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
