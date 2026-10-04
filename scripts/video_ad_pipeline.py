"""Video Ad Pipeline: brief (scenes JSON) -> gated READY_FOR_PRODUCTION.

Mirrors scripts/build_gates_pipeline.py philosophy for video ads:
weak generative models + strong scaffolding beats a strong model alone.
Stages: BRIEF -> PSYCHOLOGY -> SCRIPT -> RENDER-READINESS.
Exit 0 = READY_FOR_PRODUCTION only. No secrets, no network, no exec.

Usage:
  venv/bin/python scripts/video_ad_pipeline.py <scenes.json> [--no-psych] [--json]
  scenes = [{image, voice}, ...] (+ optional _gates.psychology object)
"""
import argparse
import json
import re
import sys

HOOK_WORDS = ['بيرن', 'محدش', 'فلوس', 'خسارة', 'فاضي', 'بتضيع', '؟', '?',
              'عارف', 'بص', 'ستين الف', '60000']
CTA_WORDS = ['ديمو', 'واتساب', 'واتس اب', 'احجز', 'ابعت', 'يلا']
FAKE_STAT_RE = re.compile(r'\d+\s*%|\d+\s*الف|زيادة \d+')
HEDGE_WORDS = ['ممكن', 'شبه', 'مثل', 'زودت', 'عيادات شبه']


def load_scenes(path):
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    if isinstance(data, dict) and 'scenes' in data:
        gates = data.get('_gates', {})
        return data['scenes'], gates
    return data, {}


def estimate_duration_sec(voice):
    words = len(voice.split())
    return max(2.0, words / 2.2)


def run(scenes, gates, require_psych=True):
    stages = []
    violations = []
    warnings = []

    # Stage 1 BRIEF
    if not isinstance(scenes, list) or not (3 <= len(scenes) <= 6):
        violations.append('BRIEF: scenes must be a list of 3-6 items')
        stages.append(('BRIEF', 'FAIL'))
    else:
        bad = [i for i, s in enumerate(scenes)
               if not s.get('image') or not s.get('voice')]
        if bad:
            violations.append('BRIEF: scenes %s missing image/voice' % bad)
            stages.append(('BRIEF', 'FAIL'))
        else:
            stages.append(('BRIEF', 'PASS'))

    # Stage 2 PSYCHOLOGY
    psych = (gates or {}).get('psychology', {})
    if require_psych:
        missing = [k for k in ('profile', 'levers', 'edit_spec')
                   if k not in psych]
        if missing:
            violations.append('PSYCHOLOGY: missing %s (audience-psychology-analyst)' % missing)
            stages.append(('PSYCHOLOGY', 'FAIL'))
        else:
            stages.append(('PSYCHOLOGY', 'PASS'))
    else:
        stages.append(('PSYCHOLOGY', 'SKIP'))

    # Stage 3 SCRIPT
    if isinstance(scenes, list) and scenes:
        first_voice = str(scenes[0].get('voice', ''))
        if not any(w in first_voice for w in HOOK_WORDS):
            violations.append('SCRIPT: scene-1 has no hook (pain/?/بص/عارف) in first 3s')
        long_scenes = [i for i, s in enumerate(scenes)
                       if len(str(s.get('voice', '')).split()) > 45]
        if long_scenes:
            violations.append('SCRIPT: scenes %s exceed 45 words (cognitive load)' % long_scenes)
        last_voice = str(scenes[-1].get('voice', ''))
        if not any(w in last_voice for w in CTA_WORDS):
            violations.append('SCRIPT: last scene has no CTA (ديمو/واتساب/احجز)')
        for i, s in enumerate(scenes):
            v = str(s.get('voice', ''))
            if FAKE_STAT_RE.search(v) and not any(h in v for h in HEDGE_WORDS):
                warnings.append('SCRIPT: scene %d has a bare stat, hedge or cite it' % i)
        stages.append(('SCRIPT', 'FAIL' if any(v.startswith('SCRIPT') for v in violations) else 'PASS'))

    # Stage 4 RENDER-READINESS
    total = sum(estimate_duration_sec(str(s.get('voice', ''))) for s in scenes) if isinstance(scenes, list) else 0
    total += 0.4 * (len(scenes) if isinstance(scenes, list) else 0)
    if not (15 <= total <= 95):
        violations.append('RENDER: estimated duration %.1fs outside 15-95s window' % total)
        stages.append(('RENDER', 'FAIL'))
    else:
        stages.append(('RENDER', 'PASS'))

    ok = not violations
    return {
        'verdict': 'READY_FOR_PRODUCTION' if ok else 'NEEDS_WORK',
        'stages': stages,
        'violations': violations,
        'warnings': warnings,
        'estimated_sec': round(total, 1),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('artifact')
    ap.add_argument('--no-psych', action='store_true')
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args()
    try:
        scenes, gates = load_scenes(a.artifact)
    except Exception as e:
        print('LOAD_FAIL: %s' % e)
        return 2
    res = run(scenes, gates, require_psych=not a.no_psych)
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        for name, status in res['stages']:
            print('[%s] %s' % (name, status))
        for v in res['violations']:
            print('  X %s' % v)
        for w in res['warnings']:
            print('  ! %s' % w)
        print('estimated: %ss' % res['estimated_sec'])
        print('VERDICT %s' % res['verdict'])
    return 0 if res['verdict'] == 'READY_FOR_PRODUCTION' else 1


if __name__ == '__main__':
    sys.exit(main())
