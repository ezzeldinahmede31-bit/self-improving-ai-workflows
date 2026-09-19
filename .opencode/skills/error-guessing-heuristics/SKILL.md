---
name: error-guessing-heuristics
description: "Error guessing and experience-based testing distilled. Use when hunting likely defects from experience, past bugs, heuristics, checklists."
---

# Error Guessing Heuristics

## Purpose

Aim experience at likely failure points: past-bug patterns, platform quirks, and classic weak spots, as a complement to systematic techniques.

## When to use

Use when the user says 'error guessing', 'experience-based testing', 'bug heuristics', 'likely defects', 'past bugs'.

## Steps

1. Mine history: recent defects, hotspots, support tickets.
2. Apply classic heuristics: nulls, empties, encoding, timezones, concurrency, offline, permissions.
3. Timebox a focused attack session per heuristic family.
4. Log hits with evidence; convert repeats into permanent checks.
5. Retire heuristics that stop finding anything; add new ones from fresh bugs.

## Anti-patterns

- Error guessing as the only technique with no systematic base.
- Repeating the same pet attacks while ignoring history data.
- No log, so the same guess never compounds into knowledge.
- Blaming the technique when the real gap is missing technique mix.

## Example

Python heuristic sweep:

```python
@pytest.mark.parametrize("payload", ["", None, "é", "0", "-1", "9" * 5000])
def test_name_field_survives(payload):
    r = create_user({"name": payload})
    assert r.status_code in (200, 400)
```

## Verification

Heuristic list tied to history, sessions logged, repeats converted to checks, hit rate reviewed.

## Pairs-with

bach-session-exploratory, hendrickson-explore-it, kaner-lessons-testing, black-risk-based-testing.
