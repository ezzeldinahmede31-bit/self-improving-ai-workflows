---
name: clrs-graph-algorithm-design
description: Applies the CLRS graph algorithm toolkit to design and prove graph-based solutions: breadth-first and depth-first search and their applications, shortest paths (Dijkstra, Bellman-Ford, Floyd-Warshall), minimum spanning trees (Kruskal, Prim), and maximum flow (Ford-Fulkerson, Edmonds-Karp). For each family the skill enforces the proof pattern CLRS uses — correct data-structure choice, invariant, and termination — so a graph answer ships with a rigorous justification, not a guess. Use when the user says 'graph algorithm', 'shortest path', 'Dijkstra', 'Bellman-Ford', 'minimum spanning tree', 'Kruskal', 'Prim', 'max flow', 'BFS', 'DFS', 'topological sort', 'strongly connected components', 'bipartite check', 'network flow', or when a problem reduces to a graph model. Pairs with: clrs-algorithm-mastery, algorithmic-math-reasoner, algorithm-design-manual-war-stories, code-execution-guided-swemaster.
---

# CLRS Graph Algorithm Design

Transfers the CLRS treatment of graphs to engineering problems: model the domain as a graph, pick the correct algorithm for the metric (unweighted path, weighted path, tree, flow), and prove the choice before implementing.

## When to use
- Any problem that reduces to nodes and edges (dependency resolution, routing, scheduling, connectivity).
- Choosing among shortest-path, MST, and flow algorithms for a specific metric.
- Reasoning about traversal orders (BFS layers vs DFS recursion).

## The model-first rule
1. Define nodes, edges, weights, and the direction semantics explicitly.
2. Name the metric being optimized: unweighted hops, weighted distance, total tree weight, or throughput.
3. Match the metric to the algorithm family:
   - Unweighted hops → BFS.
   - Weighted, non-negative edges → Dijkstra with a heap.
   - Negative edges (no negative cycles) → Bellman-Ford.
   - All pairs → Floyd-Warshall.
   - Tree over all vertices with minimum total weight → Kruskal or Prim.
   - Throughput with capacities → Ford-Fulkerson / Edmonds-Karp.

## Proof patterns
- BFS correctness: invariant that frontier distance equals the true shortest hop distance; termination when the queue empties.
- Dijkstra: the selected vertex has its true final distance (cut argument); the heap keeps the frontier sorted.
- Kruskal/Prim: the cut property — a light edge crossing a cut belongs to some MST; union-find implements cycle avoidance.
- Flow: the augmenting-path argument; max-flow equals min-cut; Edmonds-Karp bounds the augmentations by a polynomial factor.

## Verification discipline
- Run the algorithm against a brute-force reference on small random graphs (algorithmic-math-reasoner gate).
- Check edge cases: disconnected graphs, zero/negative weights, self-loops, multi-edges.

## Pairs with
clrs-algorithm-mastery, algorithmic-math-reasoner, algorithm-design-manual-war-stories, code-execution-guided-swemaster.