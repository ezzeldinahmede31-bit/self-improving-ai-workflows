---
name: sedgewick-algorithms
description: Applies Sedgewick & Wayne's Algorithms to the complete standard toolkit taught with working code: fundamentals (union-find, analysis of algorithms), sorting, searching (binary search trees, red-black trees, hash tables), graphs (undirected, directed, MST, shortest paths), strings (tries, substring search, regular expressions, data compression), and the context that connects them. Use when the user says 'union-find', 'red-black tree', 'Kruskal', 'Dijkstra', 'trie', 'substring search', 'regular expression matching', 'Sedgewick', 'Algorithms book', 'standard algorithms library', or when implementing or choosing a standard algorithm from the classic catalog.
---

# Algorithms (Sedgewick & Wayne)

Sedgewick & Wayne is the readable, code-first catalog of the algorithms every programmer must know. This skill turns the catalog into a decision tool.

## Fundamentals

- Union-find is the tool for dynamic connectivity; its weighted quick-union with path compression is near-constant per operation.
- Analyze algorithms with the book's empirical method: instrument, measure, and reason about the curve.
- Every algorithm in the catalog has a stated cost; check it before committing.

## Sorting and searching

- Quicksort, mergesort, and heapsort cover the mainstream; choose by stability, worst case, and memory needs.
- Binary search trees give ordered search with insert; red-black trees keep it balanced.
- Hash tables give fast unordered lookup when order is not needed.

## Graphs and strings

- Depth-first search is the scaffolding for connectivity, cycles, and topological order; BFS for shortest paths in unweighted graphs.
- Prim and Kruskal find MSTs; Dijkstra finds shortest paths in weighted graphs with non-negative edges.
- Tries and substring search handle string keys; regular expressions compile to automata for pattern matching.

## Context and choice

- Match the algorithm to the input size and access pattern; the theoretical best is not always the practical best.
- Keep reference implementations to verify your own against on randomized inputs.
- Prefer the battle-tested library version unless you need a guarantee it lacks.

## Pairs with
clrs-algorithm-mastery, clrs-graph-algorithm-design, clrs-data-structures-mastery, algorithm-design-manual-war-stories, clrs-string-matching
