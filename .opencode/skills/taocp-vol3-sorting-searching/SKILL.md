---
name: taocp-vol3-sorting-searching
description: Applies Knuth's TAOCP Volume 3 to sorting and searching done right: the classic internal sorting methods (insertion, exchange, selection, merging, distribution/radix), external sorting, sequential and binary search, trees, and hashing — with precise complexity comparisons and correctness arguments. Use when the user says 'choose a sorting algorithm', 'which sort', 'binary search', 'external sort', 'radix sort', 'hash function', 'hash table design', 'Knuth sorting', 'sorting versus searching trade-offs', or when data must be ordered or looked up efficiently and correctly.
---

# TAOCP Vol 3: Sorting and Searching

Volume 3 is the definitive treatment of ordering and lookup. This skill turns its tables and analyses into an operational decision procedure for real data.

## Choosing the sort

- Match the method to the data shape: insertion for small nearly-ordered inputs, merge and heap for stable and worst-case-safe paths, quicksort variants for speed on random data, radix for fixed-width numeric keys.
- Stability matters when later passes must preserve an existing order; state the stability requirement before choosing.
- Record the comparison cost, not just the time, when data access is the bottleneck.

## External sorting

- When the data exceeds memory, sort in runs that fit in memory, write them out, then merge with multi-way merging.
- Tune the initial run size and the merge fan-in to minimize passes over the data.
- Account for seek and transfer cost in the design; external sorts are dominated by I/O, not comparison.

## Searching

- Sequential search is fine for small unordered data; binary search needs sorted data and gives logarithmic lookups.
- Trees keep data ordered under insert and delete; balance or self-balancing discipline keeps the depth near optimal.
- Hash tables trade ordering for near-constant average access; pick a good hash for the key distribution and handle collisions with a stated policy.

## Correctness discipline

- Each method has a loop invariant; state it and check it at every step during implementation.
- Test with adversarial inputs: already-sorted, reverse-sorted, all-equal, single-element, and empty.
- Verify the sortedness predicate on the output, not just the time.

## Pairs with
clrs-sorting-and-ordering, clrs-hashing-techniques, clrs-data-structures-mastery, taocp-vol1-fundamental-algorithms, off-by-one-boundary-guard
