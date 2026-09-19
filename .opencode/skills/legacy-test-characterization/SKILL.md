---
name: legacy-test-characterization
description: "Legacy characterization testing distilled. Use when pinning undocumented behavior, golden master, seam identification, safe test retrofitting."
---

# Legacy Characterization Testing

## Purpose

Retrofit tests onto undocumented code: find seams, pin behavior with characterization tests and golden masters, then change safely.

## When to use

Use when the user says 'legacy code', 'characterization test', 'golden master', 'seam', 'untested code', 'Feathers'.

## Steps

1. Find seams: points where behavior can be observed without rewriting.
2. Write characterization tests capturing what the code DOES, not what it should do.
3. For complex outputs, record a golden master and diff against it.
4. Break dependencies with sprout or wrap methods for new behavior.
5. Refactor outward from tested seams only.

## Anti-patterns

- Writing aspirational tests that fail on legacy reality.
- Golden masters blessed without reviewing the captured output.
- Refactoring untested regions on confidence alone.
- New features copy-pasted into the legacy mass without seams.

## Example

Python golden master:

```python
def test_report_matches_master():
    assert render_report(SAMPLE) == open("master.txt").read()
```

## Verification

Seams mapped, characterization suite green on untouched code, masters reviewed, new code enters through seams.

## Pairs-with

legacy-code-characterization, refactoring-test-safety, test-smells-catalog, xunit-test-patterns.
