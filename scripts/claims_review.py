"""Automatic claims review before publishing any sales copy.

Every psychological mechanism must pass three separate levels:
  Mechanism -> Evidence Strength -> Exact Source.
The LLM is FORBIDDEN from upgrading "inspired by" to "proven by".

Usage:
  claims_review.py --text script.txt        # exit 0 PASS, 1 WARN-only, 2 FAIL
Checks (Arabic copy):
  FAIL: absolute guarantees without hedging (مبيرجعش, دايما, مستحيل, مضمون,
        لفترة محدودة as fake urgency, اشتري/اطلب as push CTA, fixed ratios).
  FAIL: fabricated social proof templates (فهمت اللعبة, بطلت تعتمد, عملاءنا
        without names, بدأت تستخدم without cases).
  WARN: frequency claims (كل شهر/يوم/مرة) without hedging (ممكن/أغلب/قد),
        percentages without a source.
"""
import argparse
import re
import sys

FAIL_ABSOLUTES = ['مبيرجعش', 'مبيرجعوش', 'دايما', 'دائما', 'مستحيل', 'مضمون',
                  'اشتري', 'اطلب دلوقتي', 'لفترة محدودة', 'خصم حصري']
FAIL_RATIO = [r'ضعف المكسب', r'2x', r'مرتين أكثر', r'٪\s*\d|\d+\s*٪']
FAIL_PROOF = ['فهمت اللعبة', 'بطلت تعتمد', 'عملاءنا', 'بدأت تستخدم',
              'كل العيادات بتستخدم', 'اثبتت الدراسات']
WARN_FREQ = ['كل شهر', 'كل يوم', 'كل مرة', 'كل أسبوع']
HEDGE = ['ممكن', 'أغلب', 'قد ', 'يمكن', 'غالبا', 'مثال', 'تخيل']


def check(text):
    fails, warns = [], []

    def near_hedge(pos, window=60):
        ctx = text[max(0, pos - window):pos + window]
        return any(h in ctx for h in HEDGE)

    for pat in FAIL_ABSOLUTES:
        for m in re.finditer(re.escape(pat), text):
            fails.append(('absolute/push-CTA', pat, m.start()))
    for pat in FAIL_RATIO:
        for m in re.finditer(pat, text):
            fails.append(('fixed-ratio-or-percent-without-source', m.group(0), m.start()))
    for pat in FAIL_PROOF:
        for m in re.finditer(re.escape(pat), text):
            fails.append(('fabricated-proof', pat, m.start()))
    for pat in WARN_FREQ:
        for m in re.finditer(re.escape(pat), text):
            if not near_hedge(m.start()):
                warns.append(('unhedged-frequency', pat, m.start()))
    return fails, warns


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--text', required=True)
    ap.add_argument('--gate', action='store_true',
                    help='also print the Mechanism->Strength->Source reminder')
    a = ap.parse_args()
    text = open(a.text, encoding='utf-8').read()
    fails, warns = check(text)
    for kind, pat, pos in fails:
        print('FAIL [%s] %r at char %d' % (kind, pat, pos))
    for kind, pat, pos in warns:
        print('WARN [%s] %r at char %d' % (kind, pat, pos))
    if a.gate:
        print('GATE: Mechanism -> Evidence Strength -> Exact Source; '
              '"inspired by" must never ship as "proven by".')
    if fails:
        print('VERDICT: FAIL')
        return 2
    if warns:
        print('VERDICT: WARN')
        return 1
    print('VERDICT: PASS')
    return 0


if __name__ == '__main__':
    sys.exit(main())
