---
name: clrs-sorting-and-ordering
description: "Applies the sorting chapters of CLRS (Introduction to Algorithms) to choose and implement the right sort for the job: comparison-based sorts (insertion, merge, heap, quicksort with randomized pivot / 3-way partitioning / introsort guard), the Omega(n lg n) comparison lower bound, linear-time sorts (tallying sort, radix sort, bucket sort) and when their assumptions hold, and stability rules for multi-key ordering. Use when the user says 'which sort to use', 'implement quicksort', 'merge sort', 'heapsort', 'radix sort', 'bucket sort', 'stable sort', 'sorting lower bound', 'sorting a large file', 'custom comparator', 'external sort', or when ordering data correctly and fast matters. Pairs with: clrs-algorithm-mastery, clrs-data-structures-mastery, algorithm-design-manual-war-stories, algorithmic-math-reasoner, off-by-one-boundary-guard."
---

# Sorting and Ordering (CLRS)

The sorting chapters are the decision handbook for ordering data. Every sort is
a trade — time, space, stability, and the assumptions it makes about the input.

## When to use

- Choosing the sort for a given input size and shape.
- Implementing a correct quicksort, heapsort, or merge sort.
- Ordering with stability across multiple keys, or external data.

## The comparison-based core

- **Insertion sort** — small or nearly ordered inputs; quadratic but
  cache-friendly.
- **Merge sort** — guaranteed linearithmic, stable, but needs O(n) extra memory.
- **Heapsort** — in-place, linearithmic, but not stable and cache-unfriendly.
- **Quicksort** — the practical winner in place; worst-case quadratic unless
  guarded.

## The lower bound

- Any comparison-based sort needs Ω(n lg n) comparisons in the worst case. Do
  not look for a comparison sort that beats this — the bound is a fact.

## Quicksort done right

- Randomize the pivot so adversarial input cannot force the quadratic path.
- For heavy duplicate keys, use 3-way partitioning (Dutch national flag).
- Add the introsort guard: switch to heapsort when recursion depth grows too
  deep, so worst-case stays linearithmic.

## Linear-time sorts (when the assumptions hold)

- **Tallying sort** — when keys are small non-negative integers.
- **Radix sort** — run the tallying sort on each digit group, least significant
  first.
- **Bucket sort** — distribute uniform keys into buckets, sort each,
  concatenate.
- These beat the lower bound because they use key structure, not comparisons.

## Stability and multi-key ordering

- A stable sort preserves the relative order of equal elements.
- To order by two keys, sort by the minor key first, then the major key — the
  second stable pass preserves the first ordering.
- Choose merge sort (or a stable library sort) when stability is a contract.

Pairs with: clrs-algorithm-mastery (proof discipline), clrs-data-structures-mastery
(heaps), algorithm-design-manual-war-stories (catalog choice), off-by-one-boundary-guard
(boundary care in partition loops).
