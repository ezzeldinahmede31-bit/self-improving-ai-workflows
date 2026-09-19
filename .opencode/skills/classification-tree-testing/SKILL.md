---
name: classification-tree-testing
description: "Classification tree testing distilled. Use when structuring test domains into trees, classes, combinations, systematic case design."
---

# Classification Tree Testing

## Purpose

Decompose a messy input domain into a tree of classifications and classes, then derive systematic combinations from it.

## When to use

Use when the user says 'classification tree', 'CTE', 'test domain model', 'input classes', 'systematic combinations'.

## Steps

1. Identify classifications (dimensions) of the domain under test.
2. Split each into disjoint classes (values that behave alike).
3. Draw the tree; check classes are disjoint and complete.
4. Derive combinations across branches, pruning with constraints.
5. Turn surviving combinations into named executable cases.

## Anti-patterns

- Overlapping classes that double-cover some areas and miss others.
- Trees built once and never updated when the domain changes.
- Combining everything instead of constraining impossible branches.
- Classes so fine-grained the tree becomes unmaintainable.

## Example

Domain: file upload — Classifications: type {image, doc}, size {small, huge}, auth {owner, guest}.

```python
@pytest.mark.parametrize("ftype,size,role", [("image", "small", "owner"), ("doc", "huge", "guest")])
def test_upload_matrix(ftype, size, role):
    assert upload(ftype, size, role).handled
```

## Verification

Tree complete and disjoint, constraints recorded, combinations traceable to branches.

## Pairs-with

combinatorial-testing-t-way, beizer-domain-testing, decision-table-testing, graham-istqb-foundations.
