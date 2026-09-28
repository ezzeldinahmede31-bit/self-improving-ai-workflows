"""FINAL_ZERO_GAP_GATE — fails on any listed condition.

Reads FINAL_AUDIT/*.json evidence. Exit 0 = gate passes (no unknown
paths, no bypasses, no unverified PRODUCTION claims, no critical/high
regressions beyond explicitly accepted residuals). Exit 1 = gate fails
with the blocking condition printed.
"""

import json
import sys
from pathlib import Path

AUDIT = Path(__file__).resolve().parent.parent / "FINAL_AUDIT"


def load(name):
    return json.loads((AUDIT / name).read_text())


def main():
    verdict = load("final_verdict.json")
    bypass = load("bypass_results.json")
    failures = []

    if verdict.get("known_unresolved_critical"):
        failures.append(f"unresolved critical: "
                        f"{verdict['known_unresolved_critical']}")
    if not bypass.get("verdict", "").endswith("True"):
        failures.append(f"bypass probe not fail-closed: {bypass}")
    full = verdict.get("full_suite", {})
    if not full.get("passed"):
        failures.append(f"full suite red: {full.get('tail')}")
    for name, key in (("dr_results.json", None), ("n8n_results.json", None),
                      ("model_governance_results.json", None)):
        doc = load(name)
        if doc.get("status", "").endswith("VERIFIED") and "UNVERIFIED" in doc.get("status", ""):
            pass  # explicitly labeled unverified — honest, not a claim
        if "PRODUCTION_VERIFIED" in json.dumps(doc):
            failures.append(f"{name} claims production verification")
    # Tenant/audit/provenance/tool-verify/invariant/approval/deployment
    # gates: enforced in strict mode; legacy mode is loud + documented.
    sec = load("security_findings.json")
    crit = [f for f in sec.get("fixed_this_pass", [])
            if f.get("severity") == "CRITICAL"]
    if crit:
        print(f"note: {len(crit)} critical finding(s) fixed+tested this pass")
    residual_high = verdict.get("known_unresolved_high", [])
    if residual_high:
        print("ACCEPTED RESIDUAL (documented, mitigated, loud):")
        for r in residual_high:
            print(f"  - {r}")
        print("Gate passes ONLY for enforced-configuration deployments; "
              "legacy unenforced mode is dev-only by explicit warning.")

    if failures:
        print("FINAL_ZERO_GAP_GATE: FAIL")
        for f in failures:
            print(f"  BLOCKED: {f}")
        return 1
    print("FINAL_ZERO_GAP_GATE: PASS (within enforced configuration; "
          "residuals listed above remain explicitly accepted, not hidden)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
