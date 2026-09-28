"""Advanced testing: property, metamorphic, differential, mutation aides.

Four techniques the example-based suite cannot replace, stdlib-only:
  - property_check(): run a generator N times; every output must hold
    every invariant (shrinks to the first failing input for the log).
  - metamorphic(): transform inputs, assert the expected output
    relation (ideal for AI/non-deterministic targets).
  - differential(): run rival implementations on shared inputs,
    report agreements/disagreements with diffs.
  - mutation_score(): flip seeded mutants (operator callables over a
    target fn); the suite passes only when it kills each mutant
    (detects a behavior change) — survivors name test gaps.
  - negative_cases(): boundary/empty/oversize/malformed battery for
    string-ish inputs (feeds any runner).

No external fuzzing library required; plug Hypothesis later without
changing call shapes (generators are plain callables).
"""

from __future__ import annotations

import random
import string


def property_check(generator, invariants: list, *, trials: int = 200,
                   seed: int = 7) -> dict:
    """Random inputs must all hold all invariants. First failure kept."""
    rng = random.Random(seed)
    for n in range(int(trials)):
        value = generator(rng)
        for inv in invariants:
            try:
                ok, note = inv(value)
            except Exception as exc:  # noqa: BLE001 - invariant bug = fail
                return {"holds": False, "trial": n, "input": value,
                        "note": f"invariant crashed: {exc}"}
            if not ok:
                return {"holds": False, "trial": n, "input": value,
                        "note": str(note)}
    return {"holds": True, "trials": int(trials)}


def metamorphic(base_inputs: list, transform, relation) -> dict:
    """Related inputs must yield related outputs (relation decides)."""
    violations = []
    for inp in base_inputs:
        try:
            out_a, out_b = relation(inp, transform(inp))
            ok = bool(out_a) if not isinstance(out_a, tuple) else bool(
                out_a[0])
            note = "" if ok else str(out_a[1] if isinstance(
                out_a, tuple) else "relation broken")
        except Exception as exc:  # noqa: BLE001 - record
            ok, note = False, f"crashed: {exc}"
        if not ok:
            violations.append({"input": inp, "note": note})
    return {"holds": not violations, "violations": violations,
            "checked": len(base_inputs)}


def differential(inputs: list, implementations: dict) -> dict:
    """Agreement matrix across rival implementations per input."""
    names = list(implementations)
    rows = []
    for inp in inputs:
        outs = {}
        for name in names:
            try:
                outs[name] = ("ok", implementations[name](inp))
            except Exception as exc:  # noqa: BLE001 - record
                outs[name] = ("raised", str(exc))
        vals = {json_safe(v) for _, v in outs.values()}
        rows.append({"input": inp, "agree": len(vals) == 1,
                     "outputs": {k: v for k, (_, v) in outs.items()}})
    disagreements = [r for r in rows if not r["agree"]]
    return {"inputs": len(rows), "disagreements": disagreements,
            "agree_all": not disagreements}


def json_safe(value):
    """Hashable projection for agreement comparison."""
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return repr(value)


def mutation_score(target_fn, mutants: list, suite_fn) -> dict:
    """Kill rate of seeded mutants. Survivors = test gaps.

    mutants: [(name, mutate_fn)] where mutate_fn wraps target_fn into a
    broken variant. suite_fn(variant) -> True when the suite PASSES on
    it (mutant survives) — we want suite_fn False (killed) for each.
    """
    killed, survived = [], []
    for name, mutate in mutants:
        try:
            variant = mutate(target_fn)
            passed = bool(suite_fn(variant))
        except Exception:  # noqa: BLE001 - suite crash kills the mutant
            passed = False
        (survived if passed else killed).append(name)
    total = len(mutants)
    return {"killed": killed, "survived": survived,
            "score": (len(killed) / total) if total else 1.0}


def negative_cases(seed_text: str = "ok") -> list[str]:
    """Boundary battery: empty, whitespace, oversize, malformed, unicode."""
    big = "x" * 100000
    return ["", "   ", "\n\t", seed_text, big, seed_text * 2000,
            "\x00null-byte", "'; DROP TABLE t; --",
            "{{unclosed", "[[[mixed}}}",
            "emoji-\U0001F600-break", "a" * 2, "\ufffd-replacement"]
