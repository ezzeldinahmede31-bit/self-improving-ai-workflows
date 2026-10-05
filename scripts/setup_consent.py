#!/usr/bin/env python3
"""
setup_consent.py — بوابة الموافقة وقت التنزيل (install-time consent).

المبدأ: لا شيء يغادر جهازك دون موافقة صريحة منك، تُسجل مرة واحدة
وقت الإعداد، ويمكنك تغييرها في أي وقت بإعادة تشغيل هذا السكريبت.

- توافق → تُفعَّل المشاركة (metadata فقط + موافقة صريحة على كل إرسال)
  مقابل استقبال تطويرات الشبكة.
- ترفض → استخدام كامل محليًا، صفر إرسال، عادي جدًا — لا أحد يجبرك.

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
    """True = مسموح بالإرسال. missing/False + interactive → يسأل ويسجل.

    interactive=False (مثل git hook في الخلفية): الافتراضي الآمن = لا إرسال.
    """
    data = load_consent()
    if "contribute" in data:
        return bool(data["contribute"])
    if not interactive:
        return False
    print("\n" + "=" * 60)
    print("📥 أول استخدام لأدوات المشاركة — نحتاج موافقتك (مرة واحدة):")
    print("  - ما يُرسل: metadata فقط (أسماء مهارات + أرقام) + موافقة صريحة")
    print("    على كل إرسال قبل حدوثه — لا إرسال صامت أبدًا.")
    print("  - المقابل: تستقبل تطويرات الشبكة (قبول/رفض بيدك دائمًا).")
    print("  - الرفض عادي: استخدام محلي كامل، صفر إرسال.")
    print("=" * 60)
    try:
        ans = input("توافق على المشاركة؟ [y نعم / n لا] ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("\n⏸️  لم تُسجل موافقة — لن يُرسل شيء.")
        return False
    ok = ans in ("y", "yes", "نعم", "اه", "ok")
    save_consent(ok)
    print("✅ سُجلت موافقتك — شكرًا لمشاركتك." if ok
          else "✅ سُجل رفضك — استخدام محلي فقط، ولن نطلب مجددًا هنا.")
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
    print("🛠️  إعداد Skill Evolution System — الموافقة أولًا")
    print("=" * 60)

    if args.accept:
        save_consent(True)
        print("✅ تم تسجيل الموافقة (--accept).")
    elif args.decline:
        save_consent(False)
        print("✅ تم تسجيل الرفض (--decline) — استخدام محلي فقط.")
        return 0
    else:
        cur = load_consent().get("contribute")
        if cur is True:
            print("ℹ️  حالتك الحالية: **موافق** على المشاركة.")
        elif cur is False:
            print("ℹ️  حالتك الحالية: **رافض** (محلي فقط).")
        else:
            print("ℹ️  لم تسجل موافقتك بعد.")
        print()
        print("المقايضة بصراحة:")
        print("  توافق → تطويراتك (metadata + بموافقتك كل مرة) تقوي الشبكة،")
        print("            وتستقبل تطويرات الكل (تقبل/ترفض بيدك).")
        print("  ترفض  → كل شيء محلي، لا يخرج من جهازك بت واحد. عادي تمامًا.")
        ans = ask("\nتوافق على المشاركة؟ [y نعم / n لا] (default: n): ", "n")
        ok = ans.lower() in ("y", "yes", "نعم", "اه", "ok")
        save_consent(ok)
        print("✅ سُجلت موافقتك." if ok else "✅ سُجل رفضك — محلي فقط.")

    if not load_consent().get("contribute"):
        print("\n⏭️  تخطي إعداد الشبكة (وضع محلي).")
        print("   لتغيير رأيك لاحقًا: venv/bin/python scripts/setup_consent.py")
        return 0

    # إعداد الشبكة للمشاركين فقط
    print("\n--- إعداد الشبكة (للمشاركين) ---")
    repo = ask("مستودع المركزي OWNER/REPO (فارغ = لاحقًا): ")
    if repo and "/" in repo:
        UPSTREAM_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(UPSTREAM_PATH, "w", encoding="utf-8") as f:
            json.dump({"repo": repo.strip()}, f, ensure_ascii=False, indent=2)
        print(f"✅ حُفظ: {UPSTREAM_PATH.relative_to(ROOT)}")
    else:
        print("⏭️  تخطي — البلاغات ستُحفظ في outbox محلي حتى الربط.")
    if not os.environ.get("GITHUB_TOKEN"):
        print("💡 للكتابة على GitHub لاحقًا: export GITHUB_TOKEN=ghp_... (لا يُخزن في ملفات)")

    hook = ask("تركيب git hook للمزامنة التلقائية؟ [y/n] (default: y): ", "y")
    if hook.lower() in ("y", "yes", "نعم", "اه", "ok", ""):
        r = subprocess.run(["bash", "scripts/install_hook.sh"], cwd=str(ROOT))
        if r.returncode != 0:
            print("⚠️  تعذر تركيب الـ hook — يمكنك لاحقًا: make install-hook")
    else:
        print("⏭️  تخطي الـ hook — استخدم make sync يدويًا عند الرغبة.")
    print("\n🎉 انتهى الإعداد. ابدأ بـ: make dev-cycle")
    return 0


if __name__ == "__main__":
    sys.exit(main())
