---
name: snapshot-testing-patterns
description: "Snapshot testing patterns distilled. Use when testing rendered output, component snapshots, serializers,configs, snapshot review discipline."
---

# Snapshot Testing Patterns

## Purpose

Use snapshots where output shape matters and logic tests would be verbose: render once, review deliberately, diff on change.

## When to use

Use when the user says 'snapshot test', 'component snapshot', 'serializer snapshot', 'Jest snapshot', 'snapshot review'.

## Steps

1. Snapshot stable, deterministic output only (normalize dates, ids, randomness).
2. Keep snapshots small and focused per component or unit.
3. Review every new or changed snapshot as production code.
4. Delete obsolete snapshots with the code they covered.
5. Prefer explicit assertions for behavior; snapshots for shape.

## Anti-patterns

- Blind `--update-snapshot` to make CI green.
- Giant snapshots hiding the real change in noise.
- Snapshotting volatile data (timestamps, random ids).
- Snapshot as the only test for critical behavior.

## Example

JS:

```js
expect(renderBadge({ level: 'gold' })).toMatchSnapshot();
```

Python (`syrupy`): same shape-approval idea for serializers.

## Verification

Snapshots deterministic, reviewed per change, obsolete ones removed, behavior assertions alongside.

## Pairs-with

visual-regression-deep, test-smells-catalog, xunit-test-patterns, frontend-perf-testing.
