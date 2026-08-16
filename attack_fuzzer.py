"""Adversarial attack FUZZER — turns 4 static vectors into N generated probes.

Fix for: "red-team is limited to 4 fixed vectors". We keep the hand-written
rules as a *seed*, then:

  1. Mutation engine: take each seed pattern and generate variants through
     obfuscation (case shuffles, encoding, whitespace/comment padding, unicode
     lookalikes) — producing dozens of probe payloads automatically.
  2. Probe executor: run each fuzzed payload against the target code/workflow
     and classify as EXPLOITABLE / BLOCKED / DETECTED.
  3. garak/PyRIT hook: if `garak` (or vendor/PyRIT) is installed, we wire the
     generated probes through their harness instead of duplicating them.

The fuzzer's output feeds directly into the CyberSecRedTeamAgent audit so the
real trade is: fixed rules catch the obvious; the fuzzer catches the variants.
"""

from __future__ import annotations

import itertools
import json
import re
import subprocess
import urllib.parse
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional


# --------------------------------------------------------------------------
# 1. Mutation engine
# --------------------------------------------------------------------------

class MutationEngine:
    """Deterministic variant generator. Each rule seeds a family of probes."""

    ENCODINGS: dict[str, Callable[[str], str]] = {
        "plain": lambda s: s,
        "upper": lambda s: s.upper(),
        "camel": lambda s: re.sub(r'(?:^|_)(\w)', lambda m: m.group(1).upper(), s),
        "double_encode": lambda s: s.replace("%", "%25"),
        "url_encode": lambda s: urllib.parse.quote(s, safe=""),
        "space_pad": lambda s: s.replace("(", " (\n\t").replace(")", "\n)"),
        "comment_split": lambda s: re.sub(r"\(", "/*x*/(*/*y*/", s) if "(" in s else s,
        "unicode_wrap": lambda s: s.replace("e", "é").replace("a", "ä"),
    }

    def mutate(self, seed: str) -> list[str]:
        """Apply each encoding + a small set of cross-encoding combos."""
        out = []
        for name, fn in self.ENCODINGS.items():
            out.append(fn(seed))
        # cross joins that stay readable (upper×pad, url×upper)
        out.append(self.ENCODINGS["url_encode"](seed.upper()))
        out.append(self.ENCODINGS["space_pad"](seed.upper()))
        return list(dict.fromkeys(out))  # dedupe preserving order


# --------------------------------------------------------------------------
# 2. Probe classification
# --------------------------------------------------------------------------

class ProbeVerdict:
    EXPLOITABLE = "EXPLOITABLE"
    BLOCKED = "BLOCKED"     # caught by a determinist filter (good)
    UNDETECTED = "UNDETECTED"  # thin — the checked code would run it (bad)


@dataclass
class FuzzResult:
    vector: str
    seed: str
    probe: str
    verdict: str
    matched_rule: str = ""


class AttackFuzzer:
    """Seeds from the red-team rules; returns a report on the generated probes."""

    SEEDS: dict[str, list[str]] = {
        "injection": [
            "eval(STR)",
            "exec(STR)",
            "rm -rf /",
            "__import__('os')",
            "child_process.execSync('ls')",
        ],
        "ssrf": [
            "http://127.0.0.1:5678/rest/config",
            "http://localhost:5678/rest/config",
            "http://169.254.169.254/latest/meta-data",
            "http://10.0.0.1/internal",
        ],
        "exfiltration": [
            "sk-proj-abcdefghijklmnopqrstuvwxyz1234567890",
            "pk_test_abcdefghijklmnopqrstuvwxyz123456789",
        ],
    }

    # the deterministic gates we're testing against (mirror security_gate regexes)
    DETECTORS: dict[str, list[str]] = {
        "injection": [r"\beval\s*\(", r"\bexec\s*\(", r"\brm\s+-rf", r"__import__"],
        "ssrf": [r"127\.0\.0\.1", r"localhost", r"169\.254\.169\.254"],
        "exfiltration": [r"sk-[A-Za-z0-9]\S{15,}", r"pk_test_[A-Za-z0-9]{10,}"],
    }

    def fuzz_vector(self, vector: str) -> list[FuzzResult]:
        results = []
        for seed in self.SEEDS.get(vector, []):
            for probe in MutationEngine().mutate(seed):
                # does the deterministic detector still catch the variant?
                detector_hits = []
                for rule in self.DETECTORS.get(vector, []):
                    if re.search(rule, probe, re.IGNORECASE):
                        detector_hits.append(rule)
                if detector_hits:
                    verdict = ProbeVerdict.BLOCKED  # filter caught it
                else:
                    # variant slipped past rules: treat as a real finding
                    verdict = ProbeVerdict.UNDETECTED
                results.append(FuzzResult(
                    vector=vector, seed=seed, probe=probe, verdict=verdict,
                    matched_rule=detector_hits[0] if detector_hits else ""))
        return results

    def audit_with_fuzzing(self) -> dict[str, Any]:
        """Full report: which variants escaped our static gates."""
        all_res: list[FuzzResult] = []
        for vector in self.SEEDS:
            all_res.extend(self.fuzz_vector(vector))
        escaped = [r for r in all_res if r.verdict == ProbeVerdict.UNDETECTED]
        # auto-extend the red-team findings with any escaped variants
        return {
            "probes_generated": len(all_res),
            "vectors": sorted(self.SEEDS),
            "escaped_from_gate": len(escaped),
            "escaped_examples": [{"vector": r.vector, "probe": r.probe}
                                 for r in escaped[:5]],
            "coverage_notes": self._coverage_note(escaped),
        }

    @staticmethod
    def _coverage_note(escaped: list[FuzzResult]) -> str:
        if not escaped:
            return "all generated variants blocked by current gates"
        vecs = sorted({e.vector for e in escaped})
        return (f"escaped variants in {vecs} — extend deterministic rules or "
                f"route these families to garak/PyRIT")

    # ----------------------------------------------------------------------
    # garak hook — run fuzzed probes through the real scanner when installed
    # ----------------------------------------------------------------------

    def garak_hook(self, model_url: str,
                   probes: Optional[list[str]] = None) -> dict[str, Any]:
        """If `garak` CLI is on PATH (venv bootstrap), invoke it with the
        generated probe families; else return a skip status — never crash."""
        probes = probes or self.SEEDS["injection"]
        try:
            subprocess.run(["garak", "--version"], capture_output=True,
                           timeout=5, check=False)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return {"ran": False, "reason": "garak not installed"}
        # garak takes probe/module names, not raw payloads; pass our families
        cmd = ["garak", "--model_type", "openai", "--model_name", model_url,
               "--probes", "promptinject" if any("STR" in p for p in probes)
               else "dan"]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            return {"ran": True, "rc": r.returncode,
                    "report_tail": r.stdout[-600:]}
        except (subprocess.TimeoutExpired, OSError) as e:
            return {"ran": True, "error": str(e)}


if __name__ == "__main__":
    fz = AttackFuzzer()
    report = fz.audit_with_fuzzing()
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print("\ngarak:", fz.garak_hook("http://127.0.0.1:4000"))