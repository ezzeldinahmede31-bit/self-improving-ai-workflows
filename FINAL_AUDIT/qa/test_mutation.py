"""F12 mutation testing: prove the suite catches injected defects.
Introduces 5 mutants into TEMP copies, runs relevant suites, expects FAILs.
Run: venv/bin/python FINAL_AUDIT/qa/test_mutation.py
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

QA = Path("FINAL_AUDIT/qa")
MUT = QA / "mutants"
SH = sys.executable


def sh(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=300)


MUTANTS = [
    ("M1-agenda-offbyone",
     "clinic_staff_console", "Format Agenda Reply",
     "parts.length - 3", "parts.length - 2",  # reintroduce index bug
     "test_functional.py", "F2-006-arabic-names"),
    ("M2-ownership-always-true",
     "clinic_sub_cal_cancel", "Verify Owner",
     "const ok = okChat || okPhone;", "const ok = true;",
     "test_comp_authz.py", "F5-patient-other-cancel"),
    ("M3-idempotency-removed",
     "clinic_sub_cal_book", "Parse Idempotent",
     "repeat: !!rec", "repeat: false",
     "test_functional.py", "F2-dup-repeat"),
    ("M4-demo-price-leak",
     "clinic_sub_knowledge_base", "Lookup Clinic Catalog",
     "_fallback: true", "_fallback: false",
     "test_functional.py", "F2-013-no-fallback-fabrication"),
    ("M5-confirm-always-true",
     "clinic_sub_cal_book", "Confirm Verified?",
     "ok: eid !== ''", "ok: true",
     "test_functional.py", "F2-015-no-false-confirm"),
]

print("mutant | suite-result(expect FAIL) | caught?")
caught = 0
for mid, wf, node, old, new, suite, witness in MUTANTS:
    d = json.load(open(f"FINAL_AUDIT/qa/isolated/{wf}.json"))
    hit = False
    for n in d["nodes"]:
        if n.get("name") == node and old in n["parameters"]["jsCode"]:
            n["parameters"]["jsCode"] = n["parameters"]["jsCode"].replace(
                old, new, 1)
            hit = True
    assert hit, f"pattern not found for {mid}"
    # run suite with isolated dir temporarily swapped
    bak = QA / "isolated-bak"
    if bak.exists():
        shutil.rmtree(bak)
    shutil.copytree(QA / "isolated", bak)
    json.dump(d, open(f"FINAL_AUDIT/qa/isolated/{wf}.json", "w"))
    r = sh([SH, f"FINAL_AUDIT/qa/{suite}"])
    fail_seen = ("FAIL " in r.stdout) or (witness not in r.stdout)
    # more precise: witness test must FAIL
    witness_fail = f"FAIL {witness}" in r.stdout
    shutil.rmtree(QA / "isolated")
    shutil.move(str(bak), str(QA / "isolated"))
    print(f"{mid}: witness-fail={witness_fail} "
          f"{'CAUGHT' if witness_fail else 'ESCAPED!'}")
    caught += witness_fail

print(f"\nMUTATION: {caught}/{len(MUTANTS)} caught")
raise SystemExit(0 if caught == len(MUTANTS) else 1)
